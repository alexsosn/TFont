from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .parent_identity import parent_manifest_digest
from .semantic_bundle_validation import validate_bundle_source_closure
from .semantic_child_validation import (
    check_evidence_bindings,
    validate_child_evidence,
    validate_native_semantics,
    validate_projection_reviews,
)
from .semantic_digest_v2 import mapping_semantic_digest_v2
from .semantic_policy_validation import validate_mapping_policies
from .semantic_vocabulary import (
    CANDIDATE_ASSESSMENTS,
    CAPABILITY_IDS,
    FORMAL_KINDS,
    NATIVE_STATES,
    PROFILE_IDS,
    PROJECTION_ASSESSMENTS,
    SEMANTIC_ROLES,
    TARGET_ROUTING,
)


@dataclass(frozen=True)
class SemanticArtifact:
    kind: str
    source_name: str
    data: dict[str, Any]


@dataclass(frozen=True)
class SemanticSourceBundle:
    profile: SemanticArtifact
    expected_parent_manifest: SemanticArtifact
    mappings: SemanticArtifact
    ontology_locks: tuple[SemanticArtifact, ...] = ()
    evidences: tuple[SemanticArtifact, ...] = ()
    ontology_bundle: SemanticArtifact | None = None
    bridges: tuple[SemanticArtifact, ...] = ()
    profile_catalog: SemanticArtifact | None = None
    reference_catalog: SemanticArtifact | None = None


@dataclass(frozen=True)
class SemanticValidationProblem:
    category: str
    message: str
    artifact_kind: str
    source_name: str
    path: tuple[str | int, ...] = ()
    related_id: str | None = None


class SemanticValidationError(ValueError):
    def __init__(self, problem: SemanticValidationProblem):
        self.problem = problem
        super().__init__(f"{problem.category}: {problem.message}")


@dataclass(frozen=True)
class SemanticIndexes:
    components: tuple[tuple[str, dict[str, Any]], ...] = ()
    dependencies: tuple[tuple[str, dict[str, Any]], ...] = ()
    mappings: tuple[tuple[str, dict[str, Any]], ...] = ()
    projections: tuple[tuple[str, dict[str, Any]], ...] = ()
    candidates: tuple[tuple[str, dict[str, Any]], ...] = ()
    references: tuple[tuple[str, dict[str, Any]], ...] = ()
    ontology_locks: tuple[tuple[str, dict[str, Any]], ...] = ()
    evidences: tuple[tuple[str, dict[str, Any]], ...] = ()


@dataclass(frozen=True)
class ValidatedSemanticBundle:
    bundle: SemanticSourceBundle
    expected_parent_manifest_digest: str
    mapping_semantic_digests: tuple[tuple[str, str], ...]
    ontology_bundle_digest: str | None
    indexes: SemanticIndexes


def _fail(
    artifact: SemanticArtifact,
    category: str,
    message: str,
    *,
    path: tuple[str | int, ...] = (),
    related_id: str | None = None,
) -> None:
    raise SemanticValidationError(
        SemanticValidationProblem(
            category=category,
            message=message,
            artifact_kind=artifact.kind,
            source_name=artifact.source_name,
            path=path,
            related_id=related_id,
        )
    )


def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16be")


def _sequence(value: Any, *, artifact: SemanticArtifact, path: tuple[str | int, ...]) -> list[Any]:
    if type(value) is not list:
        _fail(artifact, "missing_reference", "expected list", path=path)
    return value


def _index_records(
    records: list[dict[str, Any]],
    id_field: str,
    *,
    artifact: SemanticArtifact,
    path_prefix: tuple[str | int, ...],
) -> tuple[tuple[str, dict[str, Any]], ...]:
    seen: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if type(record) is not dict:
            _fail(artifact, "missing_reference", "record must be an object", path=path_prefix + (index,))
        identifier = record.get(id_field)
        if type(identifier) is not str or not identifier:
            _fail(
                artifact,
                "missing_reference",
                f"{id_field} must be a non-empty string",
                path=path_prefix + (index, id_field),
            )
        if identifier in seen:
            _fail(
                artifact,
                "duplicate_id",
                f"duplicate {id_field}: {identifier}",
                path=path_prefix + (index, id_field),
                related_id=identifier,
            )
        seen[identifier] = record
    return tuple(sorted(seen.items(), key=lambda item: _utf16_key(item[0])))


