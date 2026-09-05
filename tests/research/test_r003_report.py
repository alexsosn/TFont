from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-003-ergonomics.md"


class R003AuthoritativeReportTests(unittest.TestCase):
    def test_capability_examples_use_evidence_bearing_compatibility_states(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn('"compatibility": "verified"', text)
        self.assertIn("verified-exact", text)
        self.assertIn("verified-compatible", text)
        self.assertIn("unverified", text)
        self.assertIn("non-executable", text.lower())
        self.assertNotIn("allow_unverified", text)

    def test_research_candidate_strength_cannot_activate_runtime_mapping(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("r-005", text)
        self.assertIn("candidate", text)
        self.assertIn("approved", text)
        self.assertIn("cannot", text)
        self.assertIn("exact", text)

    def test_dense_empty_records_are_non_semantic(self):
        text = REPORT.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("empty-string", lower)
        self.assertIn("no semantic value", lower)
        self.assertIn("nodes_with_value", text)
        self.assertIn("applicable", lower)
        self.assertIn("explicit absence", lower)


if __name__ == "__main__":
    unittest.main()
