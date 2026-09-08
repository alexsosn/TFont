from __future__ import annotations

import unittest

import tfont
import tfont.digests as digests
from tfont.semantic_validation import SemanticValidationError, validate_semantic_bundle
from tests.i004.test_semantic_validation_phase3 import bundle, reviewed_sources


class I004PublicContractTests(unittest.TestCase):
    def test_mapping_v2_digest_api_is_available_from_tfont_digests(self):
        self.assertEqual(
            getattr(digests, "MAPPING_SEMANTIC_ALGORITHM_V2", None),
            "tfont-mapping-semantic-sha256-v2",
        )
        self.assertTrue(callable(getattr(digests, "mapping_semantic_digest_v2", None)))

    def test_projection_digest_api_uses_planned_public_name(self):
        self.assertEqual(
            getattr(digests, "PROJECTION_SEMANTIC_ALGORITHM", None),
            "tfont-projection-semantic-sha256-v1",
        )
        self.assertTrue(callable(getattr(digests, "projection_semantic_digest_v1", None)))

    def test_package_root_exports_i004_validator_surface(self):
        for name in (
            "SemanticArtifact",
            "SemanticSourceBundle",
            "SemanticValidationProblem",
            "SemanticValidationError",
            "SemanticIndexes",
            "ValidatedSemanticBundle",
            "validate_semantic_bundle",
        ):
            self.assertTrue(hasattr(tfont, name), name)

    def test_stale_mapping_digest_uses_frozen_category(self):
        sources = reviewed_sources()
        sources["mappings"]["mappings"][0]["native_binding"]["node_type"] = "phrase"
        with self.assertRaises(SemanticValidationError) as raised:
            validate_semantic_bundle(bundle(sources))
        self.assertEqual(raised.exception.problem.category, "stale_semantic_digest")

    def test_stale_review_binding_uses_frozen_category(self):
        sources = reviewed_sources()
        sources["mappings"]["mappings"][0]["review"]["reviewed_mapping_digest"] = "sha256:stale"
        with self.assertRaises(SemanticValidationError) as raised:
            validate_semantic_bundle(bundle(sources))
        self.assertEqual(raised.exception.problem.category, "stale_review_binding")


if __name__ == "__main__":
    unittest.main()
