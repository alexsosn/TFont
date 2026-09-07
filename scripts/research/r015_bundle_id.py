"""Non-production R-015 semantic-bundle identity/reference validator.

This prototype exists only to make the research contract executable. Production
schema/loading belongs to P-003 and later implementation tickets.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any

from tfont.digests import canonical_json_bytes


_ONTOLOGY_REF_FIELDS = ("lock_id", "digest")
_BRIDGE_CONTENT_FIELDS = (
    "source_lock_id",
    "source_lock_digest",
    "target_lock_id",
    "target_lock_digest",
    "assertion_kind",
    "scope",
    "compatibility",
    "evidence_id",
    "evidence_digest",
    "runtime_strength",
    "runtime_limitations",
)
_BRIDGE_FIELDS = (
    "bridge_id",
    "digest",
    *_BRIDGE_CONTENT_FIELDS,
    "review_status",
    "reviewed_content_digest",
    "review_id",
    "reviewer_id",
    "reviewed_at",
)
_EDGE_FIELDS = (
    "id",
    "consumer",
    "requires",
    "satisfied_by",
    "active",
    "required_lock_digest",
    "required_bridge_scope",
)
_REQUIRED_SCOPE_FIELDS = ("source_term", "target_term", "relation")
_REQUIRED_BRIDGE_ENDPOINT_FIELDS = (
    "source_lock_id",
    "source_lock_digest",
    "target_lock_id",
    "target_lock_digest",
)
_REQUIRED_BRIDGE_STRING_FIELDS = (
    "evidence_id",
    "evidence_digest",
    "review_id",
    "reviewer_id",
    "reviewed_at",
    "runtime_strength",
)
_RUNTIME_STRENGTHS = {"exact", "approximate", "related", "composition-only"}
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _canonical_bytes(value: Any) -> bytes:
    """Reuse the accepted I-002 RFC 8785/JCS byte contract."""

    return canonical_json_bytes(value)


def _sha256_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _project(item: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {key: item[key] for key in fields if key in item}


def _validate_digest(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be sha256:<64 lowercase hex digits>")
    return value


def bridge_content_digest(bridge: dict[str, Any]) -> str:
    """Digest semantic bridge content with the accepted I-002 JCS contract."""

    return _sha256_digest(_canonical_bytes(_project(bridge, _BRIDGE_CONTENT_FIELDS)))


def _validate_scope(scope: Any, *, label: str) -> None:
    if not isinstance(scope, dict) or not scope:
        raise ValueError(f"{label} must be a non-empty object")
    for key in _REQUIRED_SCOPE_FIELDS:
        value = scope.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} missing non-empty {key}")


def _validate_reviewed_at(value: Any, *, bridge_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"bridge {bridge_id} missing reviewed_at")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"bridge {bridge_id} reviewed_at must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"bridge {bridge_id} reviewed_at must include timezone")


def _validate_unique_ids(bundle: dict[str, Any]) -> None:
    profile_contracts = bundle.get("profile_contracts", [])
    if not all(isinstance(item, str) and item for item in profile_contracts):
        raise ValueError("profile_contracts must contain non-empty contract IDs")
    if len(profile_contracts) != len(set(profile_contracts)):
        raise ValueError("duplicate profile contract ID")

    for collection, id_key in (
        ("ontology_locks", "lock_id"),
        ("bridge_locks", "bridge_id"),
        ("dependency_edges", "id"),
    ):
        seen: set[str] = set()
        for item in bundle.get(collection, []):
            item_id = item.get(id_key)
            if not item_id:
                raise ValueError(f"{collection} item missing required {id_key}")
            if item_id in seen:
                raise ValueError(f"duplicate {id_key}: {item_id}")
            seen.add(item_id)


def _active_bridge_ids(bundle: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for edge in bundle.get("dependency_edges", []):
        if not edge.get("active", True):
            continue
        satisfied_by = edge.get("satisfied_by", "")
        if isinstance(satisfied_by, str) and satisfied_by.startswith("bridge:"):
            bridge_id = satisfied_by.removeprefix("bridge:")
            if bridge_id:
                result.add(bridge_id)
    return result


def _validate_bridge_provenance(bridge: dict[str, Any], *, bridge_id: str) -> None:
    for key in _REQUIRED_BRIDGE_STRING_FIELDS:
        value = bridge.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"bridge {bridge_id} missing {key}")

    _validate_digest(bridge["evidence_digest"], label=f"bridge {bridge_id} evidence_digest")
    _validate_reviewed_at(bridge.get("reviewed_at"), bridge_id=bridge_id)

    strength = bridge["runtime_strength"]
    if strength not in _RUNTIME_STRENGTHS:
        raise ValueError(f"bridge {bridge_id} unknown runtime_strength: {strength}")

    limitations = bridge.get("runtime_limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(isinstance(item, str) and item.strip() for item in limitations)
    ):
        raise ValueError(f"bridge {bridge_id} runtime_limitations must be non-empty strings")


def _validate_content_identity(bundle: dict[str, Any]) -> None:
    for lock in bundle.get("ontology_locks", []):
        lock_id = lock.get("lock_id", "<unknown>")
        _validate_digest(lock.get("digest"), label=f"ontology lock {lock_id} digest")

    active_bridge_ids = _active_bridge_ids(bundle)
    for bridge in bundle.get("bridge_locks", []):
        bridge_id = bridge.get("bridge_id", "<unknown>")
        if bridge_id not in active_bridge_ids:
            raise ValueError(f"bridge {bridge_id} is not referenced by an active dependency")
        for key in _REQUIRED_BRIDGE_ENDPOINT_FIELDS:
            if not bridge.get(key):
                raise ValueError(f"bridge {bridge_id} missing {key}")
        _validate_digest(
            bridge["source_lock_digest"],
            label=f"bridge {bridge_id} source_lock_digest",
        )
        _validate_digest(
            bridge["target_lock_digest"],
            label=f"bridge {bridge_id} target_lock_digest",
        )
        _validate_scope(bridge.get("scope"), label=f"bridge {bridge_id} scope")
        _validate_bridge_provenance(bridge, bridge_id=bridge_id)
        digest = _validate_digest(bridge.get("digest"), label=f"bridge {bridge_id} digest")
        reviewed_digest = _validate_digest(
            bridge.get("reviewed_content_digest"),
            label=f"bridge {bridge_id} reviewed_content_digest",
        )
        expected = bridge_content_digest(bridge)
        if digest != expected:
            raise ValueError(f"bridge {bridge_id} content digest mismatch")
        if bridge.get("review_status") == "reviewed" and reviewed_digest != digest:
            # Keep this as an operational state in dependency_states; validation only
            # guarantees that both values use the canonical digest representation.
            pass

    for edge in bundle.get("dependency_edges", []):
        if not edge.get("active", True):
            continue
        satisfied_by = edge.get("satisfied_by", "")
        if isinstance(satisfied_by, str) and satisfied_by.startswith("bridge:"):
            _validate_scope(
                edge.get("required_bridge_scope"),
                label=f"dependency {edge.get('id', '<unknown>')} required_bridge_scope",
            )
        elif isinstance(satisfied_by, str) and satisfied_by.startswith("lock:"):
            _validate_digest(
                edge.get("required_lock_digest"),
                label=f"dependency {edge.get('id', '<unknown>')} required_lock_digest",
            )


def _validate_bundle(bundle: dict[str, Any]) -> None:
    _validate_unique_ids(bundle)
    _validate_content_identity(bundle)


def semantic_projection(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return the semantic, order-independent active bundle projection.

    The projection is an allow-list. Presentation-only metadata is excluded even when
    nested inside records. Review identity/date are operationally identity-bearing.
    Inactive dependency edges remain diagnostic input but are not bundle identity.
    """

    _validate_bundle(bundle)
    profile_contracts = list(bundle.get("profile_contracts", []))

    ontology_refs = [
        _project(item, _ONTOLOGY_REF_FIELDS) for item in bundle.get("ontology_locks", [])
    ]
    bridge_refs = [
        _project(item, _BRIDGE_FIELDS) for item in bundle.get("bridge_locks", [])
    ]
    active_edges = [
        _project(item, _EDGE_FIELDS)
        for item in bundle.get("dependency_edges", [])
        if item.get("active", True)
    ]

    return {
        "schema_version": bundle["schema_version"],
        "profile_contracts": sorted(profile_contracts),
        "ontology_locks": sorted(ontology_refs, key=_canonical_bytes),
        "bridge_locks": sorted(bridge_refs, key=_canonical_bytes),
        "dependency_edges": sorted(active_edges, key=_canonical_bytes),
    }


