import hashlib

import pytest

from scripts.research.r015_bundle_id import bundle_digest, executable


def _digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _lock(lock_id: str, *, release: str) -> dict:
    return {
        "lock_id": lock_id,
        "ontology_id": lock_id,
        "support_tier": "core",
        "term_namespace": f"{lock_id}:",
        "release": release,
        "source_uri": f"https://example.org/{lock_id}/{release}",
        "content_digest": _digest(lock_id),
        "license": "test-license",
        "terms_used": [f"{lock_id}:T1"],
    }


def _exact_lock_bundle(active_marker=...):
    edge = {
        "id": "required-edge",
        "consumer": "consumer",
        "requires": "required",
        "satisfied_by": "lock:required",
        "required_lock_release": "1.0",
        "required_lock_digest": _digest("required"),
    }
    if active_marker is not ...:
        edge["active"] = active_marker
    return {
        "schema_version": 1,
        "profile_contracts": ["profile@1"],
        "ontology_locks": [
            _lock("consumer", release="1.0"),
            _lock("required", release="1.0"),
        ],
        "bridge_locks": [],
        "dependency_edges": [edge],
    }


@pytest.mark.parametrize("value", [0, 1, None, "", "false", [], {}])
def test_dependency_active_must_be_exact_boolean(value):
    bundle = _exact_lock_bundle(value)
    with pytest.raises(ValueError, match="active.*boolean|boolean.*active"):
        bundle_digest(bundle)
    assert not executable(bundle)


def test_missing_active_defaults_to_active_not_inactive():
    bundle = _exact_lock_bundle()
    assert executable(bundle)

    bundle["ontology_locks"][1]["content_digest"] = _digest("wrong-required")
    assert not executable(bundle)


@pytest.mark.parametrize("value", [0, 2, 999, "1", "future", True, None, 1.0])
def test_schema_version_must_be_exact_supported_integer_one(value):
    bundle = _exact_lock_bundle()
    bundle["schema_version"] = value
    with pytest.raises(ValueError, match="schema_version.*1|supported.*schema|schema.*version"):
        bundle_digest(bundle)
    assert not executable(bundle)


def test_missing_schema_version_fails_closed():
    bundle = _exact_lock_bundle()
    del bundle["schema_version"]
    with pytest.raises(ValueError, match="schema_version.*1|supported.*schema|schema.*version"):
        bundle_digest(bundle)
    assert not executable(bundle)
