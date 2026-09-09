from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from typing import Any, Iterable

from .digests import canonical_json_bytes
from .semantic_ir import (
    BundleVariantIR,
    BundleVariantKey,
    CapabilityFactsIR,
    CapabilityKey,
    CompiledSemanticIR,
    EvidenceFingerprint,
    NativeBindingIR,
    OntologyLockFingerprint,
    ProfileReleaseSignature,
    ReviewFingerprint,
    SemanticKey,
    TargetBindingIR,
    native_binding_identity,
)
from .semantic_vocabulary import CAPABILITY_IDS, FORMAL_KINDS, PROFILE_IDS, SEMANTIC_ROLES

EXACT_RESOLVER_CONTRACT = "tfont-exact-semantic-resolver-v1"
PROFILE_RELEASE_FINGERPRINT_ALGORITHM = "tfont-profile-release-signature-jcs-sha256-v1"
RUNTIME_PREREQUISITE_FINGERPRINT_ALGORITHM = "tfont-runtime-prerequisite-jcs-sha256-v1"
EXACT_PLAN_FINGERPRINT_ALGORITHM = "tfont-exact-native-plan-jcs-sha256-v1"
EXACT_RESOLUTION_FINGERPRINT_ALGORITHM = "tfont-exact-resolution-jcs-sha256-v1"

SEMANTIC_RESOLUTION_CATEGORIES = frozenset(
    {
        "invalid_request",
        "unsupported_semantic_mode",
        "unknown_request_vocabulary",
        "invalid_corpus_selection",
        "invalid_prerequisite",
        "missing_prerequisite",
        "stale_prerequisite",
        "ambiguous_prerequisite_variant",
        "parent_unverified",
        "parent_incompatible",
        "dependency_unavailable",
        "ontology_bundle_unavailable",
        "capability_absent",
        "capability_unavailable",
        "semantic_tuple_absent",
        "non_exact_mapping",
        "multiple_exact_bindings",
        "invalid_compiled_ir",
    }
)

_PARENT_STATES = frozenset({"verified-exact", "verified-compatible", "unverified", "incompatible"})
_DEPENDENCY_RESULTS = frozenset({"pass", "fail", "unknown"})
_BUNDLE_STATES = frozenset({"not-required", "verified", "unavailable"})


@dataclass(frozen=True)
class DependencyPrerequisiteResult:
    dependency_id: str
    result: str
    observed_evidence_digest: str | None
    evaluator_rule_version: str


@dataclass(frozen=True)
class RuntimePrerequisiteState:
    variant: BundleVariantKey
    profile_release_fingerprint: str
    observed_parent_manifest_digest: str
    parent_state: str
    dependency_results: tuple[DependencyPrerequisiteResult, ...]
    active_ontology_bundle_digest: str | None
    ontology_bundle_state: str
    source_contract: str


@dataclass(frozen=True)
class SemanticResolveRequest:
    key: SemanticKey
    corpora: tuple[str, ...]
    semantic_mode: str = "exact"


@dataclass(frozen=True)
class SemanticCapabilityView:
    corpus_id: str
    variant: BundleVariantKey
    profile_id: str
    capability_id: str
    state: str
    facts: CapabilityFactsIR
    executable_exact: bool
    prerequisite_fingerprint: str


@dataclass(frozen=True)
class ExactNativePlan:
    resolver_contract: str
    corpus_id: str
    semantic_key: SemanticKey
    reference_kind: str
    query_role: str
    semantic_mode: str
    capability_state: str
    variant: BundleVariantKey
    profile_release_fingerprint: str
    expected_parent_manifest_digest: str
    observed_parent_manifest_digest: str
    parent_state: str
    prerequisite_fingerprint: str
    prerequisite_source_contract: str
    mapping_id: str
    projection_id: str
    assessment: str
    native_execution_binding_identity: str
    native_execution_binding: NativeBindingIR
    native_dependencies: tuple[str, ...]
    mapping_semantic_digest: str
    projection_semantic_digest: str
    mapping_review: ReviewFingerprint
    projection_review: ReviewFingerprint
    ontology_lock: OntologyLockFingerprint
    ontology_bundle_digest: str | None
    mapping_evidence: tuple[EvidenceFingerprint, ...]
    projection_evidence: tuple[EvidenceFingerprint, ...]
    plan_fingerprint: str