def _build_indexes(bundle: SemanticSourceBundle) -> SemanticIndexes:
    parent = bundle.expected_parent_manifest
    profile = bundle.profile
    mappings_artifact = bundle.mappings

    components = _index_records(
        _sequence(parent.data.get("components"), artifact=parent, path=("components",)),
        "component_id",
        artifact=parent,
        path_prefix=("components",),
    )
    dependencies = _index_records(
        _sequence(profile.data.get("dependencies"), artifact=profile, path=("dependencies",)),
        "dependency_id",
        artifact=profile,
        path_prefix=("dependencies",),
    )
    mappings = _index_records(
        _sequence(mappings_artifact.data.get("mappings"), artifact=mappings_artifact, path=("mappings",)),
        "mapping_id",
        artifact=mappings_artifact,
        path_prefix=("mappings",),
    )

    projections_raw: list[dict[str, Any]] = []
    candidates_raw: list[dict[str, Any]] = []
    references_raw: list[dict[str, Any]] = []
    for _, mapping in mappings:
        projections_raw.extend(mapping.get("projections", []))
        candidates_raw.extend(mapping.get("ambiguous_candidates", []))
        references_raw.extend(mapping.get("external_references", []))

    projections = (
        _index_records(projections_raw, "projection_id", artifact=mappings_artifact, path_prefix=("projections",))
        if projections_raw else ()
    )
    candidates = (
        _index_records(candidates_raw, "candidate_id", artifact=mappings_artifact, path_prefix=("ambiguous_candidates",))
        if candidates_raw else ()
    )
    references = (
        _index_records(references_raw, "reference_id", artifact=mappings_artifact, path_prefix=("external_references",))
        if references_raw else ()
    )

    lock_records = [artifact.data for artifact in bundle.ontology_locks]
    ontology_locks = (
        _index_records(
            lock_records,
            "lock_id",
            artifact=bundle.ontology_locks[0] if bundle.ontology_locks else SemanticArtifact("ontology-lock", "<none>", {}),
            path_prefix=("ontology_locks",),
        )
        if lock_records else ()
    )

    evidence_records = [artifact.data for artifact in bundle.evidences]
    evidences = (
        _index_records(
            evidence_records,
            "evidence_id",
            artifact=bundle.evidences[0] if bundle.evidences else SemanticArtifact("evidence", "<none>", {}),
            path_prefix=("evidences",),
        )
        if evidence_records else ()
    )

    return SemanticIndexes(
        components=components,
        dependencies=dependencies,
        mappings=mappings,
        projections=projections,
        candidates=candidates,
        references=references,
        ontology_locks=ontology_locks,
        evidences=evidences,
    )


def _require_vocab(
    value: Any,
    allowed: frozenset[str],
    *,
    artifact: SemanticArtifact,
    path: tuple[str | int, ...],
    label: str,
) -> str:
    if type(value) is not str or value not in allowed:
        _fail(artifact, "unknown_vocabulary", f"unknown {label}: {value!r}", path=path)
    return value


