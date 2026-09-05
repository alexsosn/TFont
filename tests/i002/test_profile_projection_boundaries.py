from __future__ import annotations

import unittest

from tfont.digests import DigestError, profile_semantic_digest


def profile_projection() -> dict:
    return {
        "profile_id": "tfont-test",
        "schema_version": 1,
        "semantic_contract_version": 1,
        "semantic_domains": ["morphology"],
        "expected_parent_manifest_digest": "sha256:parent",
        "dependencies": [
            {"dependency_id": "dep:a", "component_id": "c", "kind": "feature"},
        ],
        "ontology_locks": [
            {"lock_id": "lock:a", "content_digest": "sha256:a"},
        ],
        "mappings": [
            {"mapping_id": "map:a", "mapping_semantic_digest": "sha256:ma"},
        ],
        "review_readiness": [
            {"mapping_id": "map:a", "status": "reviewed", "reviewed_digest_matches": True},
        ],
        "applicability": {},
        "publication_semantics": {},
    }


class ProfileProjectionBoundaryTests(unittest.TestCase):
    def assert_projection_error(self, projection: dict) -> None:
        with self.assertRaises(DigestError) as raised:
            profile_semantic_digest(projection)
        self.assertEqual(raised.exception.problem.category, "projection_error")

    def test_ontology_lock_audit_timestamp_cannot_enter_semantic_digest(self):
        projection = profile_projection()
        projection["ontology_locks"][0]["retrieved_at"] = "2026-09-06T00:00:00Z"
        self.assert_projection_error(projection)

    def test_mapping_review_provenance_cannot_enter_profile_semantic_digest(self):
        projection = profile_projection()
        projection["mappings"][0]["review"] = {
            "reviewer_id": "audit-only",
            "reviewed_at": "2026-09-06T00:00:00Z",
        }
        self.assert_projection_error(projection)

    def test_lock_and_mapping_semantic_identity_changes_still_change_digest(self):
        base = profile_projection()
        changed_lock = profile_projection()
        changed_lock["ontology_locks"][0]["content_digest"] = "sha256:changed-lock"
        changed_mapping = profile_projection()
        changed_mapping["mappings"][0]["mapping_semantic_digest"] = "sha256:changed-mapping"
        self.assertNotEqual(profile_semantic_digest(base), profile_semantic_digest(changed_lock))
        self.assertNotEqual(profile_semantic_digest(base), profile_semantic_digest(changed_mapping))


if __name__ == "__main__":
    unittest.main()