@dataclass(frozen=True)
class SemanticResolutionResult:
    resolver_contract: str
    request: SemanticResolveRequest
    plans: tuple[ExactNativePlan, ...]
    comparison_state: str
    losses: tuple[str, ...]
    resolution_fingerprint: str


@dataclass(frozen=True)
class SemanticResolutionProblem:
    category: str
    message: str
    corpus_id: str | None = None
    related_id: str | None = None


class SemanticResolutionError(Exception):
    def __init__(self, problem: SemanticResolutionProblem):
        self.problem = problem
        super().__init__(f"{problem.category}: {problem.message}")


def _fail(category: str, message: str, *, corpus_id: str | None = None, related_id: str | None = None) -> None:
    raise SemanticResolutionError(
        SemanticResolutionProblem(category=category, message=message, corpus_id=corpus_id, related_id=related_id)
    )


def _utf16(value: str) -> bytes:
    return value.encode("utf-16be")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _variant_projection(value: BundleVariantKey) -> dict[str, Any]:
    return {
        "corpus_id": value.corpus_id,
        "authored_profile_id": value.authored_profile_id,
        "profile_version": value.profile_version,
        "expected_parent_manifest_digest": value.expected_parent_manifest_digest,
        "ontology_bundle_digest": value.ontology_bundle_digest,
    }


def _review_projection(value: ReviewFingerprint) -> dict[str, str]:
    return {
        "review_id": value.review_id,
        "status": value.status,
        "reviewed_semantic_digest": value.reviewed_semantic_digest,
    }


def _lock_projection(value: OntologyLockFingerprint) -> dict[str, str]:
    return {
        "lock_id": value.lock_id,
        "ontology_id": value.ontology_id,
        "release": value.release,
        "content_digest": value.content_digest,
        "term_namespace": value.term_namespace,
    }


def _evidence_projection(value: EvidenceFingerprint) -> dict[str, str]:
    return {"evidence_id": value.evidence_id, "content_digest": value.content_digest}


def _semantic_key_projection(value: SemanticKey) -> dict[str, str]:
    return {
        "profile_id": value.profile_id,
        "capability_id": value.capability_id,
        "target": value.target,
        "formal_kind": value.formal_kind,
        "semantic_role": value.semantic_role,
    }


def profile_release_fingerprint(signature: ProfileReleaseSignature) -> str:
    if type(signature) is not ProfileReleaseSignature:
        raise TypeError("signature must be ProfileReleaseSignature")
    payload = {
        "algorithm": PROFILE_RELEASE_FINGERPRINT_ALGORITHM,
        "profile_schema_version": signature.profile_schema_version,
        "profile_catalog_version": signature.profile_catalog_version,
        "dependency_contract_version": signature.dependency_contract_version,
        "mapping_schema_version": signature.mapping_schema_version,
        "minimum_tfont_runtime": signature.minimum_tfont_runtime,
        "profiles": list(signature.profiles),
        "capabilities": list(signature.capabilities),
        "dependency_records": [[key, value] for key, value in signature.dependency_records],
        "mapping_digests": [[key, value] for key, value in signature.mapping_digests],
        "ontology_bundle_digest": signature.ontology_bundle_digest,
        "ontology_locks": [_lock_projection(item) for item in signature.ontology_locks],
        "mapping_semantic_algorithm": signature.mapping_semantic_algorithm,
        "projection_semantic_algorithm": signature.projection_semantic_algorithm,
        "mapping_reviews": [
            [mapping_id, _review_projection(review)] for mapping_id, review in signature.mapping_reviews
        ],
        "projection_reviews": [
            [mapping_id, projection_id, _review_projection(review)]
            for mapping_id, projection_id, review in signature.projection_reviews
        ],
    }
    return _sha256(payload)