def _validate_component_authority(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    profile = bundle.profile
    component_ids = set(dict(indexes.components))
    required = profile.data.get("required_components")
    if type(required) is not list:
        _fail(profile, "component_authority", "required_components must be a list", path=("required_components",))
    required_ids = set(required)
    for index, component_id in enumerate(required):
        if type(component_id) is not str or component_id not in component_ids:
            _fail(
                profile,
                "component_authority",
                f"required component is not present in expected parent: {component_id!r}",
                path=("required_components", index),
                related_id=component_id if type(component_id) is str else None,
            )
    for dependency_id, dependency in indexes.dependencies:
        component_id = dependency.get("component_id")
        if component_id not in required_ids or component_id not in component_ids:
            _fail(
                profile,
                "component_authority",
                f"dependency {dependency_id} uses unauthorized component {component_id!r}",
                path=("dependencies", dependency_id, "component_id"),
                related_id=component_id if type(component_id) is str else None,
            )


def _validate_dependency_closure_and_mapping_scope(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    dependencies = dict(indexes.dependencies)
    for mapping_id, mapping in indexes.mappings:
        dependency_ids = mapping.get("native_dependencies")
        if type(dependency_ids) is not list:
            _fail(artifact, "missing_reference", "native_dependencies must be a list", path=("mappings", mapping_id, "native_dependencies"))
        for index, dependency_id in enumerate(dependency_ids):
            if dependency_id not in dependencies:
                _fail(
                    artifact,
                    "missing_reference",
                    f"missing dependency: {dependency_id!r}",
                    path=("mappings", mapping_id, "native_dependencies", index),
                    related_id=dependency_id if type(dependency_id) is str else None,
                )

        authorized_components = {dependencies[dependency_id].get("component_id") for dependency_id in dependency_ids}
        binding_rows: list[tuple[tuple[str | int, ...], Any]] = [
            (("mappings", mapping_id, "native_binding", "component_id"), mapping.get("native_binding", {}).get("component_id") if type(mapping.get("native_binding")) is dict else None)
        ]
        for projection_index, projection in enumerate(mapping.get("projections", [])):
            execution = projection.get("native_execution_binding")
            binding_rows.append(
                (
                    ("mappings", mapping_id, "projections", projection_index, "native_execution_binding", "component_id"),
                    execution.get("component_id") if type(execution) is dict else None,
                )
            )
        for reference_index, reference in enumerate(mapping.get("external_references", [])):
            native = reference.get("native_binding")
            if native is not None:
                binding_rows.append(
                    (
                        ("mappings", mapping_id, "external_references", reference_index, "native_binding", "component_id"),
                        native.get("component_id") if type(native) is dict else None,
                    )
                )
        for path, component_id in binding_rows:
            if component_id is not None and component_id not in authorized_components:
                _fail(
                    artifact,
                    "component_authority",
                    f"native binding component is not authorized by mapping dependencies: {component_id!r}",
                    path=path,
                    related_id=component_id if type(component_id) is str else None,
                )


def _validate_vocabulary(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    for mapping_id, mapping in indexes.mappings:
        _require_vocab(mapping.get("native_state"), NATIVE_STATES, artifact=artifact, path=("mappings", mapping_id, "native_state"), label="native state")
        for index, profile_id in enumerate(mapping.get("profiles", [])):
            _require_vocab(profile_id, PROFILE_IDS, artifact=artifact, path=("mappings", mapping_id, "profiles", index), label="profile")
        for index, capability_id in enumerate(mapping.get("capabilities", [])):
            _require_vocab(capability_id, CAPABILITY_IDS, artifact=artifact, path=("mappings", mapping_id, "capabilities", index), label="capability")
        for projection_index, projection in enumerate(mapping.get("projections", [])):
            prefix = ("mappings", mapping_id, "projections", projection_index)
            _require_vocab(projection.get("formal_kind"), FORMAL_KINDS, artifact=artifact, path=prefix + ("formal_kind",), label="formal kind")
            _require_vocab(projection.get("semantic_role"), SEMANTIC_ROLES, artifact=artifact, path=prefix + ("semantic_role",), label="semantic role")
            _require_vocab(projection.get("profile_id"), PROFILE_IDS, artifact=artifact, path=prefix + ("profile_id",), label="profile")
            _require_vocab(projection.get("capability_id"), CAPABILITY_IDS, artifact=artifact, path=prefix + ("capability_id",), label="capability")
            _require_vocab(projection.get("assessment"), PROJECTION_ASSESSMENTS, artifact=artifact, path=prefix + ("assessment",), label="projection assessment")
            routing = (projection.get("reference_kind"), projection.get("query_role"))
            if routing not in TARGET_ROUTING:
                _fail(artifact, "invalid_reference_routing", f"invalid target routing pair: {routing!r}", path=prefix, related_id=projection.get("projection_id"))


def _validate_record_states(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    for mapping_id, mapping in indexes.mappings:
        state = mapping.get("native_state")
        projections = mapping.get("projections", [])
        candidates = mapping.get("ambiguous_candidates", [])
        references = mapping.get("external_references", [])
        if state in {"native-only", "unsupported"} and (projections or candidates):
            _fail(artifact, "invalid_record_state", f"{state} record cannot carry target projections or candidates", path=("mappings", mapping_id, "native_state"), related_id=mapping_id)
        if state == "ambiguous" and (projections or not candidates):
            _fail(artifact, "invalid_record_state", "ambiguous record requires candidates and zero approved projections", path=("mappings", mapping_id), related_id=mapping_id)
        if state == "positive":
            if candidates:
                _fail(artifact, "invalid_record_state", "positive record cannot carry unresolved ambiguous candidates", path=("mappings", mapping_id, "ambiguous_candidates"), related_id=mapping_id)
            if not projections and not references:
                _fail(artifact, "invalid_record_state", "positive record requires an approved projection or external reference", path=("mappings", mapping_id), related_id=mapping_id)


def _kind_role_allowed(formal_kind: str, semantic_role: str) -> bool:
    if formal_kind == "class":
        return semantic_role in {"entity-type", "annotation-category", "annotation-value"}
    if formal_kind == "property":
        return semantic_role in {"relation", "attribute", "annotation-category"}
    if formal_kind == "skos-concept":
        return semantic_role in {"annotation-value", "lexical-concept-identity", "authority-reference"}
    if formal_kind == "named-resource":
        return semantic_role in {
            "lexical-entry-identity",
            "lexical-form-identity",
            "lexical-sense-identity",
            "lexical-concept-identity",
            "authority-reference",
            "claim-proposition",
            "inference-activity",
        }
    return False


def _validate_projection_and_candidate_legality(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    candidate_required = {
        "candidate_id",
        "target",
        "reference_kind",
        "query_role",
        "formal_kind",
        "semantic_role",
        "profile_id",
        "capability_id",
        "assessment_candidate",
        "ontology_lock",
        "evidence",
    }
    candidate_forbidden = {
        "native_execution_binding",
        "approximation",
        "publication_relation",
        "review",
        "projection_semantic_digest",
    }
    for mapping_id, mapping in indexes.mappings:
        for projection_index, projection in enumerate(mapping.get("projections", [])):
            prefix = ("mappings", mapping_id, "projections", projection_index)
            if not _kind_role_allowed(projection.get("formal_kind"), projection.get("semantic_role")):
                _fail(artifact, "kind_role_conflict", "formal kind and semantic role are incompatible", path=prefix, related_id=projection.get("projection_id"))
        for candidate_index, candidate in enumerate(mapping.get("ambiguous_candidates", [])):
            prefix = ("mappings", mapping_id, "ambiguous_candidates", candidate_index)
            missing = candidate_required - candidate.keys()
            illegal = candidate_forbidden & candidate.keys()
            if missing or illegal:
                _fail(artifact, "invalid_candidate", f"invalid candidate envelope; missing={sorted(missing)}, forbidden={sorted(illegal)}", path=prefix, related_id=candidate.get("candidate_id"))
            _require_vocab(candidate.get("formal_kind"), FORMAL_KINDS, artifact=artifact, path=prefix + ("formal_kind",), label="formal kind")
            _require_vocab(candidate.get("semantic_role"), SEMANTIC_ROLES, artifact=artifact, path=prefix + ("semantic_role",), label="semantic role")
            _require_vocab(candidate.get("profile_id"), PROFILE_IDS, artifact=artifact, path=prefix + ("profile_id",), label="profile")
            _require_vocab(candidate.get("capability_id"), CAPABILITY_IDS, artifact=artifact, path=prefix + ("capability_id",), label="capability")
            _require_vocab(candidate.get("assessment_candidate"), CANDIDATE_ASSESSMENTS, artifact=artifact, path=prefix + ("assessment_candidate",), label="candidate assessment")
            routing = (candidate.get("reference_kind"), candidate.get("query_role"))
            if routing not in TARGET_ROUTING:
                _fail(artifact, "invalid_reference_routing", f"invalid candidate routing pair: {routing!r}", path=prefix, related_id=candidate.get("candidate_id"))
            if not _kind_role_allowed(candidate.get("formal_kind"), candidate.get("semantic_role")):
                _fail(artifact, "kind_role_conflict", "candidate formal kind and semantic role are incompatible", path=prefix, related_id=candidate.get("candidate_id"))


def _validate_target_locks(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    locks = dict(indexes.ontology_locks)
    for mapping_id, mapping in indexes.mappings:
        rows = [("projections", i, row) for i, row in enumerate(mapping.get("projections", []))]
        rows += [("ambiguous_candidates", i, row) for i, row in enumerate(mapping.get("ambiguous_candidates", []))]
        for collection, index, row in rows:
            prefix = ("mappings", mapping_id, collection, index)
            lock_id = row.get("ontology_lock")
            if type(lock_id) is not str or lock_id not in locks:
                _fail(artifact, "missing_reference", f"missing ontology lock: {lock_id!r}", path=prefix + ("ontology_lock",), related_id=lock_id if type(lock_id) is str else None)
            target = row.get("target")
            if type(target) is not str or target not in locks[lock_id].get("terms_used", []):
                _fail(artifact, "unknown_ontology_target", f"target not present in lock terms_used: {target!r}", path=prefix + ("target",), related_id=target if type(target) is str else None)


def _validate_bundle_source(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> str | None:
    artifact = bundle.ontology_bundle or (bundle.bridges[0] if bundle.bridges else bundle.mappings)

    def fail(category: str, message: str, path: tuple[str | int, ...], related_id: str | None) -> None:
        _fail(artifact, category, message, path=path, related_id=related_id)

    return validate_bundle_source_closure(
        bundle.ontology_bundle.data if bundle.ontology_bundle is not None else None,
        canonical_locks=dict(indexes.ontology_locks),
        bridge_artifacts=tuple(item.data for item in bundle.bridges),
        fail=fail,
    )


def _validate_evidence_bindings(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    evidences = dict(indexes.evidences)

    def fail(category: str, message: str, path: tuple[str | int, ...], related_id: str | None) -> None:
        _fail(artifact, category, message, path=path, related_id=related_id)

    for dependency_id, dependency in indexes.dependencies:
        bindings = dependency.get("evidence")
        if bindings:
            check_evidence_bindings(
                bindings,
                evidences=evidences,
                path=("dependencies", dependency_id, "evidence"),
                fail=fail,
            )

    for mapping_id, mapping in indexes.mappings:
        if mapping.get("evidence"):
            check_evidence_bindings(
                mapping["evidence"],
                evidences=evidences,
                path=("mappings", mapping_id, "evidence"),
                fail=fail,
            )
        for projection_index, projection in enumerate(mapping.get("projections", [])):
            if projection.get("evidence"):
                check_evidence_bindings(
                    projection["evidence"],
                    evidences=evidences,
                    path=("mappings", mapping_id, "projections", projection_index, "evidence"),
                    fail=fail,
                )
            approximation = projection.get("approximation")
            if type(approximation) is dict and approximation.get("evidence"):
                check_evidence_bindings(
                    approximation["evidence"],
                    evidences=evidences,
                    path=("mappings", mapping_id, "projections", projection_index, "approximation", "evidence"),
                    fail=fail,
                )

    validate_child_evidence(indexes.mappings, evidences=evidences, fail=fail)


def _validate_digests_and_reviews(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> tuple[tuple[str, str], ...]:
    artifact = bundle.mappings

    def fail(category: str, message: str, path: tuple[str | int, ...], related_id: str | None) -> None:
        _fail(artifact, category, message, path=path, related_id=related_id)

    validate_projection_reviews(indexes.mappings, fail=fail)

    result: list[tuple[str, str]] = []
    for mapping_id, mapping in indexes.mappings:
        review = mapping.get("review")
        if not review:
            continue
        computed = mapping_semantic_digest_v2(mapping)
        stored = mapping.get("mapping_semantic_digest")
        if stored != computed:
            _fail(
                artifact,
                "semantic_digest_mismatch",
                f"mapping semantic digest is stale: {mapping_id}",
                path=("mappings", mapping_id, "mapping_semantic_digest"),
                related_id=mapping_id,
            )
        if type(review) is not dict or review.get("reviewed_mapping_digest") != computed:
            _fail(
                artifact,
                "review_digest_mismatch",
                f"review does not bind current mapping semantics: {mapping_id}",
                path=("mappings", mapping_id, "review", "reviewed_mapping_digest"),
                related_id=mapping_id,
            )
        result.append((mapping_id, computed))
    return tuple(sorted(result, key=lambda item: _utf16_key(item[0])))


def _validate_native_semantics(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings

    def fail(category: str, message: str, path: tuple[str | int, ...], related_id: str | None) -> None:
        _fail(artifact, category, message, path=path, related_id=related_id)

    validate_native_semantics(indexes.mappings, dependencies=dict(indexes.dependencies), fail=fail)


def _validate_policies(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings

    def fail(category: str, message: str, path: tuple[str | int, ...], related_id: str | None) -> None:
        _fail(artifact, category, message, path=path, related_id=related_id)

    validate_mapping_policies(indexes.mappings, fail=fail)


def validate_semantic_bundle(bundle: SemanticSourceBundle) -> ValidatedSemanticBundle:
    if not isinstance(bundle, SemanticSourceBundle):
        raise TypeError("bundle must be SemanticSourceBundle")

    indexes = _build_indexes(bundle)
    _validate_component_authority(bundle, indexes)
    _validate_dependency_closure_and_mapping_scope(bundle, indexes)
    _validate_vocabulary(bundle, indexes)
    _validate_record_states(bundle, indexes)
    _validate_projection_and_candidate_legality(bundle, indexes)
    _validate_target_locks(bundle, indexes)
    ontology_bundle_digest = _validate_bundle_source(bundle, indexes)
    _validate_evidence_bindings(bundle, indexes)
    mapping_digests = _validate_digests_and_reviews(bundle, indexes)
    _validate_native_semantics(bundle, indexes)
    _validate_policies(bundle, indexes)

    return ValidatedSemanticBundle(
        bundle=bundle,
        expected_parent_manifest_digest=parent_manifest_digest(bundle.expected_parent_manifest.data),
        mapping_semantic_digests=mapping_digests,
        ontology_bundle_digest=ontology_bundle_digest,
        indexes=indexes,
    )
