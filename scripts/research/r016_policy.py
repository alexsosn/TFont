"""Non-production R-016 approximate-execution policy prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

LOSS_UNDER = "undercoverage"
LOSS_OVER = "overcoverage"
_VALID_LOSSES = frozenset({LOSS_UNDER, LOSS_OVER})
_VALID_SEMANTIC_MODES = frozenset({"exact", "approximate"})


@dataclass(frozen=True)
class MappingPolicy:
    mapping_id: str
    assessment: str
    approximation_eligible: bool = False
    reviewed_losses: frozenset[str] = frozenset()
    native_plan: str = ""


@dataclass(frozen=True)
class AtomResult:
    mapping_id: str
    assessment: str
    status: str
    losses: frozenset[str]
    native_plan: str
    reason: str = ""


@dataclass(frozen=True)
class ConjunctionResult:
    status: str
    losses: frozenset[str]
    atoms: tuple[AtomResult, ...]


def _required_losses(mapping: MappingPolicy) -> frozenset[str] | None:
    """Return a reviewed, directionally consistent executable loss contract.

    `broader`/`narrower` have an assessment-implied direction. An explicit
    reviewed loss contract is optional for those assessments, but if present it
    must agree exactly with that direction. `close` has no implied direction and
    therefore requires an explicit non-empty contract drawn from the closed loss
    vocabulary. Unknown or contradictory contracts fail closed.
    """

    reviewed = mapping.reviewed_losses
    if not reviewed.issubset(_VALID_LOSSES):
        return None

    if mapping.assessment == "exact":
        return frozenset() if not reviewed else None

    if mapping.assessment == "broader":
        required = frozenset({LOSS_UNDER})
        return required if not reviewed or reviewed == required else None

    if mapping.assessment == "narrower":
        required = frozenset({LOSS_OVER})
        return required if not reviewed or reviewed == required else None

    if mapping.assessment == "close":
        return reviewed or None

    return None


def _informative(mapping: MappingPolicy, reason: str, losses: frozenset[str] = frozenset()) -> AtomResult:
    return AtomResult(
        mapping.mapping_id,
        mapping.assessment,
        "informative-only",
        losses,
        "",
        reason,
    )


def _has_native_plan(mapping: MappingPolicy) -> bool:
    return isinstance(mapping.native_plan, str) and bool(mapping.native_plan.strip())


def resolve_atom(
    mapping: MappingPolicy,
    *,
    semantic_mode: str = "exact",
    accepted_losses: Iterable[str] = (),
) -> AtomResult:
    accepted = frozenset(accepted_losses)

    if semantic_mode not in _VALID_SEMANTIC_MODES:
        return _informative(mapping, "unknown semantic mode")

    if mapping.assessment == "exact":
        required = _required_losses(mapping)
        if required is None:
            return _informative(mapping, "exact mapping has an inconsistent reviewed loss contract")
        if not _has_native_plan(mapping):
            return _informative(mapping, "mapping has no executable native plan")
        return AtomResult(
            mapping.mapping_id,
            mapping.assessment,
            "executable-exact",
            frozenset(),
            mapping.native_plan,
        )

    if mapping.assessment in {"related", "ambiguous", "native-only", "unsupported"}:
        reason = {
            "related": "related mapping is not a substitute constraint",
            "ambiguous": "mapping target is unresolved",
            "native-only": "mapping has no common semantic reverse target",
            "unsupported": "requested semantics are unsupported",
        }[mapping.assessment]
        return _informative(mapping, reason)

    if semantic_mode != "approximate":
        return _informative(mapping, "non-exact mapping is disabled in exact mode")

    if not mapping.approximation_eligible:
        return _informative(mapping, "mapping has no reviewed approximation authorization")

    required = _required_losses(mapping)
    if required is None:
        return _informative(mapping, "mapping has no valid reviewed executable loss contract")

    if not required.issubset(accepted):
        return _informative(
            mapping,
            "caller did not accept every reviewed semantic loss",
            required,
        )

    if not _has_native_plan(mapping):
        return _informative(mapping, "mapping has no executable native plan", required)

    return AtomResult(
        mapping.mapping_id,
        mapping.assessment,
        "executable-approximate",
        required,
        mapping.native_plan,
    )


def resolve_conjunction(
    mappings: Iterable[MappingPolicy],
    *,
    semantic_mode: str = "exact",
    accepted_losses: Iterable[str] = (),
) -> ConjunctionResult:
    atoms = tuple(
        resolve_atom(m, semantic_mode=semantic_mode, accepted_losses=accepted_losses)
        for m in mappings
    )
    if any(not atom.status.startswith("executable-") for atom in atoms):
        losses = frozenset().union(*(atom.losses for atom in atoms))
        return ConjunctionResult("non-executable", losses, atoms)
    losses = frozenset().union(*(atom.losses for atom in atoms))
    status = "executable-exact" if not losses else "executable-approximate"
    return ConjunctionResult(status, losses, atoms)


def comparison_state(
    plans: Iterable[ConjunctionResult],
    *,
    allow_approximate_aggregates: bool = False,
) -> dict[str, object]:
    plans = tuple(plans)
    if not plans or any(plan.status == "non-executable" for plan in plans):
        return {"state": "partial/non-executable", "aggregate_allowed": False}

    loss_sets = {plan.losses for plan in plans}
    if loss_sets == {frozenset()}:
        return {"state": "exactly-comparable", "aggregate_allowed": True}

    nonempty = {loss for loss in loss_sets if loss}
    state = "approximately-comparable" if len(nonempty) <= 1 else "heterogeneous-loss"
    return {
        "state": state,
        "aggregate_allowed": bool(allow_approximate_aggregates),
    }
