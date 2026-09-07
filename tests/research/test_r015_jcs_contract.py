import hashlib
import re

import pytest

from scripts.research.r015_bundle_id import bridge_content_digest, bundle_digest
from tfont.digests import canonical_json_bytes


DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _scope():
    # U+10000 sorts before U+E000 under RFC 8785 UTF-16 ordering, while Python
    # code-point ordering does the opposite. The extra keys force a real JCS check.
    return {
        "source_term": "old:F28",
        "target_term": "new:F28",
        "relation": "reviewed-continuity",
        "\ue000": "bmp-private-use",
        "\U00010000": "astral",
    }


def _bridge():
    return {
        "bridge_id": "f28",
        "source_lock_id": "old",
        "source_lock_digest": _digest("old"),
        "target_lock_id": "new",
        "target_lock_digest": _digest("new"),
        "scope": _scope(),
        "compatibility": "compatible",
        "evidence_id": "evidence:f28",
        "evidence_digest": _digest("evidence"),
        "runtime_strength": "exact",
        "runtime_limitations": ["term scoped"],
        "review_status": "reviewed",
        "review_id": "review:f28",
        "reviewer_id": "github:reviewer",
        "reviewed_at": "2026-09-07T15:00:00Z",
    }


def _semantic_bridge_payload(bridge):
    fields = (
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
    return {key: bridge[key] for key in fields if key in bridge}


def test_bridge_digest_is_sha256_of_i002_jcs_bytes():
    bridge = _bridge()
    expected = "sha256:" + hashlib.sha256(
        canonical_json_bytes(_semantic_bridge_payload(bridge))
    ).hexdigest()
    assert bridge_content_digest(bridge) == expected
    assert DIGEST_RE.fullmatch(expected)


def test_bundle_digest_uses_i002_jcs_and_has_canonical_digest_shape():
    bridge = _bridge()
    bridge["digest"] = bridge_content_digest(bridge)
    bridge["reviewed_content_digest"] = bridge["digest"]
    bundle = {
        "schema_version": 1,
        "profile_contracts": ["written-text@1"],
        "ontology_locks": [
            {"lock_id": "consumer", "digest": _digest("consumer")},
            {"lock_id": "old", "digest": _digest("old")},
            {"lock_id": "new", "digest": _digest("new")},
        ],
        "bridge_locks": [bridge],
        "dependency_edges": [
            {
                "id": "edge",
                "consumer": "consumer",
                "requires": "old",
                "satisfied_by": "bridge:f28",
                "required_bridge_scope": _scope(),
                "active": True,
            }
        ],
    }
    result = bundle_digest(bundle)
    assert DIGEST_RE.fullmatch(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_lock_digest", "sha256:not-hex"),
        ("target_lock_digest", "sha256:ABCDEF"),
        ("evidence_digest", "not-a-digest"),
    ],
)
def test_bridge_digest_fields_must_use_i002_sha256_representation(field, value):
    bridge = _bridge()
    bridge[field] = value
    bridge["digest"] = bridge_content_digest(bridge)
    bridge["reviewed_content_digest"] = bridge["digest"]
    bundle = {
        "schema_version": 1,
        "profile_contracts": ["written-text@1"],
        "ontology_locks": [
            {"lock_id": "consumer", "digest": _digest("consumer")},
            {"lock_id": "old", "digest": _digest("old")},
            {"lock_id": "new", "digest": _digest("new")},
        ],
        "bridge_locks": [bridge],
        "dependency_edges": [
            {
                "id": "edge",
                "consumer": "consumer",
                "requires": "old",
                "satisfied_by": "bridge:f28",
                "required_bridge_scope": _scope(),
                "active": True,
            }
        ],
    }
    with pytest.raises(ValueError, match="digest"):
        bundle_digest(bundle)


def test_ontology_lock_digest_must_use_i002_sha256_representation():
    bundle = {
        "schema_version": 1,
        "profile_contracts": ["linguistic@1"],
        "ontology_locks": [{"lock_id": "olia", "digest": "sha256:fake"}],
        "bridge_locks": [],
        "dependency_edges": [],
    }
    with pytest.raises(ValueError, match="digest"):
        bundle_digest(bundle)
