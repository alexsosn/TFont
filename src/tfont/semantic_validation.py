from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .parent_identity import parent_manifest_digest


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


def validate_semantic_bundle(bundle: SemanticSourceBundle) -> ValidatedSemanticBundle:
    """Return the structurally assembled semantic bundle.

    This first implementation establishes only the public I-004 API. Cross-artifact
    semantic checks are added in subsequent RED/GREEN phases and must fail closed.
    """
    if not isinstance(bundle, SemanticSourceBundle):
        raise TypeError("bundle must be SemanticSourceBundle")

    return ValidatedSemanticBundle(
        bundle=bundle,
        expected_parent_manifest_digest=parent_manifest_digest(bundle.expected_parent_manifest.data),
        mapping_semantic_digests=(),
        indexes=SemanticIndexes(),
    )
