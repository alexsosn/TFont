from __future__ import annotations

from typing import Any, Callable

from .semantic_digest_v2 import projection_semantic_digest_v1

Fail = Callable[[str, str, tuple[str | int, ...], str | None], None]


def check_evidence_bindings(
    bindings: Any,
    *,
    evidences: dict[str, dict[str, Any]],
    path: tuple[str | int, ...],
    fail: Fail,
) -> None:
    if type(bindings) is not list:
        fail("missing_reference", "evidence bindings must be a list", path, None)
    for index, binding in enumerate(bindings):
        item_path = path + (index,)
        if type(binding) is not dict:
            fail("missing_reference", "evidence binding must be an object", item_path, None)
        evidence_id = binding.get("evidence_id")
        if type(evidence_id) is not str or evidence_id not in evidences:
            fail(
                "missing_reference",
                f"missing evidence: {evidence_id!r}",
                item_path + ("evidence_id",),
                evidence_id if type(evidence_id) is str else None,
            )
        if binding.get("content_digest") != evidences[evidence_id].get("content_digest"):
            fail(
                "evidence_digest_mismatch",
                f"evidence digest mismatch: {evidence_id}",
                item_path + ("content_digest",),
                evidence_id,
            )


def validate_child_evidence(
    mappings: tuple[tuple[str, dict[str, Any]], ...],
    *,
    evidences: dict[str, dict[str, Any]],
    fail: Fail,
) -> None:
    for mapping_id, mapping in mappings:
        for index, candidate in enumerate(mapping.get("ambiguous_candidates", [])):
            bindings = candidate.get("evidence", [])
            if bindings:
                check_evidence_bindings(
                    bindings,
                    evidences=evidences,
                    path=("mappings", mapping_id, "ambiguous_candidates", index, "evidence"),
                    fail=fail,
                )
        for index, reference in enumerate(mapping.get("external_references", [])):
            bindings = reference.get("evidence", [])
            if bindings:
                check_evidence_bindings(
                    bindings,
                    evidences=evidences,
                    path=("mappings", mapping_id, "external_references", index, "evidence"),
                    fail=fail,
                )


def validate_projection_reviews(
    mappings: tuple[tuple[str, dict[str, Any]], ...],
    *,
    fail: Fail,
) -> None:
    for mapping_id, mapping in mappings:
        for index, projection in enumerate(mapping.get("projections", [])):
            review = projection.get("review")
            if not review:
                continue
            path = ("mappings", mapping_id, "projections", index)
            computed = projection_semantic_digest_v1(projection)
            stored = projection.get("projection_semantic_digest")
            if stored != computed:
                fail(
                    "semantic_digest_mismatch",
                    f"projection semantic digest is stale: {projection.get('projection_id')}",
                    path + ("projection_semantic_digest",),
                    projection.get("projection_id"),
                )
            if type(review) is not dict or review.get("reviewed_mapping_digest") != computed:
                fail(
                    "review_digest_mismatch",
                    f"projection review does not bind current semantics: {projection.get('projection_id')}",
                    path + ("review", "reviewed_mapping_digest"),
                    projection.get("projection_id"),
                )


def validate_native_semantics(
    mappings: tuple[tuple[str, dict[str, Any]], ...],
    *,
    dependencies: dict[str, dict[str, Any]],
    fail: Fail,
) -> None:
    for mapping_id, mapping in mappings:
        binding = mapping.get("native_binding")
        if type(binding) is not dict:
            continue
        resolved = [
            dependencies[dependency_id]
            for dependency_id in mapping.get("native_dependencies", [])
            if dependency_id in dependencies
        ]

        if "value" in binding and binding.get("value") in {"", None}:
            required = (binding.get("node_type"), binding.get("feature"), binding.get("value"))
            proven = False
            for dependency in resolved:
                assertion = dependency.get("assertion")
                if dependency.get("kind") == "native-value-present" and type(assertion) is dict:
                    actual = (
                        assertion.get("node_type"),
                        assertion.get("feature"),
                        assertion.get("value"),
                    )
                    if actual == required and assertion.get("value_semantics") == "semantic":
                        proven = True
                        break
            if not proven:
                fail(
                    "native_semantics_unproven",
                    "empty/null native value requires matching semantic native-value-present dependency",
                    ("mappings", mapping_id, "native_binding", "value"),
                    mapping_id,
                )

        if "closed_values" in binding:
            values = binding.get("closed_values")
            if type(values) is not list or not values:
                fail(
                    "native_semantics_unproven",
                    "closed_values must be a non-empty reviewed domain claim",
                    ("mappings", mapping_id, "native_binding", "closed_values"),
                    mapping_id,
                )
            required_values = set(values)
            proven = False
            for dependency in resolved:
                assertion = dependency.get("assertion")
                if dependency.get("kind") == "value-domain" and type(assertion) is dict:
                    if (
                        assertion.get("node_type") == binding.get("node_type")
                        and assertion.get("feature") == binding.get("feature")
                        and assertion.get("domain_semantics") == "closed-reviewed"
                        and type(assertion.get("values")) is list
                        and set(assertion.get("values")) == required_values
                        and assertion.get("evidence")
                    ):
                        proven = True
                        break
            if not proven:
                fail(
                    "native_semantics_unproven",
                    "closed domain claim requires matching closed-reviewed value-domain dependency with evidence",
                    ("mappings", mapping_id, "native_binding", "closed_values"),
                    mapping_id,
                )


def validate_child_semantics(
    mappings: tuple[tuple[str, dict[str, Any]], ...],
    *,
    dependencies: dict[str, dict[str, Any]],
    evidences: dict[str, dict[str, Any]],
    fail: Fail,
) -> None:
    """Compatibility composition; the I-004 orchestrator invokes the phases separately."""

    validate_child_evidence(mappings, evidences=evidences, fail=fail)
    validate_projection_reviews(mappings, fail=fail)
    validate_native_semantics(mappings, dependencies=dependencies, fail=fail)
