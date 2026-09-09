from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
HEADING = "## F-series research ownership"


class ContributorDocumentationREDTests(unittest.TestCase):
    def test_contributing_documents_f_series_ownership_and_checker(self):
        text = CONTRIBUTING.read_text(encoding="utf-8")
        self.assertIn(HEADING, text)
        section = text.split(HEADING, 1)[1]
        if "\n## " in section:
            section = section.split("\n## ", 1)[0]

        self.assertIn("`docs/research/F-NNN-*.md`", section)
        self.assertIn("`**Issue:** #N`", section)
        self.assertIn("same issue owner", section)
        self.assertIn("`python scripts/check_f_series_ownership.py`", section)


if __name__ == "__main__":
    unittest.main()