def _validate_prerequisite_shape(state: RuntimePrerequisiteState) -> tuple[DependencyPrerequisiteResult, ...]:
    if type(state) is not RuntimePrerequisiteState:
        raise TypeError("prerequisite must be RuntimePrerequisiteState")
    if type(state.variant) is not BundleVariantKey:
        _fail("invalid_prerequisite", "prerequisite variant must be BundleVariantKey")
    if type(state.profile_release_fingerprint) is not str or not state.profile_release_fingerprint:
        _fail("invalid_prerequisite", "profile_release_fingerprint must be a non-empty string", corpus_id=state.variant.corpus_id)
    if type(state.observed_parent_manifest_digest) is not str or not state.observed_parent_manifest_digest:
        _fail("invalid_prerequisite", "observed_parent_manifest_digest must be a non-empty string", corpus_id=state.variant.corpus_id)
    if type(state.parent_state) is not str or state.parent_state not in _PARENT_STATES:
        _fail("invalid_prerequisite", "unknown parent state", corpus_id=state.variant.corpus_id)
    if type(state.ontology_bundle_state) is not str or state.ontology_bundle_state not in _BUNDLE_STATES:
        _fail("invalid_prerequisite", "unknown ontology bundle state", corpus_id=state.variant.corpus_id)
    if type(state.source_contract) is not str or not state.source_contract:
        _fail("invalid_prerequisite", "source_contract must be a non-empty exact string", corpus_id=state.variant.corpus_id)
    if type(state.dependency_results) is not tuple:
        _fail("invalid_prerequisite", "dependency_results must be an exact tuple", corpus_id=state.variant.corpus_id)
    seen: set[str] = set()
    rows: list[DependencyPrerequisiteResult] = []
    for row in state.dependency_results:
        if type(row) is not DependencyPrerequisiteResult:
            _fail("invalid_prerequisite", "dependency result must be DependencyPrerequisiteResult", corpus_id=state.variant.corpus_id)
        if type(row.dependency_id) is not str or not row.dependency_id or row.dependency_id in seen:
            _fail("invalid_prerequisite", "dependency IDs must be non-empty and unique", corpus_id=state.variant.corpus_id, related_id=row.dependency_id if type(row.dependency_id) is str else None)
        seen.add(row.dependency_id)
        if type(row.result) is not str or row.result not in _DEPENDENCY_RESULTS:
            _fail("invalid_prerequisite", "unknown dependency result", corpus_id=state.variant.corpus_id, related_id=row.dependency_id)
        if row.observed_evidence_digest is not None and (type(row.observed_evidence_digest) is not str or not row.observed_evidence_digest):
            _fail("invalid_prerequisite", "observed evidence digest must be null or a non-empty string", corpus_id=state.variant.corpus_id, related_id=row.dependency_id)
        if type(row.evaluator_rule_version) is not str or not row.evaluator_rule_version:
            _fail("invalid_prerequisite", "evaluator_rule_version must be a non-empty string", corpus_id=state.variant.corpus_id, related_id=row.dependency_id)
        rows.append(row)
    rows.sort(key=lambda item: _utf16(item.dependency_id))
    return tuple(rows)


def runtime_prerequisite_fingerprint(state: RuntimePrerequisiteState) -> str:
    rows = _validate_prerequisite_shape(state)
    payload = {
        "algorithm": RUNTIME_PREREQUISITE_FINGERPRINT_ALGORITHM,
        "variant": _variant_projection(state.variant),
        "profile_release_fingerprint": state.profile_release_fingerprint,
        "observed_parent_manifest_digest": state.observed_parent_manifest_digest,
        "parent_state": state.parent_state,
        "dependency_results": [
            {
                "dependency_id": row.dependency_id,
                "result": row.result,
                "observed_evidence_digest": row.observed_evidence_digest,
                "evaluator_rule_version": row.evaluator_rule_version,
            }
            for row in rows
        ],
        "active_ontology_bundle_digest": state.active_ontology_bundle_digest,
        "ontology_bundle_state": state.ontology_bundle_state,
        "source_contract": state.source_contract,
    }
    return _sha256(payload)


