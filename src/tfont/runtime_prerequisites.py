from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Protocol

from .digests import canonical_json_bytes
from .semantic_ir import BundleVariantIR, BundleVariantKey
from .semantic_resolver import (
    DependencyPrerequisiteResult,
    RuntimePrerequisiteState,
    profile_release_fingerprint,
)

RUNTIME_EVALUATION_CONTRACT = "tfont-runtime-evaluation-v1"
OBSERVATION_FINGERPRINT_ALGORITHM = "tfont-runtime-observation-jcs-sha256-v1"
RUNTIME_REPORT_FINGERPRINT_ALGORITHM = "tfont-runtime-report-jcs-sha256-v1"
NATIVE_VALUE_RULE = "tfont-runtime-native-value-present-v1"


class RuntimeObservation(Protocol):
    parent_manifest_digest: str

    def values(
        self,
        component_id: str,
        node_type: str,
        feature: str,
    ) -> tuple[str, tuple[Any, ...]]: ...


@dataclass(frozen=True)
class RuntimeEvaluationReport:
    contract: str
    variant: BundleVariantKey
    profile_release_fingerprint: str
    observed_parent_manifest_digest: str
    compatibility_state: str
    dependency_results: tuple[DependencyPrerequisiteResult, ...]
    active_ontology_bundle_digest: str | None
    ontology_bundle_state: str
    source_contract: str
    report_fingerprint: str

    def to_prerequisite(self) -> RuntimePrerequisiteState:
        return RuntimePrerequisiteState(
            variant=self.variant,
            profile_release_fingerprint=self.profile_release_fingerprint,
            observed_parent_manifest_digest=self.observed_parent_manifest_digest,
            parent_state=self.compatibility_state,
            dependency_results=self.dependency_results,
            active_ontology_bundle_digest=self.active_ontology_bundle_digest,
            ontology_bundle_state=self.ontology_bundle_state,
            source_contract=self.source_contract,
        )


class RuntimeEvaluationError(ValueError):
    pass


def _hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _utf16(value: str) -> bytes:
    return value.encode("utf-16be")


def _scalar_key(value: Any) -> tuple[str, Any]:
    if value is None:
        return ("null", None)
    if type(value) is bool:
        return ("boolean", value)
    if type(value) is int:
        return ("integer", value)
    if type(value) is float:
        if not math.isfinite(value):
            raise RuntimeEvaluationError("non-finite JSON number in observation")
        return ("number", value)
    if type(value) is str:
        return ("string", value)
    raise RuntimeEvaluationError("observation contains a non-JSON scalar")


def _validate_variant(variant: BundleVariantIR) -> None:
    if type(variant) is not BundleVariantIR:
        raise TypeError("variant must be BundleVariantIR")
    key = variant.key
    release_key = variant.release_key
    if (
        release_key.corpus_id != key.corpus_id
        or release_key.authored_profile_id != key.authored_profile_id
        or release_key.profile_version != key.profile_version
    ):
        raise RuntimeEvaluationError("variant release key does not match variant key")
    signature = variant.release_signature
    if signature.ontology_bundle_digest != key.ontology_bundle_digest:
        raise RuntimeEvaluationError("variant ontology bundle identity is incoherent")
    if variant.mapping_digests != signature.mapping_digests:
        raise RuntimeEvaluationError("variant mapping authority is incoherent")
    if variant.ontology_locks != signature.ontology_locks:
        raise RuntimeEvaluationError("variant ontology authority is incoherent")
    profile_release_fingerprint(signature)


def _dependency_records(variant: BundleVariantIR) -> tuple[tuple[str, dict[str, Any]], ...]:
    rows: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    for row in variant.release_signature.dependency_records:
        if type(row) is not tuple or len(row) != 2:
            raise RuntimeEvaluationError("invalid dependency record envelope")
        dependency_id, encoded = row
        if type(dependency_id) is not str or not dependency_id or dependency_id in seen:
            raise RuntimeEvaluationError("dependency IDs must be unique non-empty strings")
        if type(encoded) is not str or not encoded:
            raise RuntimeEvaluationError("dependency record must be canonical JSON text")
        try:
            record = json.loads(encoded)
        except (TypeError, ValueError) as error:
            raise RuntimeEvaluationError("dependency record is invalid JSON") from error
        if type(record) is not dict or record.get("dependency_id") != dependency_id:
            raise RuntimeEvaluationError("dependency record identity mismatch")
        if record.get("kind") != "native-value-present":
            raise RuntimeEvaluationError("dependency kind is not implemented by this GREEN slice")
        if type(record.get("component_id")) is not str or not record["component_id"]:
            raise RuntimeEvaluationError("native-value dependency has invalid component_id")
        assertion = record.get("assertion")
        if type(assertion) is not dict:
            raise RuntimeEvaluationError("native-value dependency has invalid assertion")
        if type(assertion.get("node_type")) is not str or not assertion["node_type"]:
            raise RuntimeEvaluationError("native-value dependency has invalid node_type")
        if type(assertion.get("feature")) is not str or not assertion["feature"]:
            raise RuntimeEvaluationError("native-value dependency has invalid feature")
        if "value" not in assertion:
            raise RuntimeEvaluationError("native-value dependency is missing value")
        _scalar_key(assertion["value"])
        seen.add(dependency_id)
        rows.append((dependency_id, record))
    rows.sort(key=lambda item: _utf16(item[0]))
    return tuple(rows)


