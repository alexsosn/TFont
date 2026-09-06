from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"


class ReadmeStatusContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = README.read_text(encoding="utf-8")

    def test_bootstrap_research_only_status_is_retired(self):
        self.assertNotIn("first project phase is **research only**", self.readme.lower())

    def test_merged_capability_sections_are_named(self):
        self.assertIn("Structural source validation", self.readme)
        self.assertIn("Canonicalization and digests", self.readme)

    def test_source_checkout_install_is_documented(self):
        self.assertIn("python -m pip install -e .", self.readme)

    def test_examples_use_current_public_api_names(self):
        self.assertIn("load_and_validate", self.readme)
        self.assertIn("canonical_json_bytes", self.readme)

    def test_unmerged_surfaces_are_not_claimed_as_implemented(self):
        lowered = self.readme.lower()
        for claim in (
            "semantic_search is implemented",
            "verified-compatible is implemented",
            "i-003 is implemented",
        ):
            with self.subTest(claim=claim):
                self.assertNotIn(claim, lowered)


if __name__ == "__main__":
    unittest.main()
