"""Non-production R-016 approximate-execution policy prototype.

R-016 owns mapping-assessment approximation only. The prototype consumes a
fail-closed upstream execution-prerequisite gate; it does not replace R-003
parent-compatibility checks or R-015 semantic-bundle/bridge validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

LOSS_UNDER = "undercoverage"
LOSS_OVER = "overcoverage"
_VALID_LOSSES = frozenset({LOSS_UNDER, LOSS_OVER})
_VALID_SEMANTIC_MODES = frozenset({"exact", "approximate"})
_VALID_ASSESSMENTS = frozenset(
    {
        "exact",
        "close",
        "broader",
        "narrower",
        "related",
        "ambiguous",
        "native-only",
        "unsupported",
    }
)


@dataclass(frozen=True)
class MappingPolicy:
    mapping_id: str
    assessment: str
    # Fail closed by default. P-003 must set this only after the R-003/R-015
    # execution prerequisites for the selected mapping/bundle are satisfied.
    prerequisites_executable: bool = False
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


def _normalize_loss_input(value: Iterable[str]) -> frozenset[str] | None:
    """Normalize an explicit caller loss set without truthiness/coercion tricks."""

    if type(value) not in {list, tuple, set, frozenset}:
        return None
    if any(type(item) is not str for item in value):
        return None
    normalized = frozenset(value)
    if not normalized.issubset(_VALID_LOSSES):
        return None
    return normalized


def _required_losses(mapping: MappingPolicy) -> frozenset[str] | None:
    """Return a reviewed, directionally consistent executable loss contract.

    `broader`/`narrower` have an assessment-implied direction. An explicit
    reviewed loss contract is optional for those assessments, but if present it
    must agree exactly with that direction. `close` has no implied direction and
    therefore requires an explicit non-empty contract drawn from the closed loss
    vocabulary. Unknown or contradictory contracts fail closed.
    """

    if type(mapping.reviewed_losses) is not frozenset:
        return None
    if any(type(item) is not str for item in mapping.reviewed_losses):
        return None
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


def _informative(
    mapping: MappingPolicy,
    reason: str,
    losses: frozenset[str] = frozenset(),
) -> AtomResult:
    return AtomResult(
        mapping.mapping_id,
        mapping.assessment,
        "informative-only",
        losses,
        "",
        reason,
    )


def _has_native_plan(mapping: MappingPolicy) -> bool:
    return type(mapping.native_plan) is str and bool(mapping.native_plan.strip())


def resolve_atom(
    mapping: MappingPolicy,
    *,
    semantic_mode: str = "exact",
    accepted_losses: Iterable[str] = (),
) -> AtomResult:
    """Evaluate one reviewed mapping after upstream execution gates have run."""

    if type(mapping.prerequisites_executable) is not bool:
        return _informative(mapping, "execution prerequisite gate must be an exact boolean")
    if not mapping.prerequisites_executable:
        return _informative(mapping, "upstream execution prerequisites are not executable")

    if type(mapping.approximation_eligible) is not bool:
        return _informative(mapping, "approximation eligibility must be an exact boolean")

    if mapping.assessment not in _VALID_ASSESSMENTS:
        return _informative(mapping, "unknown mapping assessment")

    if type(semantic_mode) is not str or semantic_mode not in _VALID_SEMANTIC_MODES:
        return _informative(mapping, "unknown semantic mode")

    accepted = _normalize_loss_input(accepted_losses)
    if accepted is None:
        return _informative(mapping, "caller supplied an invalid or unknown loss token")

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

    # Generic caller opt-in is sufficient only when every lossy plan has the
    # same loss shape. Opposite/heterogeneous biases are not a bounded common
    # approximation and remain non-aggregatable in R-016 v1.
    aggregate_allowed = (
        type(allow_approximate_aggregates) is bool
        and allow_approximate_aggregates
        and state == "approximately-comparable"
    )
    return {
        "state": state,
        "aggregate_allowed": aggregate_allowed,
    }