def _canonical_request(request: SemanticResolveRequest) -> SemanticResolveRequest:
    if type(request) is not SemanticResolveRequest:
        raise TypeError("request must be SemanticResolveRequest")
    if type(request.key) is not SemanticKey:
        _fail("invalid_request", "request key must be SemanticKey")
    if request.semantic_mode != "exact":
        _fail("unsupported_semantic_mode", "I-006 implements exact semantic mode only")
    if type(request.corpora) not in {tuple, list} or not request.corpora:
        _fail("invalid_corpus_selection", "corpora must be a non-empty tuple/list")
    corpora: list[str] = []
    seen: set[str] = set()
    for corpus in request.corpora:
        if type(corpus) is not str or not corpus or corpus in seen:
            _fail("invalid_corpus_selection", "corpus IDs must be non-empty and duplicate-free", related_id=corpus if type(corpus) is str else None)
        seen.add(corpus)
        corpora.append(corpus)
    key = request.key
    if key.profile_id not in PROFILE_IDS:
        _fail("unknown_request_vocabulary", f"unknown profile: {key.profile_id!r}")
    if key.capability_id not in CAPABILITY_IDS or key.capability_id.split(".", 1)[0] != key.profile_id:
        _fail("unknown_request_vocabulary", f"unknown or cross-profile capability: {key.capability_id!r}")
    if key.formal_kind not in FORMAL_KINDS:
        _fail("unknown_request_vocabulary", f"unknown formal kind: {key.formal_kind!r}")
    if key.semantic_role not in SEMANTIC_ROLES:
        _fail("unknown_request_vocabulary", f"unknown semantic role: {key.semantic_role!r}")
    if type(key.target) is not str or not key.target:
        _fail("invalid_request", "semantic target must be a non-empty exact string")
    corpora.sort(key=_utf16)
    return SemanticResolveRequest(key=key, corpora=tuple(corpora), semantic_mode="exact")


def _build_ir_indexes(ir: CompiledSemanticIR):
    if type(ir) is not CompiledSemanticIR:
        raise TypeError("ir must be CompiledSemanticIR")
    variants: dict[BundleVariantKey, BundleVariantIR] = {}
    for variant in ir.variants:
        if type(variant) is not BundleVariantIR or variant.key in variants:
            _fail("invalid_compiled_ir", "compiled IR contains duplicate or invalid variant keys")
        variants[variant.key] = variant
    semantic: dict[SemanticKey, tuple[TargetBindingIR, ...]] = {}
    for key, bindings in ir.semantic_index:
        if type(key) is not SemanticKey or key in semantic or type(bindings) is not tuple:
            _fail("invalid_compiled_ir", "compiled IR contains duplicate or invalid semantic-index keys")
        semantic[key] = bindings
    capabilities: dict[CapabilityKey, CapabilityFactsIR] = {}
    for key, facts in ir.capability_facts:
        if type(key) is not CapabilityKey or key in capabilities or type(facts) is not CapabilityFactsIR:
            _fail("invalid_compiled_ir", "compiled IR contains duplicate or invalid capability keys")
        capabilities[key] = facts
    return variants, semantic, capabilities


def _materialize_prerequisites(prerequisites: Iterable[RuntimePrerequisiteState]) -> tuple[RuntimePrerequisiteState, ...]:
    try:
        rows = tuple(prerequisites)
    except TypeError as exc:
        raise TypeError("prerequisites must be iterable") from exc
    seen: set[BundleVariantKey] = set()
    for row in rows:
        _validate_prerequisite_shape(row)
        if row.variant in seen:
            _fail("invalid_prerequisite", "duplicate prerequisite record for exact variant", corpus_id=row.variant.corpus_id)
        seen.add(row.variant)
    return rows


def _select_prerequisite(corpus_id: str, rows: tuple[RuntimePrerequisiteState, ...], variants: dict[BundleVariantKey, BundleVariantIR]):
    corpus_rows = tuple(row for row in rows if row.variant.corpus_id == corpus_id)
    if not corpus_rows:
        _fail("missing_prerequisite", "requested corpus has no prerequisite attestation", corpus_id=corpus_id)
    current = tuple(row for row in corpus_rows if row.variant in variants)
    if not current:
        _fail("stale_prerequisite", "all prerequisite variants for corpus are stale", corpus_id=corpus_id)
    fresh: list[RuntimePrerequisiteState] = []
    for row in current:
        expected = profile_release_fingerprint(variants[row.variant].release_signature)
        if row.profile_release_fingerprint == expected:
            fresh.append(row)
    if not fresh:
        _fail("stale_prerequisite", "prerequisite profile-release fingerprint is stale", corpus_id=corpus_id)
    if len(fresh) > 1:
        _fail("ambiguous_prerequisite_variant", "more than one fresh variant is attested for requested corpus", corpus_id=corpus_id)
    return fresh[0], variants[fresh[0].variant]


