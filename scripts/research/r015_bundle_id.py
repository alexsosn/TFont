"""Non-production R-015 semantic-bundle identity/reference validator.

This prototype exists only to make the research contract executable. Production
schema/loading belongs to P-003 and later implementation tickets.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


_SET_LIKE_LISTS = {
    "profile_contracts",
    "ontology_locks",
    "bridge_locks",
    "dependency_edges",
}


def _canonical_item(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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

    Unknown presentation/audit keys are deliberately excluded. P-003 owns the final
    schema; this research prototype proves the identity properties only.
    """

    _validate_unique_ids(bundle)
    result: dict[str, Any] = {"schema_version": bundle["schema_version"]}
    for key in sorted(_SET_LIKE_LISTS):
        values = deepcopy(bundle.get(key, []))
        result[key] = sorted(values, key=_canonical_item)
    return result


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

        satisfied_by = edge.get("satisfied_by", "")
        if satisfied_by.startswith("lock:"):
            lock_id = satisfied_by.removeprefix("lock:")
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
