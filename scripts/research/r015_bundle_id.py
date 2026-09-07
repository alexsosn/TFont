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


def semantic_projection(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return the semantic, order-independent bundle projection.

    Unknown presentation/audit keys are deliberately excluded. P-003 owns the final
    schema; this research prototype proves the identity properties only.
    """

    result: dict[str, Any] = {"schema_version": bundle["schema_version"]}
    for key in sorted(_SET_LIKE_LISTS):
        values = deepcopy(bundle.get(key, []))
        result[key] = sorted(values, key=_canonical_item)
    return result


def bundle_digest(bundle: dict[str, Any]) -> str:
    payload = _canonical_item(semantic_projection(bundle)).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _locks(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["lock_id"]: item for item in bundle.get("ontology_locks", [])}


def _bridges(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["bridge_id"]: item for item in bundle.get("bridge_locks", [])}


def dependency_states(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate active dependency edges without ontology reasoning.

    Each edge is an explicit reviewed TFont dependency requirement. Optional inactive
    edges are diagnostic `inactive`, never failures.
    """

    locks = _locks(bundle)
    bridges = _bridges(bundle)
    states: list[dict[str, str]] = []

    for edge in bundle.get("dependency_edges", []):
        edge_id = edge.get("id") or f"{edge.get('consumer')}->{edge.get('requires')}"
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
            if expected and lock.get("digest") != expected:
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
            if bridge.get("compatibility") == "incompatible":
                states.append({"id": edge_id, "state": "incompatible-bridge"})
                continue
            states.append({"id": edge_id, "state": "satisfied-reviewed-bridge"})
            continue

        states.append({"id": edge_id, "state": "missing-bridge"})

    return states


def executable(bundle: dict[str, Any]) -> bool:
    allowed = {"inactive", "satisfied-exact-lock", "satisfied-reviewed-bridge"}
    return all(item["state"] in allowed for item in dependency_states(bundle))


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    data = json.loads(args.bundle.read_text(encoding="utf-8"))
    print(bundle_digest(data))
    print(json.dumps(dependency_states(data), indent=2, sort_keys=True))
    raise SystemExit(0 if executable(data) else 1)