def _validate_executable_prerequisite(state: RuntimePrerequisiteState, variant: BundleVariantIR) -> None:
    corpus_id = variant.key.corpus_id
    if state.parent_state == "unverified":
        _fail("parent_unverified", "parent identity has not been verified", corpus_id=corpus_id)
    if state.parent_state == "incompatible":
        _fail("parent_incompatible", "parent identity is incompatible", corpus_id=corpus_id)
    if state.parent_state == "verified-exact":
        if state.observed_parent_manifest_digest != variant.key.expected_parent_manifest_digest:
            _fail("stale_prerequisite", "verified-exact parent digest does not match selected variant", corpus_id=corpus_id)
    elif state.parent_state == "verified-compatible":
        if state.observed_parent_manifest_digest == variant.key.expected_parent_manifest_digest:
            _fail("invalid_prerequisite", "verified-compatible parent must differ from exact parent identity", corpus_id=corpus_id)

    expected_ids = {dependency_id for dependency_id, _ in variant.release_signature.dependency_records}
    observed = {row.dependency_id: row for row in _validate_prerequisite_shape(state)}
    if set(observed) != expected_ids:
        _fail("stale_prerequisite", "dependency prerequisite set does not match selected release", corpus_id=corpus_id)
    if any(row.result != "pass" for row in observed.values()):
        _fail("dependency_unavailable", "one or more runtime dependencies are unavailable", corpus_id=corpus_id)

    required_bundle = variant.key.ontology_bundle_digest
    if required_bundle is None:
        if state.ontology_bundle_state != "not-required" or state.active_ontology_bundle_digest is not None:
            _fail("invalid_prerequisite", "variant without ontology bundle requires not-required/None attestation", corpus_id=corpus_id)
    else:
        if state.ontology_bundle_state == "unavailable":
            _fail("ontology_bundle_unavailable", "required ontology bundle is unavailable", corpus_id=corpus_id)
        if state.ontology_bundle_state != "verified" or state.active_ontology_bundle_digest is None:
            _fail("invalid_prerequisite", "required ontology bundle must be explicitly verified", corpus_id=corpus_id)
        if state.active_ontology_bundle_digest != required_bundle:
            _fail("stale_prerequisite", "active ontology bundle digest is stale", corpus_id=corpus_id)


def _native_binding_source_projection(binding: NativeBindingIR) -> dict[str, Any]:
    if type(binding) is not NativeBindingIR:
        raise TypeError("binding must be NativeBindingIR")
    result: dict[str, Any] = {}
    for field in ("component_id", "node_type", "feature", "edge", "direction", "interpretation", "execution_shape"):
        value = getattr(binding, field)
        if value is not None:
            result[field] = value
    if binding.value_present:
        result["value"] = binding.value
    if binding.closed_values is not None:
        result["closed_values"] = list(binding.closed_values)
    if binding.steps is not None:
        result["steps"] = [{"edge": step.edge, "direction": step.direction} for step in binding.steps]
    return result


def _validate_variant_coherence(variant: BundleVariantIR) -> None:
    key = variant.key
    release_key = variant.release_key
    signature = variant.release_signature
    if (
        release_key.corpus_id != key.corpus_id
        or release_key.authored_profile_id != key.authored_profile_id
        or release_key.profile_version != key.profile_version
        or signature.ontology_bundle_digest != key.ontology_bundle_digest
        or variant.mapping_digests != signature.mapping_digests
        or variant.ontology_locks != signature.ontology_locks
        or variant.profile_schema_version != signature.profile_schema_version
        or variant.profile_catalog_version != signature.profile_catalog_version
        or variant.dependency_contract_version != signature.dependency_contract_version
        or variant.mapping_schema_version != signature.mapping_schema_version
        or variant.mapping_semantic_algorithm != signature.mapping_semantic_algorithm
        or variant.projection_semantic_algorithm != signature.projection_semantic_algorithm
    ):
        _fail("invalid_compiled_ir", "selected bundle variant disagrees with its release signature", corpus_id=key.corpus_id)


def _validate_binding_key(binding: TargetBindingIR, key: SemanticKey, variant: BundleVariantIR, corpus_id: str) -> None:
    if type(binding) is not TargetBindingIR:
        _fail("invalid_compiled_ir", "semantic index contains a non-target binding", corpus_id=corpus_id)
    if (
        binding.variant != variant.key
        or binding.corpus_id != corpus_id
        or binding.profile_id != key.profile_id
        or binding.capability_id != key.capability_id
        or binding.target != key.target
        or binding.formal_kind != key.formal_kind
        or binding.semantic_role != key.semantic_role
        or binding.reference_kind != "semantic-pivot"
        or binding.query_role != "semantic-constraint"
    ):
        _fail("invalid_compiled_ir", "semantic index binding disagrees with its key/selected variant", corpus_id=corpus_id, related_id=getattr(binding, "projection_id", None))


