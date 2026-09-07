from copy import deepcopy

from scripts.research.r015_bundle_id import bundle_digest, dependency_states, executable


def _bundle():
    return {
        "schema_version": 1,
        "profile_contracts": ["written-text@1"],
        "ontology_locks": [
            {"lock_id": "crm-old", "digest": "sha256:crm-old"},
            {"lock_id": "crm-current", "digest": "sha256:crm-current"},
            {"lock_id": "crmtex", "digest": "sha256:crmtex"},
        ],
        "bridge_locks": [
            {
                "bridge_id": "crm-bridge",
                "digest": "sha256:bridge",
                "source_lock_id": "crm-old",
                "source_lock_digest": "sha256:crm-old",
                "target_lock_id": "crm-current",
                "target_lock_digest": "sha256:crm-current",
                "review_status": "reviewed",
                "reviewed_content_digest": "sha256:bridge",
                "compatibility": "compatible",
            }
        ],
        "dependency_edges": [
            {
                "id": "crmtex-crm",
                "consumer": "crmtex",
                "requires": "crm-old",
                "satisfied_by": "bridge:crm-bridge",
                "active": True,
            }
        ],
        "display_label": "ignored presentation field",
    }


def test_reordering_set_like_members_does_not_change_digest():
    a = _bundle()
    b = deepcopy(a)
    b["ontology_locks"].reverse()
    b["bridge_locks"].reverse()
    b["dependency_edges"].reverse()
    assert bundle_digest(a) == bundle_digest(b)


def test_presentation_fields_do_not_change_digest():
    a = _bundle()
    b = deepcopy(a)
    b["display_label"] = "different"
    b["retrieved_at"] = "2099-01-01T00:00:00Z"
    assert bundle_digest(a) == bundle_digest(b)


def test_participating_ontology_digest_changes_bundle_identity():
    a = _bundle()
    b = deepcopy(a)
    b["ontology_locks"][0]["digest"] = "sha256:changed"
    assert bundle_digest(a) != bundle_digest(b)


def test_bridge_digest_changes_bundle_identity():
    a = _bundle()
    b = deepcopy(a)
    b["bridge_locks"][0]["digest"] = "sha256:changed-bridge"
    assert bundle_digest(a) != bundle_digest(b)


def test_unused_known_ontology_outside_active_bundle_is_irrelevant():
    a = _bundle()
    # The active bundle is the object passed to the digester. A registry-level known
    # ontology that is not selected must not be injected into this projection.
    registry_only = {"lock_id": "crmarchaeo", "digest": "sha256:arch"}
    assert registry_only not in a["ontology_locks"]
    assert bundle_digest(a) == bundle_digest(deepcopy(a))


def test_active_missing_bridge_fails_closed():
    b = _bundle()
    b["bridge_locks"] = []
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "missing-bridge"}]
    assert not executable(b)


def test_inactive_optional_dependency_does_not_fail():
    b = _bundle()
    b["bridge_locks"] = []
    b["dependency_edges"][0]["active"] = False
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "inactive"}]
    assert executable(b)


def test_stale_bridge_detects_lock_digest_change():
    b = _bundle()
    b["ontology_locks"][0]["digest"] = "sha256:new-crm-old"
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "stale-bridge"}]
    assert not executable(b)


def test_unreviewed_bridge_cannot_execute():
    b = _bundle()
    b["bridge_locks"][0]["review_status"] = "draft"
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "unreviewed-bridge"}]
    assert not executable(b)


def test_review_is_bound_to_bridge_content_digest():
    b = _bundle()
    b["bridge_locks"][0]["digest"] = "sha256:edited"
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "unreviewed-bridge"}]
    assert not executable(b)


def test_incompatible_reviewed_bridge_fails_closed():
    b = _bundle()
    b["bridge_locks"][0]["compatibility"] = "incompatible"
    assert dependency_states(b) == [{"id": "crmtex-crm", "state": "incompatible-bridge"}]
    assert not executable(b)


def test_exact_locked_dependency_needs_no_bridge():
    b = _bundle()
    b["bridge_locks"] = []
    b["dependency_edges"][0] = {
        "id": "crmtex-crm",
        "consumer": "crmtex",
        "requires": "crm-old",
        "satisfied_by": "lock:crm-old",
        "required_lock_digest": "sha256:crm-old",
        "active": True,
    }
    assert dependency_states(b) == [
        {"id": "crmtex-crm", "state": "satisfied-exact-lock"}
    ]
    assert executable(b)


def test_same_namespace_conceptually_does_not_override_content_identity():
    a = _bundle()
    b = deepcopy(a)
    a["ontology_locks"][0]["namespace"] = "http://example.org/model/"
    b["ontology_locks"][0]["namespace"] = "http://example.org/model/"
    b["ontology_locks"][0]["digest"] = "sha256:different-release"
    assert bundle_digest(a) != bundle_digest(b)
