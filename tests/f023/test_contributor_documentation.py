from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"


class ContributorDocumentationContractTests(unittest.TestCase):
    def test_contributing_explains_research_authority_and_all_downstream_carriers(self):
        text = CONTRIBUTING.read_text(encoding="utf-8")

        required = {
            "one-way authority": (
                "F-series research metadata is the sole allocation authority; "
                "plans, workflows, and test packages only claim an existing allocation."
            ),
            "plan namespace": "docs/plans/F-NNN-*.md",
            "plan owner": "**Issue:** #N",
            "workflow namespace": ".github/workflows/fNNN-*.yml",
            "workflow yaml namespace": ".github/workflows/fNNN-*.yaml",
            "workflow owner": "# Issue: #N",
            "test sidecar": "tests/fNNN/issue-owner.txt",
            "test owner": "Issue: #N",
            "checker command": "python scripts/check_f_series_ownership.py .",
        }
        missing = [label for label, snippet in required.items() if snippet not in text]
        self.assertEqual(missing, [], f"CONTRIBUTING.md is missing F-series ownership guidance: {missing}")


if __name__ == "__main__":
    unittest.main()