def _validate_binding_authority(binding: TargetBindingIR, variant: BundleVariantIR) -> None:
    corpus_id = variant.key.corpus_id
    signature = variant.release_signature
    mapping_rows = tuple(row for row in signature.mapping_digests if row[0] == binding.mapping_id)
    if len(mapping_rows) != 1 or mapping_rows[0][1] != binding.mapping_semantic_digest:
        _fail("invalid_compiled_ir", "binding mapping digest is outside selected release authority", corpus_id=corpus_id, related_id=binding.mapping_id)
    mapping_reviews = tuple(row for row in signature.mapping_reviews if row[0] == binding.mapping_id)
    if len(mapping_reviews) != 1 or mapping_reviews[0][1] != binding.mapping_review:
        _fail("invalid_compiled_ir", "binding mapping review is outside selected release authority", corpus_id=corpus_id, related_id=binding.mapping_id)
    projection_reviews = tuple(
        row for row in signature.projection_reviews if row[0] == binding.mapping_id and row[1] == binding.projection_id
    )
    if len(projection_reviews) != 1 or projection_reviews[0][2] != binding.projection_review:
        _fail("invalid_compiled_ir", "binding projection review is outside selected release authority", corpus_id=corpus_id, related_id=binding.projection_id)
    if binding.ontology_lock not in signature.ontology_locks:
        _fail("invalid_compiled_ir", "binding ontology lock is outside selected release authority", corpus_id=corpus_id, related_id=binding.ontology_lock.lock_id)
    dependency_ids = {dependency_id for dependency_id, _ in signature.dependency_records}
    if any(dependency_id not in dependency_ids for dependency_id in binding.native_dependencies):
        _fail("invalid_compiled_ir", "binding native dependency is outside selected release authority", corpus_id=corpus_id, related_id=binding.projection_id)
    if binding.mapping_review.status != "reviewed" or binding.projection_review.status != "reviewed":
        _fail("invalid_compiled_ir", "exact binding reviews are no longer reviewed", corpus_id=corpus_id, related_id=binding.projection_id)
    if binding.ontology_bundle_digest != variant.key.ontology_bundle_digest:
        _fail("invalid_compiled_ir", "binding ontology bundle digest disagrees with selected variant", corpus_id=corpus_id, related_id=binding.projection_id)
    if binding.ontology_bundle_requirement is not None and binding.ontology_bundle_requirement.bundle_digest != variant.key.ontology_bundle_digest:
        _fail("invalid_compiled_ir", "projection ontology bundle requirement disagrees with selected variant", corpus_id=corpus_id, related_id=binding.projection_id)
    try:
        recomputed = native_binding_identity(_native_binding_source_projection(binding.native_execution_binding))
    except Exception:
        _fail("invalid_compiled_ir", "native execution binding cannot be reconstructed", corpus_id=corpus_id, related_id=binding.projection_id)
    if recomputed != binding.native_execution_binding_identity:
        _fail("invalid_compiled_ir", "native execution binding identity mismatch", corpus_id=corpus_id, related_id=binding.projection_id)


def _plan_projection(plan: ExactNativePlan) -> dict[str, Any]:
    return {
        "algorithm": EXACT_PLAN_FINGERPRINT_ALGORITHM,
        "resolver_contract": plan.resolver_contract,
        "corpus_id": plan.corpus_id,
        "semantic_key": _semantic_key_projection(plan.semantic_key),
        "reference_kind": plan.reference_kind,
        "query_role": plan.query_role,
        "semantic_mode": plan.semantic_mode,
        "capability_state": plan.capability_state,
        "variant": _variant_projection(plan.variant),
        "profile_release_fingerprint": plan.profile_release_fingerprint,
        "expected_parent_manifest_digest": plan.expected_parent_manifest_digest,
        "observed_parent_manifest_digest": plan.observed_parent_manifest_digest,
        "parent_state": plan.parent_state,
        "prerequisite_fingerprint": plan.prerequisite_fingerprint,
        "prerequisite_source_contract": plan.prerequisite_source_contract,
        "mapping_id": plan.mapping_id,
        "projection_id": plan.projection_id,
        "assessment": plan.assessment,
        "native_execution_binding_identity": plan.native_execution_binding_identity,
        "native_dependencies": list(plan.native_dependencies),
        "mapping_semantic_digest": plan.mapping_semantic_digest,
        "projection_semantic_digest": plan.projection_semantic_digest,
        "mapping_review": _review_projection(plan.mapping_review),
        "projection_review": _review_projection(plan.projection_review),
        "ontology_lock": _lock_projection(plan.ontology_lock),
        "ontology_bundle_digest": plan.ontology_bundle_digest,
        "mapping_evidence": [_evidence_projection(item) for item in plan.mapping_evidence],
        "projection_evidence": [_evidence_projection(item) for item in plan.projection_evidence],
    }


