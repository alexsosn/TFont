from copy import deepcopy
import hashlib

import pytest

from scripts.research.r015_bundle_id import (
    bridge_content_digest,
    bundle_digest,
    dependency_states,
)


def _digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _lock(lock_id: str, *, terms: list[str], release: str = "1.0") -> dict:
    return {
        "lock_id": lock_id,
        "ontology_id": f"ontology:{lock_id}",
        "support_tier": "core",
        "term_namespace": f"urn:{lock_id}:",
        "release": release,
        "source_uri": f"https://example.org/{lock_id}/{release}",
        "content_digest": _digest(lock_id),
        "license": "test-license",
        "terms_used": list(terms),
    }


def _scope(source_term: str = "old:F28", target_term: str = "new:F28") -> dict:
    return {
        "source_term": source_term,
        "target_term": target_term,
        "relation": "reviewed-continuity",
    }


def _bundle(*, source_term: str = "old:F28", target_term: str = "new:F28") -> dict:
    bridge = {
        "bridge_id": "f28",
        "source_lock_id": "old",
        "source_lock_release": "1.0",
        "source_lock_digest": _digest("old"),
        "target_lock_id": "new",
        "target_lock_release": "1.0",
        "target_lock_digest": _digest("new"),
        "scope": _scope(source_term, target_term),
        "compatibility": "compatible",
        "evidence_id": "evidence:f28",
        "evidence_digest": _digest("evidence"),
        "runtime_strength": "exact",
        "runtime_limitations": ["term-scoped continuity only"],
        "review_status": "reviewed",
        "review_id": "review:f28",
        "reviewer_id": "github:independent-reviewer",
        "reviewed_at": "2026-09-07T17:00:00Z",
    }
    bridge["digest"] = bridge_content_digest(bridge)
    bridge["reviewed_content_digest"] = bridge["digest"]
    return {
        "schema_version": 1,
        "profile_contracts": ["written-text@1"],
        "ontology_locks": [
            _lock("consumer", terms=["consumer:TX1"]),
            _lock("old", terms=["old:F28"]),
            _lock("new", terms=["new:F28"]),
        ],
        "bridge_locks": [bridge],
        "dependency_edges": [
            {
                "id": "edge",
                "consumer": "consumer",
                "requires": "old",
                "satisfied_by": "bridge:f28",
                "required_bridge_scope": _scope(source_term, target_term),
                "active": True,
            }
        ],
    }


def test_terms_used_is_part_of_bundle_semantic_identity():
    a = _bundle()
    b = deepcopy(a)
    b["ontology_locks"][1]["terms_used"].append("old:F29")
    assert bundle_digest(a) != bundle_digest(b)


def test_semantic_lock_release_is_part_of_bundle_identity_even_when_payload_digest_is_same():
    a = _bundle()
    b = deepcopy(a)
    b["ontology_locks"][1]["release"] = "1.1"
    assert (
        b["ontology_locks"][1]["content_digest"]
        == a["ontology_locks"][1]["content_digest"]
    )
    assert bundle_digest(a) != bundle_digest(b)


def test_terms_used_reordering_is_not_a_semantic_identity_change():
    a = _bundle()
    a["ontology_locks"][1]["terms_used"] = ["old:F28", "old:F29"]
    b = deepcopy(a)
    b["ontology_locks"][1]["terms_used"].reverse()
    assert bundle_digest(a) == bundle_digest(b)


def test_source_bridge_term_must_be_declared_by_source_lock():
    b = _bundle(source_term="old:F288")
    with pytest.raises(ValueError, match="source_term.*terms_used|terms_used.*source_term"):
        bundle_digest(b)


def test_target_bridge_term_must_be_declared_by_target_lock():
    b = _bundle(target_term="new:F288")
    with pytest.raises(ValueError, match="target_term.*terms_used|terms_used.*target_term"):
        bundle_digest(b)


def test_endpoint_release_change_with_same_payload_digest_makes_bridge_stale():
    b = _bundle()
    b["ontology_locks"][1]["release"] = "1.1"
    assert dependency_states(b) == [{"id": "edge", "state": "stale-bridge"}]


def test_retrieval_storage_metadata_is_outside_semantic_lock_input():
    b = _bundle()
    b["ontology_locks"][1]["retrieved_at"] = "2099-01-01T00:00:00Z"
    b["ontology_locks"][1]["snapshot_artifact"] = "/tmp/other-layout.owl"
    with pytest.raises(ValueError, match="projection_error|unknown projection fields"):
        bundle_digest(b)
