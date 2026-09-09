from __future__ import annotations

import hashlib
from dataclasses import dataclass
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


class SemanticResolutionError(ValueError):
    def __init__(self, problem: SemanticResolutionProblem):
        self.problem = problem
        super().__init__(f"{problem.category}: {problem.message}")


def _fail(category: str, message: str, *, corpus_id: str | None = None, related_id: str | None = None) -> None:
    raise SemanticResolutionError(
        SemanticResolutionProblem(category, message, corpus_id=corpus_id, related_id=related_id)
    )


def _utf16(value: str) -> bytes:
    return value.encode("utf-16be")


def _hash(projection: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def _variant_projection(value: BundleVariantKey) -> dict[str, Any]:
    return {
        "corpus_id": value.corpus_id,
        "authored_profile_id": value.authored_profile_id,
        "profile_version": value.profile_version,
        "expected_parent_manifest_digest": value.expected_parent_manifest_digest,
        "ontology_bundle_digest": value.ontology_bundle_digest,
    }


def _semantic_key_projection(value: SemanticKey) -> dict[str, Any]:
    return {
        "profile_id": value.profile_id,
        "capability_id": value.capability_id,
        "target": value.target,
        "formal_kind": value.formal_kind,
        "semantic_role": value.semantic_role,
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


def _profile_release_projection(signature: ProfileReleaseSignature) -> dict[str, Any]:
    return {
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
            [mapping_id, _review_projection(review)]
            for mapping_id, review in signature.mapping_reviews
        ],
        "projection_reviews": [
            [mapping_id, projection_id, _review_projection(review)]
            for mapping_id, projection_id, review in signature.projection_reviews
        ],
    }


def profile_release_fingerprint(signature: ProfileReleaseSignature) -> str:
    if type(signature) is not ProfileReleaseSignature:
        raise TypeError("signature must be ProfileReleaseSignature")
    return _hash(_profile_release_projection(signature))


def _validate_dependency_result(value: DependencyPrerequisiteResult) -> None:
    if type(value) is not DependencyPrerequisiteResult:
        raise TypeError("dependency result must be DependencyPrerequisiteResult")
    if not value.dependency_id or type(value.dependency_id) is not str:
        _fail("invalid_prerequisite", "dependency_id must be a non-empty string")
    if value.result not in {"pass", "fail", "unknown"}:
        _fail("invalid_prerequisite", "dependency result is not recognized", related_id=value.dependency_id)
    if type(value.evaluator_rule_version) is not str or not value.evaluator_rule_version:
        _fail("invalid_prerequisite", "evaluator_rule_version must be non-empty", related_id=value.dependency_id)
    if value.observed_evidence_digest is not None and type(value.observed_evidence_digest) is not str:
        _fail("invalid_prerequisite", "observed evidence digest must be a string or null", related_id=value.dependency_id)


def _runtime_projection(state: RuntimePrerequisiteState) -> dict[str, Any]:
    dependencies = sorted(state.dependency_results, key=lambda row: _utf16(row.dependency_id))
    return {
        "algorithm": RUNTIME_PREREQUISITE_FINGERPRINT_ALGORITHM,
        "variant": _variant_projection(state.variant),
        "profile_release_fingerprint": state.profile_release_fingerprint,
        "observed_parent_manifest_digest": state.observed_parent_manifest_digest,
        "parent_state": state.parent_state,
        "dependency_results": [
            {
                "dependency_id": item.dependency_id,
                "result": item.result,
                "observed_evidence_digest": item.observed_evidence_digest,
                "evaluator_rule_version": item.evaluator_rule_version,
            }
            for item in dependencies
        ],
        "active_ontology_bundle_digest": state.active_ontology_bundle_digest,
        "ontology_bundle_state": state.ontology_bundle_state,
        "source_contract": state.source_contract,
    }


def runtime_prerequisite_fingerprint(state: RuntimePrerequisiteState) -> str:
    if type(state) is not RuntimePrerequisiteState:
        raise TypeError("state must be RuntimePrerequisiteState")
    seen: set[str] = set()
    for row in state.dependency_results:
        _validate_dependency_result(row)
        if row.dependency_id in seen:
            _fail("invalid_prerequisite", "duplicate dependency result", related_id=row.dependency_id)
        seen.add(row.dependency_id)
    if type(state.source_contract) is not str or not state.source_contract:
        _fail("invalid_prerequisite", "source_contract must be a non-empty string")
    return _hash(_runtime_projection(state))


def _native_binding_projection(binding: NativeBindingIR) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if binding.component_id is not None:
        result["component_id"] = binding.component_id
    if binding.node_type is not None:
        result["node_type"] = binding.node_type
    if binding.feature is not None:
        result["feature"] = binding.feature
    if binding.value_present:
        result["value"] = binding.value
    if binding.closed_values is not None:
        result["closed_values"] = list(binding.closed_values)
    if binding.edge is not None:
        result["edge"] = binding.edge
    if binding.direction is not None:
        result["direction"] = binding.direction
    if binding.steps is not None:
        result["steps"] = [{"edge": step.edge, "direction": step.direction} for step in binding.steps]
    if binding.interpretation is not None:
        result["interpretation"] = binding.interpretation
    if binding.execution_shape is not None:
        result["execution_shape"] = binding.execution_shape
    return result


def _validate_ir_shape(ir: CompiledSemanticIR) -> tuple[dict[BundleVariantKey, BundleVariantIR], dict[SemanticKey, tuple[TargetBindingIR, ...]], dict[CapabilityKey, CapabilityFactsIR]]:
    if type(ir) is not CompiledSemanticIR:
        raise TypeError("ir must be CompiledSemanticIR")
    variants: dict[BundleVariantKey, BundleVariantIR] = {}
    for variant in ir.variants:
        if variant.key in variants:
            _fail("invalid_compiled_ir", "duplicate variant key", corpus_id=variant.key.corpus_id)
        if (
            variant.release_key.corpus_id != variant.key.corpus_id
            or variant.release_key.authored_profile_id != variant.key.authored_profile_id
            or variant.release_key.profile_version != variant.key.profile_version
        ):
            _fail("invalid_compiled_ir", "variant release key does not match variant key", corpus_id=variant.key.corpus_id)
        if variant.release_signature.ontology_bundle_digest != variant.key.ontology_bundle_digest:
            _fail("invalid_compiled_ir", "variant ontology bundle digest disagrees with release signature", corpus_id=variant.key.corpus_id)
        variants[variant.key] = variant
    semantic: dict[SemanticKey, tuple[TargetBindingIR, ...]] = {}
    for key, rows in ir.semantic_index:
        if key in semantic:
            _fail("invalid_compiled_ir", "duplicate semantic index key")
        semantic[key] = rows
    capabilities: dict[CapabilityKey, CapabilityFactsIR] = {}
    for key, facts in ir.capability_facts:
        if key in capabilities:
            _fail("invalid_compiled_ir", "duplicate capability key", corpus_id=key.variant.corpus_id)
        capabilities[key] = facts
    return variants, semantic, capabilities


def _validate_request(request: SemanticResolveRequest) -> SemanticResolveRequest:
    if type(request) is not SemanticResolveRequest:
        raise TypeError("request must be SemanticResolveRequest")
    if type(request.key) is not SemanticKey:
        _fail("invalid_request", "request key must be SemanticKey")
    if request.semantic_mode != "exact":
        _fail("unsupported_semantic_mode", "only exact semantic resolution is supported")
    if type(request.corpora) is not tuple or not request.corpora:
        _fail("invalid_corpus_selection", "corpora must be a non-empty tuple")
    if any(type(item) is not str or not item for item in request.corpora):
        _fail("invalid_corpus_selection", "corpus IDs must be non-empty strings")
    if len(set(request.corpora)) != len(request.corpora):
        _fail("invalid_corpus_selection", "duplicate corpus selection")
    key = request.key
    if (
        key.profile_id not in PROFILE_IDS
        or key.capability_id not in CAPABILITY_IDS
        or key.formal_kind not in FORMAL_KINDS
        or key.semantic_role not in SEMANTIC_ROLES
        or type(key.target) is not str
        or not key.target
        or not key.capability_id.startswith(key.profile_id + ".")
    ):
        _fail("unknown_request_vocabulary", "request uses unknown or inconsistent semantic vocabulary")
    corpora = tuple(sorted(request.corpora, key=_utf16))
    return SemanticResolveRequest(key=key, corpora=corpora, semantic_mode="exact")


def _materialize_prerequisites(prerequisites: Iterable[RuntimePrerequisiteState]) -> tuple[RuntimePrerequisiteState, ...]:
    try:
        rows = tuple(prerequisites)
    except TypeError:
        raise TypeError("prerequisites must be iterable") from None
    for row in rows:
        if type(row) is not RuntimePrerequisiteState:
            raise TypeError("prerequisite items must be RuntimePrerequisiteState")
    return rows


def _select_prerequisite(
    corpus_id: str,
    rows: tuple[RuntimePrerequisiteState, ...],
    variants: dict[BundleVariantKey, BundleVariantIR],
) -> tuple[RuntimePrerequisiteState, BundleVariantIR]:
    selected = [row for row in rows if row.variant.corpus_id == corpus_id]
    if not selected:
        _fail("missing_prerequisite", "no runtime prerequisite for requested corpus", corpus_id=corpus_id)
    for row in selected:
        variant = variants.get(row.variant)
        if variant is None:
            _fail("stale_prerequisite", "prerequisite variant is not in compiled IR", corpus_id=corpus_id)
        if row.profile_release_fingerprint != profile_release_fingerprint(variant.release_signature):
            _fail("stale_prerequisite", "profile release fingerprint is stale", corpus_id=corpus_id)
    variant_keys = {row.variant for row in selected}
    if len(selected) != len(variant_keys):
        _fail("invalid_prerequisite", "duplicate prerequisite for the same variant", corpus_id=corpus_id)
    if len(variant_keys) != 1:
        _fail("ambiguous_prerequisite_variant", "multiple current variants have prerequisites", corpus_id=corpus_id)
    row = selected[0]
    return row, variants[row.variant]


def _prerequisite_problem(state: RuntimePrerequisiteState, variant: BundleVariantIR) -> str | None:
    if type(state.source_contract) is not str or not state.source_contract:
        return "invalid_prerequisite"
    if state.parent_state not in {"verified-exact", "verified-compatible", "unverified", "incompatible"}:
        return "invalid_prerequisite"
    if state.parent_state == "unverified":
        return "parent_unverified"
    if state.parent_state == "incompatible":
        return "parent_incompatible"
    expected_parent = variant.key.expected_parent_manifest_digest
    if state.parent_state == "verified-exact" and state.observed_parent_manifest_digest != expected_parent:
        return "stale_prerequisite"
    if state.parent_state == "verified-compatible" and state.observed_parent_manifest_digest == expected_parent:
        return "invalid_prerequisite"

    seen: set[str] = set()
    for row in state.dependency_results:
        if type(row) is not DependencyPrerequisiteResult:
            raise TypeError("dependency result must be DependencyPrerequisiteResult")
        if row.dependency_id in seen:
            return "invalid_prerequisite"
        seen.add(row.dependency_id)
        if (
            type(row.dependency_id) is not str
            or not row.dependency_id
            or row.result not in {"pass", "fail", "unknown"}
            or type(row.evaluator_rule_version) is not str
            or not row.evaluator_rule_version
            or (row.observed_evidence_digest is not None and type(row.observed_evidence_digest) is not str)
        ):
            return "invalid_prerequisite"
    expected_dependencies = {dependency_id for dependency_id, _ in variant.release_signature.dependency_records}
    if seen != expected_dependencies:
        return "stale_prerequisite"
    if any(row.result != "pass" for row in state.dependency_results):
        return "dependency_unavailable"

    required_bundle = variant.key.ontology_bundle_digest
    if required_bundle is None:
        if state.ontology_bundle_state != "not-required" or state.active_ontology_bundle_digest is not None:
            return "invalid_prerequisite"
    else:
        if state.ontology_bundle_state == "unavailable":
            return "ontology_bundle_unavailable"
        if state.ontology_bundle_state != "verified":
            return "invalid_prerequisite"
        if state.active_ontology_bundle_digest != required_bundle:
            return "stale_prerequisite"
    return None


def _capability_view(
    variant: BundleVariantIR,
    state: RuntimePrerequisiteState,
    profile_id: str,
    capability_id: str,
    capabilities: dict[CapabilityKey, CapabilityFactsIR],
) -> SemanticCapabilityView:
    key = CapabilityKey(variant.key, profile_id, capability_id)
    facts = capabilities.get(key)
    if facts is None:
        facts = CapabilityFactsIR(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ())
    problem = _prerequisite_problem(state, variant)
    if facts.reviewed_native_support == 0:
        status = "absent"
    elif problem is None:
        status = "active"
    else:
        status = "unavailable"
    return SemanticCapabilityView(
        corpus_id=variant.key.corpus_id,
        variant=variant.key,
        profile_id=profile_id,
        capability_id=capability_id,
        state=status,
        facts=facts,
        executable_exact=status == "active" and facts.exact > 0,
        prerequisite_fingerprint=runtime_prerequisite_fingerprint(state),
    )


def semantic_capabilities(
    ir: CompiledSemanticIR,
    prerequisites: Iterable[RuntimePrerequisiteState],
    *,
    corpora: Iterable[str] | None = None,
) -> tuple[SemanticCapabilityView, ...]:
    variants, _semantic, capabilities = _validate_ir_shape(ir)
    rows = _materialize_prerequisites(prerequisites)
    if corpora is None:
        selected_corpora = sorted({variant.key.corpus_id for variant in ir.variants}, key=_utf16)
    else:
        selected_corpora = list(corpora)
        if any(type(item) is not str or not item for item in selected_corpora) or len(set(selected_corpora)) != len(selected_corpora):
            _fail("invalid_corpus_selection", "invalid capability corpus selection")
        selected_corpora.sort(key=_utf16)
    result: list[SemanticCapabilityView] = []
    for corpus_id in selected_corpora:
        state, variant = _select_prerequisite(corpus_id, rows, variants)
        for profile_id in sorted(variant.release_signature.profiles, key=_utf16):
            for capability_id in sorted(variant.release_signature.capabilities, key=_utf16):
                if capability_id.startswith(profile_id + "."):
                    result.append(_capability_view(variant, state, profile_id, capability_id, capabilities))
    return tuple(result)


def _validate_binding_against_release(binding: TargetBindingIR, variant: BundleVariantIR, request_key: SemanticKey) -> None:
    if (
        binding.variant != variant.key
        or binding.corpus_id != variant.key.corpus_id
        or binding.profile_id != request_key.profile_id
        or binding.capability_id != request_key.capability_id
        or binding.target != request_key.target
        or binding.formal_kind != request_key.formal_kind
        or binding.semantic_role != request_key.semantic_role
        or binding.reference_kind != "semantic-pivot"
        or binding.query_role != "semantic-constraint"
    ):
        _fail("invalid_compiled_ir", "semantic index binding is incoherent", corpus_id=variant.key.corpus_id, related_id=binding.mapping_id)
    mapping_digests = dict(variant.release_signature.mapping_digests)
    if mapping_digests.get(binding.mapping_id) != binding.mapping_semantic_digest:
        _fail("invalid_compiled_ir", "mapping digest is not part of selected release", corpus_id=binding.corpus_id, related_id=binding.mapping_id)
    mapping_reviews = dict(variant.release_signature.mapping_reviews)
    if mapping_reviews.get(binding.mapping_id) != binding.mapping_review or binding.mapping_review.status != "reviewed":
        _fail("invalid_compiled_ir", "mapping review is not selected release authority", corpus_id=binding.corpus_id, related_id=binding.mapping_id)
    projection_reviews = {
        (mapping_id, projection_id): review
        for mapping_id, projection_id, review in variant.release_signature.projection_reviews
    }
    if projection_reviews.get((binding.mapping_id, binding.projection_id)) != binding.projection_review or binding.projection_review.status != "reviewed":
        _fail("invalid_compiled_ir", "projection review is not selected release authority", corpus_id=binding.corpus_id, related_id=binding.projection_id)
    if binding.ontology_lock not in variant.release_signature.ontology_locks:
        _fail("invalid_compiled_ir", "ontology lock is not part of selected release", corpus_id=binding.corpus_id, related_id=binding.ontology_lock.lock_id)
    release_dependencies = {dependency_id for dependency_id, _ in variant.release_signature.dependency_records}
    if any(dependency_id not in release_dependencies for dependency_id in binding.native_dependencies):
        _fail("invalid_compiled_ir", "native dependency is not part of selected release", corpus_id=binding.corpus_id, related_id=binding.mapping_id)
    if binding.ontology_bundle_digest != variant.key.ontology_bundle_digest:
        _fail("invalid_compiled_ir", "binding ontology bundle digest disagrees with variant", corpus_id=binding.corpus_id, related_id=binding.projection_id)
    if binding.ontology_bundle_requirement is not None and binding.ontology_bundle_requirement.bundle_digest != variant.key.ontology_bundle_digest:
        _fail("invalid_compiled_ir", "projection bundle requirement disagrees with variant", corpus_id=binding.corpus_id, related_id=binding.projection_id)
    if native_binding_identity(_native_binding_projection(binding.native_execution_binding)) != binding.native_execution_binding_identity:
        _fail("invalid_compiled_ir", "native execution binding identity mismatch", corpus_id=binding.corpus_id, related_id=binding.projection_id)


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


def _make_plan(binding: TargetBindingIR, variant: BundleVariantIR, state: RuntimePrerequisiteState, semantic_key: SemanticKey) -> ExactNativePlan:
    prerequisite_fingerprint = runtime_prerequisite_fingerprint(state)
    values = dict(
        resolver_contract=EXACT_RESOLVER_CONTRACT,
        corpus_id=binding.corpus_id,
        semantic_key=semantic_key,
        reference_kind="semantic-pivot",
        query_role="semantic-constraint",
        semantic_mode="exact",
        capability_state="active",
        variant=variant.key,
        profile_release_fingerprint=state.profile_release_fingerprint,
        expected_parent_manifest_digest=variant.key.expected_parent_manifest_digest,
        observed_parent_manifest_digest=state.observed_parent_manifest_digest,
        parent_state=state.parent_state,
        prerequisite_fingerprint=prerequisite_fingerprint,
        prerequisite_source_contract=state.source_contract,
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
    )
    provisional = ExactNativePlan(plan_fingerprint="", **values)
    return ExactNativePlan(plan_fingerprint=_hash(_plan_projection(provisional)), **values)


def semantic_resolve(
    ir: CompiledSemanticIR,
    request: SemanticResolveRequest,
    prerequisites: Iterable[RuntimePrerequisiteState],
) -> SemanticResolutionResult:
    variants, semantic_index, capabilities = _validate_ir_shape(ir)
    canonical_request = _validate_request(request)
    prerequisite_rows = _materialize_prerequisites(prerequisites)
    plans: list[ExactNativePlan] = []
    bindings_for_key = semantic_index.get(canonical_request.key)

    for corpus_id in canonical_request.corpora:
        state, variant = _select_prerequisite(corpus_id, prerequisite_rows, variants)
        problem = _prerequisite_problem(state, variant)
        if problem is not None:
            _fail(problem, "runtime prerequisite is not executable", corpus_id=corpus_id)

        capability = _capability_view(
            variant,
            state,
            canonical_request.key.profile_id,
            canonical_request.key.capability_id,
            capabilities,
        )
        if capability.state == "absent":
            _fail("capability_absent", "requested capability is absent", corpus_id=corpus_id)
        if capability.state != "active":
            _fail("capability_unavailable", "requested capability is unavailable", corpus_id=corpus_id)

        if bindings_for_key is None:
            _fail("semantic_tuple_absent", "semantic tuple is absent", corpus_id=corpus_id)
        candidates = [
            row
            for row in bindings_for_key
            if row.corpus_id == corpus_id and row.variant == variant.key
        ]
        if not candidates:
            _fail("semantic_tuple_absent", "semantic tuple is absent for selected corpus variant", corpus_id=corpus_id)
        for candidate in candidates:
            _validate_binding_against_release(candidate, variant, canonical_request.key)
        exact = [row for row in candidates if row.assessment == "exact"]
        if not exact:
            _fail("non_exact_mapping", "semantic tuple has no exact mapping", corpus_id=corpus_id)
        if len(exact) > 1:
            _fail("multiple_exact_bindings", "multiple exact bindings require explicit composition semantics", corpus_id=corpus_id)
        plans.append(_make_plan(exact[0], variant, state, canonical_request.key))

    plans.sort(key=lambda plan: _utf16(plan.corpus_id))
    plan_tuple = tuple(plans)
    result_projection = {
        "algorithm": EXACT_RESOLUTION_FINGERPRINT_ALGORITHM,
        "resolver_contract": EXACT_RESOLVER_CONTRACT,
        "request": {
            "key": _semantic_key_projection(canonical_request.key),
            "corpora": list(canonical_request.corpora),
            "semantic_mode": canonical_request.semantic_mode,
        },
        "comparison_state": "exactly-comparable",
        "losses": [],
        "plan_fingerprints": [plan.plan_fingerprint for plan in plan_tuple],
    }
    return SemanticResolutionResult(
        resolver_contract=EXACT_RESOLVER_CONTRACT,
        request=canonical_request,
        plans=plan_tuple,
        comparison_state="exactly-comparable",
        losses=(),
        resolution_fingerprint=_hash(result_projection),
    )