def _make_plan(key: SemanticKey, binding: TargetBindingIR, variant: BundleVariantIR, prerequisite: RuntimePrerequisiteState) -> ExactNativePlan:
    prereq_fp = runtime_prerequisite_fingerprint(prerequisite)
    release_fp = profile_release_fingerprint(variant.release_signature)
    plan = ExactNativePlan(
        resolver_contract=EXACT_RESOLVER_CONTRACT,
        corpus_id=binding.corpus_id,
        semantic_key=key,
        reference_kind=binding.reference_kind,
        query_role=binding.query_role,
        semantic_mode="exact",
        capability_state="active",
        variant=variant.key,
        profile_release_fingerprint=release_fp,
        expected_parent_manifest_digest=variant.key.expected_parent_manifest_digest,
        observed_parent_manifest_digest=prerequisite.observed_parent_manifest_digest,
        parent_state=prerequisite.parent_state,
        prerequisite_fingerprint=prereq_fp,
        prerequisite_source_contract=prerequisite.source_contract,
        mapping_id=binding.mapping_id,
        projection_id=binding.projection_id,
        assessment=binding.assessment,
        native_execution_binding_identity=binding.native_execution_binding_identity,
        native_execution_binding=binding.native_execution_binding,
        native_dependencies=binding.native_dependencies,
        mapping_semantic_digest=binding.mapping_semantic_digest,
        projection_semantic_digest=binding.projection_semantic_digest,
        mapping_review=binding.mapping_review,
        projection_review=binding.projection_review,
        ontology_lock=binding.ontology_lock,
        ontology_bundle_digest=binding.ontology_bundle_digest,
        mapping_evidence=binding.mapping_evidence,
        projection_evidence=binding.projection_evidence,
        plan_fingerprint="",
    )
    return replace(plan, plan_fingerprint=_sha256(_plan_projection(plan)))


def _resolution_fingerprint(request: SemanticResolveRequest, plans: tuple[ExactNativePlan, ...]) -> str:
    return _sha256(
        {
            "algorithm": EXACT_RESOLUTION_FINGERPRINT_ALGORITHM,
            "resolver_contract": EXACT_RESOLVER_CONTRACT,
            "request": {
                "key": _semantic_key_projection(request.key),
                "corpora": list(request.corpora),
                "semantic_mode": request.semantic_mode,
            },
            "comparison_state": "exactly-comparable",
            "losses": [],
            "plan_fingerprints": [plan.plan_fingerprint for plan in plans],
        }
    )


def _resolve_one(
    corpus_id: str,
    key: SemanticKey,
    prerequisite: RuntimePrerequisiteState,
    variant: BundleVariantIR,
    semantic_rows: tuple[TargetBindingIR, ...] | None,
    capabilities: dict[CapabilityKey, CapabilityFactsIR],
) -> ExactNativePlan:
    _validate_executable_prerequisite(prerequisite, variant)
    capability_key = CapabilityKey(variant.key, key.profile_id, key.capability_id)
    facts = capabilities.get(capability_key)
    if facts is None or facts.reviewed_native_support == 0:
        _fail("capability_absent", "requested capability is absent", corpus_id=corpus_id, related_id=key.capability_id)
    if semantic_rows is None:
        _fail("semantic_tuple_absent", "requested semantic tuple is absent", corpus_id=corpus_id, related_id=key.target)
    candidates = tuple(row for row in semantic_rows if row.corpus_id == corpus_id and row.variant == variant.key)
    if not candidates:
        _fail("semantic_tuple_absent", "requested semantic tuple is absent for selected corpus variant", corpus_id=corpus_id, related_id=key.target)
    for row in candidates:
        _validate_binding_key(row, key, variant, corpus_id)
    exact = tuple(row for row in candidates if row.assessment == "exact")
    if not exact:
        _fail("non_exact_mapping", "only non-exact mappings exist for requested tuple", corpus_id=corpus_id, related_id=key.target)
    if len(exact) > 1:
        _fail("multiple_exact_bindings", "multiple exact bindings require separately reviewed composition", corpus_id=corpus_id, related_id=key.target)
    _validate_variant_coherence(variant)
    binding = exact[0]
    _validate_binding_authority(binding, variant)
    return _make_plan(key, binding, variant, prerequisite)


