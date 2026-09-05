from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-004-documentation-architecture.md"


class R004AuthoritativeReportTests(unittest.TestCase):
    def test_compatibility_reference_uses_evidence_bearing_states(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("a stale parent-schema binding fails closed", text)
        self.assertIn("verified-exact", text)
        self.assertIn("verified-compatible", text)
        self.assertIn("unverified", text)
        self.assertIn("incompatible", text)
        self.assertIn("parent artifact", text.lower())
        self.assertIn("dependency fingerprint", text.lower())

    def test_research_candidate_and_approved_mapping_are_separate(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("research candidate", text)
        self.assertIn("approved mapping", text)
        self.assertIn("formal publication", text)
        self.assertIn("assessment", text)

    def test_empirical_domains_do_not_promote_storage_empties_or_closure(self):
        text = REPORT.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("empty_observation_count", text)
        self.assertIn("nodes_with_value", text)
        self.assertIn("observed small domain", lower)
        self.assertIn("documented bounded", lower)
        self.assertIn("remark", lower)
        self.assertIn("closed vocabulary", lower)

    def test_provenance_uses_artifact_identity_not_generic_schema_fingerprint(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("Schema fingerprint: <digest>", text)
        self.assertIn("Parent artifact", text)
        self.assertIn("Dependency fingerprint", text)


if __name__ == "__main__":
    unittest.main()