def _evaluate_native_value(
    dependency_id: str,
    record: dict[str, Any],
    observation: RuntimeObservation,
) -> DependencyPrerequisiteResult:
    assertion = record["assertion"]
    try:
        state, values = observation.values(
            record["component_id"],
            assertion["node_type"],
            assertion["feature"],
        )
    except Exception:
        state, values = "unknown", ()
    if state == "unknown":
        return DependencyPrerequisiteResult(
            dependency_id=dependency_id,
            result="unknown",
            observed_evidence_digest=None,
            evaluator_rule_version=NATIVE_VALUE_RULE,
        )
    if state != "complete" or type(values) is not tuple:
        return DependencyPrerequisiteResult(
            dependency_id=dependency_id,
            result="unknown",
            observed_evidence_digest=None,
            evaluator_rule_version=NATIVE_VALUE_RULE,
        )
    tagged = tuple(_scalar_key(value) for value in values)
    wanted = _scalar_key(assertion["value"])
    result = "pass" if wanted in tagged else "fail"
    canonical_values = sorted(
        ({"type": kind, "value": value} for kind, value in tagged),
        key=lambda item: canonical_json_bytes(item),
    )
    evidence = {
        "algorithm": OBSERVATION_FINGERPRINT_ALGORITHM,
        "kind": "native-value-present",
        "component_id": record["component_id"],
        "node_type": assertion["node_type"],
        "feature": assertion["feature"],
        "complete": True,
        "values": canonical_values,
    }
    return DependencyPrerequisiteResult(
        dependency_id=dependency_id,
        result=result,
        observed_evidence_digest=_hash(evidence),
        evaluator_rule_version=NATIVE_VALUE_RULE,
    )


def _bundle_state(
    variant: BundleVariantIR,
    active_ontology_bundle_digest: str | None,
) -> tuple[str | None, str]:
    required = variant.key.ontology_bundle_digest
    if required is None:
        if active_ontology_bundle_digest is not None:
            raise RuntimeEvaluationError("active ontology bundle supplied when none is required")
        return None, "not-required"
    if active_ontology_bundle_digest is None:
        return None, "unavailable"
    if type(active_ontology_bundle_digest) is not str or not active_ontology_bundle_digest:
        raise RuntimeEvaluationError("active ontology bundle digest must be non-empty")
    if active_ontology_bundle_digest != required:
        raise RuntimeEvaluationError("active ontology bundle does not match selected release")
    return active_ontology_bundle_digest, "verified"


def _report_projection(report: RuntimeEvaluationReport) -> dict[str, Any]:
    return {
        "algorithm": RUNTIME_REPORT_FINGERPRINT_ALGORITHM,
        "contract": report.contract,
        "variant": {
            "corpus_id": report.variant.corpus_id,
            "authored_profile_id": report.variant.authored_profile_id,
            "profile_version": report.variant.profile_version,
            "expected_parent_manifest_digest": report.variant.expected_parent_manifest_digest,
            "ontology_bundle_digest": report.variant.ontology_bundle_digest,
        },
        "profile_release_fingerprint": report.profile_release_fingerprint,
        "observed_parent_manifest_digest": report.observed_parent_manifest_digest,
        "compatibility_state": report.compatibility_state,
        "dependency_results": [
            {
                "dependency_id": row.dependency_id,
                "result": row.result,
                "observed_evidence_digest": row.observed_evidence_digest,
                "evaluator_rule_version": row.evaluator_rule_version,
            }
            for row in report.dependency_results
        ],
        "active_ontology_bundle_digest": report.active_ontology_bundle_digest,
        "ontology_bundle_state": report.ontology_bundle_state,
        "source_contract": report.source_contract,
    }


def evaluate_runtime_prerequisites(
    variant: BundleVariantIR,
    observation: RuntimeObservation,
    *,
    source_contract: str,
    active_ontology_bundle_digest: str | None = None,
) -> RuntimeEvaluationReport:
    _validate_variant(variant)
    if type(source_contract) is not str or not source_contract:
        raise RuntimeEvaluationError("source_contract must be a non-empty string")
    parent_digest = getattr(observation, "parent_manifest_digest", None)
    if type(parent_digest) is not str or not parent_digest:
        raise RuntimeEvaluationError("observation parent manifest digest must be non-empty")

    results = tuple(
        _evaluate_native_value(dependency_id, record, observation)
        for dependency_id, record in _dependency_records(variant)
    )
    if any(row.result == "fail" for row in results):
        compatibility_state = "incompatible"
    elif any(row.result == "unknown" for row in results):
        compatibility_state = "unverified"
    elif parent_digest == variant.key.expected_parent_manifest_digest:
        compatibility_state = "verified-exact"
    else:
        compatibility_state = "verified-compatible"

    active_digest, bundle_state = _bundle_state(
        variant,
        active_ontology_bundle_digest,
    )
    values = dict(
        contract=RUNTIME_EVALUATION_CONTRACT,
        variant=variant.key,
        profile_release_fingerprint=profile_release_fingerprint(variant.release_signature),
        observed_parent_manifest_digest=parent_digest,
        compatibility_state=compatibility_state,
        dependency_results=results,
        active_ontology_bundle_digest=active_digest,
        ontology_bundle_state=bundle_state,
        source_contract=source_contract,
    )
    provisional = RuntimeEvaluationReport(report_fingerprint="", **values)
    return RuntimeEvaluationReport(
        report_fingerprint=_hash(_report_projection(provisional)),
        **values,
    )
