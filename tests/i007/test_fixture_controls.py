from __future__ import annotations

import json
import unittest

from tests.i006._fixtures import compiled_noun_ir


class I007FixtureControlTests(unittest.TestCase):
    def test_compiled_noun_fixture_exposes_one_valid_v1_dependency(self):
        variant = compiled_noun_ir(("bhsa",)).variants[0]
        self.assertEqual(variant.release_signature.dependency_contract_version, 1)
        self.assertEqual(len(variant.release_signature.dependency_records), 1)
        dependency_id, canonical_record = variant.release_signature.dependency_records[0]
        record = json.loads(canonical_record)
        self.assertEqual(record["dependency_id"], dependency_id)
        self.assertEqual(record["kind"], "native-value-present")
        self.assertEqual(record["component_id"], "bhsa-tf")
        self.assertEqual(record["assertion"]["node_type"], "word")
        self.assertEqual(record["assertion"]["feature"], "sp")
        self.assertEqual(record["assertion"]["value"], "subs")


if __name__ == "__main__":
    unittest.main()
