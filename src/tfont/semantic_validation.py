from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .parent_identity import parent_manifest_digest
from .semantic_vocabulary import (
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


def _index_records(
    records: list[dict[str, Any]],
    id_field: str,
    *,
    artifact: SemanticArtifact,
    path_prefix: tuple[str | int, ...],
) -> tuple[tuple[str, dict[str, Any]], ...]:
    seen: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
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


def _sequence(value: Any, *, artifact: SemanticArtifact, path: tuple[str | int, ...]) -> list[Any]:
    if type(value) is not list:
        _fail(artifact, "missing_reference", "expected list", path=path)
    return value


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

    projections = _index_records(
        projections_raw,
        "projection_id",
        artifact=mappings_artifact,
        path_prefix=("projections",),
    ) if projections_raw else ()
    candidates = _index_records(
        candidates_raw,
        "candidate_id",
        artifact=mappings_artifact,
        path_prefix=("ambiguous_candidates",),
    ) if candidates_raw else ()
    references = _index_records(
        references_raw,
        "reference_id",
        artifact=mappings_artifact,
        path_prefix=("external_references",),
    ) if references_raw else ()

    locks_raw = [artifact.data for artifact in bundle.ontology_locks]
    ontology_locks = _index_records(
        locks_raw,
        "lock_id",
        artifact=bundle.ontology_locks[0] if bundle.ontology_locks else SemanticArtifact("ontology-lock", "<none>", {}),
        path_prefix=("ontology_locks",),
    ) if locks_raw else ()

    evidence_raw = [artifact.data for artifact in bundle.evidences]
    evidences = _index_records(
        evidence_raw,
        "evidence_id",
        artifact=bundle.evidences[0] if bundle.evidences else SemanticArtifact("evidence", "<none>", {}),
        path_prefix=("evidences",),
    ) if evidence_raw else ()

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


def _validate_dependency_closure(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    mappings_artifact = bundle.mappings
    dependency_ids = set(dict(indexes.dependencies))
    for mapping_id, mapping in indexes.mappings:
        dependencies = mapping.get("native_dependencies")
        if type(dependencies) is not list:
            _fail(
                mappings_artifact,
                "missing_reference",
                "native_dependencies must be a list",
                path=("mappings", mapping_id, "native_dependencies"),
            )
        for index, dependency_id in enumerate(dependencies):
            if dependency_id not in dependency_ids:
                _fail(
                    mappings_artifact,
                    "missing_reference",
                    f"missing dependency: {dependency_id!r}",
                    path=("mappings", mapping_id, "native_dependencies", index),
                    related_id=dependency_id if type(dependency_id) is str else None,
                )


def _validate_vocabulary(bundle: SemanticSourceBundle, indexes: SemanticIndexes) -> None:
    artifact = bundle.mappings
    for mapping_id, mapping in indexes.mappings:
        _require_vocab(
            mapping.get("native_state"),
            NATIVE_STATES,
            artifact=artifact,
            path=("mappings", mapping_id, "native_state"),
            label="native state",
        )
        for index, profile_id in enumerate(mapping.get("profiles", [])):
            _require_vocab(
                profile_id,
                PROFILE_IDS,
                artifact=artifact,
                path=("mappings", mapping_id, "profiles", index),
                label="profile",
            )
        for index, capability_id in enumerate(mapping.get("capabilities", [])):
            _require_vocab(
                capability_id,
                CAPABILITY_IDS,
                artifact=artifact,
                path=("mappings", mapping_id, "capabilities", index),
                label="capability",
            )

        for projection_index, projection in enumerate(mapping.get("projections", [])):
            prefix = ("mappings", mapping_id, "projections", projection_index)
            _require_vocab(
                projection.get("formal_kind"),
                FORMAL_KINDS,
                artifact=artifact,
                path=prefix + ("formal_kind",),
                label="formal kind",
            )
            _require_vocab(
                projection.get("semantic_role"),
                SEMANTIC_ROLES,
                artifact=artifact,
                path=prefix + ("semantic_role",),
                label="semantic role",
            )
            _require_vocab(
                projection.get("profile_id"),
                PROFILE_IDS,
                artifact=artifact,
                path=prefix + ("profile_id",),
                label="profile",
            )
            _require_vocab(
                projection.get("capability_id"),
                CAPABILITY_IDS,
                artifact=artifact,
                path=prefix + ("capability_id",),
                label="capability",
            )
            _require_vocab(
                projection.get("assessment"),
                PROJECTION_ASSESSMENTS,
                artifact=artifact,
                path=prefix + ("assessment",),
                label="projection assessment",
            )
            routing = (projection.get("reference_kind"), projection.get("query_role"))
            if routing not in TARGET_ROUTING:
                _fail(
                    artifact,
                    "invalid_reference_routing",
                    f"invalid target routing pair: {routing!r}",
                    path=prefix,
                    related_id=projection.get("projection_id"),
                )


def validate_semantic_bundle(bundle: SemanticSourceBundle) -> ValidatedSemanticBundle:
    if not isinstance(bundle, SemanticSourceBundle):
        raise TypeError("bundle must be SemanticSourceBundle")

    indexes = _build_indexes(bundle)
    _validate_component_authority(bundle, indexes)
    _validate_dependency_closure(bundle, indexes)
    _validate_vocabulary(bundle, indexes)

    return ValidatedSemanticBundle(
        bundle=bundle,
        expected_parent_manifest_digest=parent_manifest_digest(bundle.expected_parent_manifest.data),
        mapping_semantic_digests=(),
        indexes=indexes,
    )
