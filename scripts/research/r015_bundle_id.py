"""Non-production R-015 semantic-bundle identity/reference validator.

This prototype exists only to make the research contract executable. Production
schema/loading belongs to P-003 and later implementation tickets.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


_ONTOLOGY_REF_FIELDS = ("lock_id", "digest")
_BRIDGE_FIELDS = (
    "bridge_id",
    "digest",
    "source_lock_id",
    "source_lock_digest",
    "target_lock_id",
    "target_lock_digest",
    "scope",
    "review_status",
    "reviewed_content_digest",
    "compatibility",
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


def _canonical_item(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _project(item: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {key: item[key] for key in fields if key in item}


def _validate_unique_ids(bundle: dict[str, Any]) -> None:
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


def semantic_projection(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return the semantic, order-independent bundle projection.

    The projection is an allow-list, not a deep copy. Presentation/audit metadata is
    deliberately excluded even when nested inside lock/bridge/edge records.
    """

    _validate_unique_ids(bundle)
    profile_contracts = list(bundle.get("profile_contracts", []))
    if not all(isinstance(item, str) and item for item in profile_contracts):
        raise ValueError("profile_contracts must contain non-empty contract IDs")

    ontology_refs = [
        _project(item, _ONTOLOGY_REF_FIELDS) for item in bundle.get("ontology_locks", [])
    ]
    bridge_refs = [
        _project(item, _BRIDGE_FIELDS) for item in bundle.get("bridge_locks", [])
    ]
    edges = [_project(item, _EDGE_FIELDS) for item in bundle.get("dependency_edges", [])]

    return {
        "schema_version": bundle["schema_version"],
        "profile_contracts": sorted(profile_contracts),
        "ontology_locks": sorted(ontology_refs, key=_canonical_item),
        "bridge_locks": sorted(bridge_refs, key=_canonical_item),
        "dependency_edges": sorted(edges, key=_canonical_item),
    }


def bundle_digest(bundle: dict[str, Any]) -> str:
    payload = _canonical_item(semantic_projection(bundle)).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _locks(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _validate_unique_ids(bundle)
    return {item["lock_id"]: item for item in bundle.get("ontology_locks", [])}


def _bridges(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _validate_unique_ids(bundle)
    return {item["bridge_id"]: item for item in bundle.get("bridge_locks", [])}


def dependency_states(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate active dependency edges without ontology reasoning.

    Each edge is an explicit reviewed TFont dependency requirement. Optional inactive
    edges are diagnostic `inactive`, never failures.
    """

    _validate_unique_ids(bundle)
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

        if satisfied_by.startswith("lock:"):
            lock_id = satisfied_by.removeprefix("lock:")
            if not required_id or lock_id != required_id:
                states.append({"id": edge_id, "state": "dependency-lock-mismatch"})
                continue
            lock = locks.get(lock_id)
            if lock is None:
                states.append({"id": edge_id, "state": "missing-lock"})
                continue
            expected = edge.get("required_lock_digest")
            if not expected:
                states.append({"id": edge_id, "state": "unbound-exact-lock"})
                continue
            if lock.get("digest") != expected:
                states.append({"id": edge_id, "state": "missing-lock"})
                continue
            states.append({"id": edge_id, "state": "satisfied-exact-lock"})
            continue

        if satisfied_by.startswith("bridge:"):
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
            if required_scope is None or bridge_scope is None:
                states.append({"id": edge_id, "state": "unbound-bridge-scope"})
                continue
            if _canonical_item(required_scope) != _canonical_item(bridge_scope):
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
