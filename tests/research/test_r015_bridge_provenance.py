from copy import deepcopy

import pytest

from scripts.research.r015_bundle_id import (
    bridge_content_digest,
    bundle_digest,
    dependency_states,
    executable,
)


def _scope():
    return {
        "source_term": "frbroo-2.4:F28",
        "target_term": "lrmoo-1.1.1:F28",
        "relation": "reviewed-continuity",
    }


def _refresh_bridge(bridge, *, refresh_review=True):
    bridge["digest"] = bridge_content_digest(bridge)
    if refresh_review:
        bridge["reviewed_content_digest"] = bridge["digest"]


def _bundle():
    bridge = {
        "bridge_id": "f28-continuity",
        "source_lock_id": "frbroo-2.4",
        "source_lock_digest": "sha256:frbroo",
        "target_lock_id": "lrmoo-1.1.1",
        "target_lock_digest": "sha256:lrmoo",
        "scope": _scope(),
        "compatibility": "compatible",
        "evidence_id": "lrmoo-1.1.1-migration-table-f28",
        "evidence_digest": "sha256:evidence",
        "runtime_strength": "exact",
        "runtime_limitations": ["term-scoped continuity only"],
        "review_status": "reviewed",
        "review_id": "review:r015-f28-001",
        "reviewed_at": "2026-09-07T15:00:00Z",
    }
    _refresh_bridge(bridge)
    return {
        "schema_version": 1,
        "profile_contracts": ["written-text@1"],
        "ontology_locks": [
            {"lock_id": "crmtex-2.0", "digest": "sha256:crmtex"},
            {"lock_id": "frbroo-2.4", "digest": "sha256:frbroo"},
            {"lock_id": "lrmoo-1.1.1", "digest": "sha256:lrmoo"},
        ],
        "bridge_locks": [bridge],
        "dependency_edges": [
            {
                "id": "crmtex-f28",
                "consumer": "crmtex-2.0",
                "requires": "frbroo-2.4",
                "satisfied_by": "bridge:f28-continuity",
                "required_bridge_scope": _scope(),
                "active": True,
            }
        ],
    }


def test_complete_provenance_bound_exact_bridge_is_executable():
    b = _bundle()
    assert dependency_states(b) == [
        {"id": "crmtex-f28", "state": "satisfied-reviewed-bridge"}
    ]
    assert executable(b)


@pytest.mark.parametrize("field", ["evidence_id", "evidence_digest"])
def test_evidence_identity_is_required(field):
    b = _bundle()
    del b["bridge_locks"][0][field]
    _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError, match=field):
        bundle_digest(b)
    assert not executable(b)


@pytest.mark.parametrize("field", ["review_id", "reviewed_at"])
def test_stable_review_identity_and_date_are_required(field):
    b = _bundle()
    del b["bridge_locks"][0][field]
    with pytest.raises(ValueError, match=field):
        bundle_digest(b)
    assert not executable(b)


@pytest.mark.parametrize("field", ["runtime_strength", "runtime_limitations"])
def test_runtime_semantics_are_required(field):
    b = _bundle()
    del b["bridge_locks"][0][field]
    _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError, match=field):
        bundle_digest(b)
    assert not executable(b)


def test_runtime_limitations_must_be_non_empty_strings():
    b = _bundle()
    b["bridge_locks"][0]["runtime_limitations"] = []
    _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError, match="runtime_limitations"):
        bundle_digest(b)
    assert not executable(b)


def test_approximate_bridge_is_not_exact_executable():
    b = _bundle()
    b["bridge_locks"][0]["runtime_strength"] = "approximate"
    _refresh_bridge(b["bridge_locks"][0])
    assert dependency_states(b) == [
        {"id": "crmtex-f28", "state": "non-exact-bridge-strength"}
    ]
    assert not executable(b)


def test_unknown_runtime_strength_is_rejected():
    b = _bundle()
    b["bridge_locks"][0]["runtime_strength"] = "sort-of-compatible"
    _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError, match="runtime_strength"):
        bundle_digest(b)
    assert not executable(b)


def test_evidence_and_runtime_semantics_are_content_addressed():
    a = _bundle()
    for field, value in (
        ("evidence_id", "different-evidence"),
        ("evidence_digest", "sha256:different-evidence"),
        ("runtime_strength", "approximate"),
        ("runtime_limitations", ["different limitation"]),
    ):
        b = deepcopy(a)
        b["bridge_locks"][0][field] = value
        _refresh_bridge(b["bridge_locks"][0])
        assert bundle_digest(a) != bundle_digest(b), field


def test_review_identity_is_bundle_identity_but_display_name_is_not():
    a = _bundle()
    b = deepcopy(a)
    b["bridge_locks"][0]["review_id"] = "review:r015-f28-002"
    assert bundle_digest(a) != bundle_digest(b)

    c = deepcopy(a)
    c["bridge_locks"][0]["reviewer_display_name"] = "Display Name Only"
    assert bundle_digest(a) == bundle_digest(c)