def semantic_resolve(
    ir: CompiledSemanticIR,
    request: SemanticResolveRequest,
    prerequisites: Iterable[RuntimePrerequisiteState],
) -> SemanticResolutionResult:
    canonical_request = _canonical_request(request)
    variants, semantic, capabilities = _build_ir_indexes(ir)
    prereq_rows = _materialize_prerequisites(prerequisites)
    plans: list[ExactNativePlan] = []
    semantic_rows = semantic.get(canonical_request.key)
    for corpus_id in canonical_request.corpora:
        prerequisite, variant = _select_prerequisite(corpus_id, prereq_rows, variants)
        plans.append(_resolve_one(corpus_id, canonical_request.key, prerequisite, variant, semantic_rows, capabilities))
    plans.sort(key=lambda item: _utf16(item.corpus_id))
    plan_tuple = tuple(plans)
    result = SemanticResolutionResult(
        resolver_contract=EXACT_RESOLVER_CONTRACT,
        request=canonical_request,
        plans=plan_tuple,
        comparison_state="exactly-comparable",
        losses=(),
        resolution_fingerprint="",
    )
    return replace(result, resolution_fingerprint=_resolution_fingerprint(canonical_request, plan_tuple))


def semantic_capabilities(
    ir: CompiledSemanticIR,
    prerequisites: Iterable[RuntimePrerequisiteState],
    *,
    corpora: Iterable[str] | None = None,
) -> tuple[SemanticCapabilityView, ...]:
    variants, _, capabilities = _build_ir_indexes(ir)
    rows = _materialize_prerequisites(prerequisites)
    if corpora is None:
        selected_corpora = sorted({variant.key.corpus_id for variant in ir.variants}, key=_utf16)
    else:
        try:
            selected_corpora = list(corpora)
        except TypeError as exc:
            raise TypeError("corpora must be iterable") from exc
        if any(type(item) is not str or not item for item in selected_corpora) or len(set(selected_corpora)) != len(selected_corpora):
            _fail("invalid_corpus_selection", "capability corpus selection must contain unique non-empty strings")
        selected_corpora.sort(key=_utf16)

    result: list[SemanticCapabilityView] = []
    for corpus_id in selected_corpora:
        prerequisite, variant = _select_prerequisite(corpus_id, rows, variants)
        prerequisite_fp = runtime_prerequisite_fingerprint(prerequisite)
        executable = True
        try:
            _validate_executable_prerequisite(prerequisite, variant)
        except SemanticResolutionError as exc:
            if exc.problem.category in {
                "parent_unverified",
                "parent_incompatible",
                "dependency_unavailable",
                "ontology_bundle_unavailable",
            }:
                executable = False
            else:
                raise
        for key, facts in sorted(capabilities.items(), key=lambda item: (_utf16(item[0].variant.corpus_id), _utf16(item[0].profile_id), _utf16(item[0].capability_id))):
            if key.variant != variant.key:
                continue
            if facts.reviewed_native_support == 0:
                state = "absent"
            elif executable:
                state = "active"
            else:
                state = "unavailable"
            result.append(
                SemanticCapabilityView(
                    corpus_id=corpus_id,
                    variant=variant.key,
                    profile_id=key.profile_id,
                    capability_id=key.capability_id,
                    state=state,
                    facts=facts,
                    executable_exact=state == "active" and facts.exact > 0,
                    prerequisite_fingerprint=prerequisite_fp,
                )
            )
    result.sort(key=lambda item: (_utf16(item.corpus_id), _utf16(item.profile_id), _utf16(item.capability_id)))
    return tuple(result)
