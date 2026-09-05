from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS_PATH = ROOT / "docs" / "research" / "data" / "R-005-corpus-pins.json"
GENERATED = ROOT / "docs" / "research" / "data" / "generated" / "r005"

# Stress targets without a committed released TF artifact are intentionally absent.
PIN_TO_FILE = {
    "bhsa": "bhsa.json",
    "cuc": "cuc.json",
    "syriac": "syriac.json",
    "peshitta": "peshitta.json",
    "syrnt": "syrnt.json",
    "extrabiblical": "extrabiblical.json",
    "tlhdig_tf": "tlhdig-tf.json",
}

CORPUS_ID = {
    "tlhdig_tf": "tlhdig-tf",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class GeneratedInventoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))["corpora"]
        cls.inventories = {
            key: json.loads((GENERATED / filename).read_text(encoding="utf-8"))
            for key, filename in PIN_TO_FILE.items()
        }

    def test_exact_generated_file_set(self):
        self.assertEqual(
            {path.name for path in GENERATED.glob("*.json")},
            set(PIN_TO_FILE.values()),
        )

    def test_identity_version_slot_and_node_counts_match_research_pins(self):
        for key, inventory in self.inventories.items():
            with self.subTest(corpus=key):
                pin = self.pins[key]
                self.assertEqual(inventory["schema_version"], 1)
                self.assertEqual(inventory["evidence_kind"], "loaded_tf_artifact")
                self.assertEqual(inventory["corpus_id"], CORPUS_ID.get(key, key))
                self.assertEqual(inventory["repository"], pin["repository"])
                self.assertEqual(inventory["revision"], pin["commit"])
                self.assertEqual(inventory["tf_version"], pin["tf_version"])
                self.assertEqual(inventory["slot_type"], pin["slot_type"])
                self.assertEqual(inventory["node_types"], pin["node_counts"])
                self.assertRegex(inventory["tf_files_sha256"], SHA256_RE)

    def test_generated_edge_inventory_covers_all_pinned_custom_edges(self):
        for key, inventory in self.inventories.items():
            with self.subTest(corpus=key):
                expected = set(self.pins[key].get("custom_edges", []))
                observed = set(inventory["edge_features"])
                self.assertEqual(observed, expected)

    def test_feature_metadata_and_applicability_are_explicit(self):
        for key, inventory in self.inventories.items():
            for name, feature in inventory["node_features"].items():
                with self.subTest(corpus=key, feature=name):
                    self.assertEqual(feature["kind"], "node")
                    self.assertIsInstance(feature["metadata"], dict)
                    self.assertIn("valueType", feature["metadata"])
                    self.assertIsInstance(feature["applies_to"], list)
                    self.assertIsInstance(feature["nodes_with_value"], int)
                    self.assertIsInstance(feature["node_records_seen"], int)
                    self.assertLessEqual(
                        feature["nodes_with_value"], feature["node_records_seen"]
                    )

            for name, feature in inventory["edge_features"].items():
                with self.subTest(corpus=key, edge=name):
                    self.assertEqual(feature["kind"], "edge")
                    self.assertIsInstance(feature["metadata"], dict)
                    self.assertIn("valueType", feature["metadata"])
                    self.assertIsInstance(feature["source_types"], list)
                    self.assertIsInstance(feature["target_types"], list)
                    self.assertIsInstance(feature["valued"], bool)
                    self.assertIsInstance(feature["edge_count"], int)

    def test_node_value_accounting_and_domains_exclude_storage_empties(self):
        for key, inventory in self.inventories.items():
            for name, feature in inventory["node_features"].items():
                with self.subTest(corpus=key, feature=name):
                    self.assertEqual(
                        feature["observation_count"] + feature["empty_observation_count"],
                        feature["raw_observation_count"],
                    )
                    self.assertEqual(
                        feature["nodes_with_value"], feature["observation_count"]
                    )
                    self._check_domain(feature)

    def test_valued_edge_domains_exclude_storage_empties(self):
        for key, inventory in self.inventories.items():
            for name, feature in inventory["edge_features"].items():
                if not feature["valued"]:
                    continue
                with self.subTest(corpus=key, edge=name):
                    self.assertEqual(
                        feature["observation_count"] + feature["empty_observation_count"],
                        feature["raw_observation_count"],
                    )
                    self.assertEqual(feature["edge_count"], feature["raw_observation_count"])
                    self._check_domain(feature)

    def test_cuc_review_regressions_are_pinned(self):
        cuc = self.inventories["cuc"]["node_features"]
        self.assertEqual(cuc["cert"]["observed_values"], ["False", "True"])
        self.assertEqual(
            set(cuc["emen"]["observed_values"]),
            {"excised", "missing", "redundant", "remark", "restored"},
        )
        self.assertEqual(cuc["cert"]["applies_to"], ["sign"])
        self.assertEqual(cuc["emen"]["applies_to"], ["sign"])

    def test_known_semantic_edge_directions_are_preserved(self):
        bhsa = self.inventories["bhsa"]["edge_features"]
        self.assertIn("mother", bhsa)
        self.assertFalse(bhsa["mother"]["valued"])

        tlhdig = self.inventories["tlhdig_tf"]["edge_features"]
        self.assertEqual(tlhdig["lexeme"]["source_types"], ["analysis"])
        self.assertEqual(tlhdig["lexeme"]["target_types"], ["lex"])
        self.assertTrue(tlhdig["selected"]["valued"])
        self.assertEqual(tlhdig["selected"]["source_types"], ["word"])
        self.assertEqual(tlhdig["selected"]["target_types"], ["analysis"])

    def _check_domain(self, feature):
        self.assertTrue(
            feature["domain_policy"]
            if "domain_policy" in feature
            else True
        )
        if feature["domain_observation"] == "observed_small_domain":
            values = feature["observed_values"]
            self.assertEqual(len(values), feature["observed_unique_count"])
        else:
            values = feature.get("sample_values", [])
        self.assertNotIn("", values)
        self.assertNotIn(None, values)


if __name__ == "__main__":
    unittest.main()