def bundle_digest(bundle: dict[str, Any]) -> str:
    return _sha256_digest(_canonical_bytes(semantic_projection(bundle)))


def _locks(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _validate_bundle(bundle)
    return {item["lock_id"]: item for item in bundle.get("ontology_locks", [])}


def _bridges(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _validate_bundle(bundle)
    return {item["bridge_id"]: item for item in bundle.get("bridge_locks", [])}


def dependency_states(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate active dependency edges without ontology reasoning.

    This reference validator models the exact-execution gate only. R-016 owns any
    later mode-aware authorization for approximate/related bridge strengths.
    """

    _validate_bundle(bundle)
    locks = _locks(bundle)
    bridges = _bridges(bundle)
    states: list[dict[str, str]] = []

    for edge in bundle.get("dependency_edges", []):
        edge_id = edge["id"]
        if not edge.get("active", True):
            states.append({"id": edge_id, "state": "inactive"})
            continue

        consumer_id = edge.get("consumer")
        if not consumer_id or consumer_id not in locks:
            states.append({"id": edge_id, "state": "missing-consumer-lock"})
            continue

        required_id = edge.get("requires")
        satisfied_by = edge.get("satisfied_by", "")

        if isinstance(satisfied_by, str) and satisfied_by.startswith("lock:"):
            lock_id = satisfied_by.removeprefix("lock:")
            if not required_id or lock_id != required_id:
                states.append({"id": edge_id, "state": "dependency-lock-mismatch"})
                continue
            lock = locks.get(lock_id)
            if lock is None:
                states.append({"id": edge_id, "state": "missing-lock"})
                continue
            expected = edge.get("required_lock_digest")
            if lock.get("digest") != expected:
                states.append({"id": edge_id, "state": "missing-lock"})
                continue
            states.append({"id": edge_id, "state": "satisfied-exact-lock"})
            continue

        if isinstance(satisfied_by, str) and satisfied_by.startswith("bridge:"):
            bridge_id = satisfied_by.removeprefix("bridge:")
            bridge = bridges.get(bridge_id)
            if bridge is None:
                states.append({"id": edge_id, "state": "missing-bridge"})
                continue

            if not required_id or bridge.get("source_lock_id") != required_id:
                states.append({"id": edge_id, "state": "bridge-requires-mismatch"})
                continue

            required_scope = edge.get("required_bridge_scope")
            bridge_scope = bridge.get("scope")
            if _canonical_bytes(required_scope) != _canonical_bytes(bridge_scope):
                states.append({"id": edge_id, "state": "bridge-scope-mismatch"})
                continue

            source = locks.get(bridge.get("source_lock_id"))
            target = locks.get(bridge.get("target_lock_id"))
            if source is None or target is None:
                states.append({"id": edge_id, "state": "missing-lock"})
                continue
            if (
                source.get("digest") != bridge.get("source_lock_digest")
                or target.get("digest") != bridge.get("target_lock_digest")
            ):
                states.append({"id": edge_id, "state": "stale-bridge"})
                continue
            if bridge.get("review_status") != "reviewed":
                states.append({"id": edge_id, "state": "unreviewed-bridge"})
                continue
            if bridge.get("reviewed_content_digest") != bridge.get("digest"):
                states.append({"id": edge_id, "state": "unreviewed-bridge"})
                continue

            compatibility = bridge.get("compatibility")
            if compatibility == "incompatible":
                states.append({"id": edge_id, "state": "incompatible-bridge"})
                continue
            if compatibility != "compatible":
                states.append({"id": edge_id, "state": "unknown-bridge-compatibility"})
                continue

            if bridge.get("runtime_strength") != "exact":
                states.append({"id": edge_id, "state": "non-exact-bridge-strength"})
                continue

            states.append({"id": edge_id, "state": "satisfied-reviewed-bridge"})
            continue

        states.append({"id": edge_id, "state": "missing-bridge"})

    return states


def executable(bundle: dict[str, Any]) -> bool:
    allowed = {"inactive", "satisfied-exact-lock", "satisfied-reviewed-bridge"}
    try:
        return all(item["state"] in allowed for item in dependency_states(bundle))
    except (KeyError, TypeError, ValueError):
        return False


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    data = json.loads(args.bundle.read_text(encoding="utf-8"))
    try:
        print(bundle_digest(data))
        print(json.dumps(dependency_states(data), indent=2, sort_keys=True))
    except (KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True))
        raise SystemExit(1) from exc
    raise SystemExit(0 if executable(data) else 1)
