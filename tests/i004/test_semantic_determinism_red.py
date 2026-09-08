from __future__ import annotations

import copy
import unittest

from tfont.semantic_validation import SemanticValidationError, validate_semantic_bundle
from tests.i004.test_semantic_validation_phase1 import base_sources, bundle


class I004DeterminismRedTests(unittest.TestCase):
    def first_problem(self, sources: dict):
        with self.assertRaises(SemanticValidationError) as raised:
            validate_semantic_bundle(bundle(sources))
        return raised.exception.problem

    def two_invalid_projections(self, *, reverse: bool) -> dict:
        sources = base_sources()
        mapping = sources["mappings"]["mappings"][0]
        original = mapping["projections"][0]

        z_projection = copy.deepcopy(original)
        z_projection["projection_id"] = "projection:z"
        z_projection["formal_kind"] = "class"
        z_projection["semantic_role"] = "relation"

        a_projection = copy.deepcopy(original)
        a_projection["projection_id"] = "projection:a"
        a_projection["formal_kind"] = "property"
        a_projection["semantic_role"] = "entity-type"

        mapping["projections"] = [a_projection, z_projection] if reverse else [z_projection, a_projection]
        return sources

    def test_projection_first_error_uses_canonical_id_order_not_authored_order(self):
        authored_z_first = self.first_problem(self.two_invalid_projections(reverse=False))
        authored_a_first = self.first_problem(self.two_invalid_projections(reverse=True))

        self.assertEqual(authored_z_first.category, "kind_role_conflict")
        self.assertEqual(authored_a_first.category, "kind_role_conflict")
        self.assertEqual(authored_z_first.related_id, "projection:a")
        self.assertEqual(authored_a_first.related_id, "projection:a")
        self.assertEqual(authored_z_first.message, authored_a_first.message)


if __name__ == "__main__":
    unittest.main()
