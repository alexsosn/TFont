from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-001-distribution-architecture.md"


class R001AuthoritativeReportTests(unittest.TestCase):
    def test_main_report_uses_reconciled_artifact_and_dependency_contract(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertNotIn("The sidecar is the semantic source/runtime contract.", text)
        self.assertNotIn("`verified-schema`", text)
        self.assertNotIn("`available-unverified`", text)

        self.assertIn("profile source", text)
        self.assertIn("runtime sidecar", text)
        self.assertIn("artifact digest", text.lower())
        self.assertIn("profile dependency closure", text.lower())
        self.assertIn("`verified-compatible`", text)
        self.assertIn("`unverified`", text)
        self.assertIn("non-executable", text.lower())

    def test_main_report_preserves_r005_empty_record_and_domain_distinctions(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("empty-string", text)
        self.assertIn("no semantic value", text)
        self.assertIn("observed small", text)
        self.assertIn("closed vocabulary", text)

    def test_main_report_records_r005_as_accepted_dependency(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn(
            "merge is blocked on independent acceptance of R-005 (#7)", text
        )
        self.assertNotIn("14ba5919a283d11912f994036ad9495c0346a99a", text)
        self.assertIn("R-005 accepted", text)
        self.assertIn("48c8bd78d0c3a0501b2fdec6946db5df90517bdb", text)


if __name__ == "__main__":
    unittest.main()
