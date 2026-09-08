from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"


class ReadmeStatusContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = README.read_text(encoding="utf-8")
        cls.lowered = cls.readme.lower()

    def test_bootstrap_research_only_status_is_retired(self):
        self.assertNotIn("first project phase is **research only**", self.lowered)

    def test_merged_capability_sections_are_named(self):
        self.assertIn("Structural source validation", self.readme)
        self.assertIn("Canonicalization and digests", self.readme)
        self.assertIn("Parent/component identity", self.readme)

    def test_parent_identity_is_not_described_as_future_work(self):
        self.assertNotIn("parent-component identity, cross-artifact semantic validation", self.lowered)

    def test_accepted_semantic_adapter_architecture_is_documented_without_overclaiming(self):
        self.assertIn("common ontology semantic-adapter", self.lowered)
        self.assertIn("accepted architecture", self.lowered)
        self.assertIn("cross-artifact semantic validation", self.lowered)
        self.assertTrue(
            "not yet shipped" in self.lowered or "not yet implemented" in self.lowered,
            "README must distinguish accepted semantic architecture from shipped semantic validation/runtime",
        )

    def test_source_checkout_install_is_documented(self):
        self.assertIn("python -m pip install -e .", self.readme)

    def test_examples_use_current_public_api_names(self):
        self.assertIn("load_and_validate", self.readme)
        self.assertIn("canonical_json_bytes", self.readme)
        self.assertIn("directory_component_digest", self.readme)
        self.assertIn("parent_manifest_digest", self.readme)

    def test_unmerged_surfaces_are_not_claimed_as_implemented(self):
        for claim in (
            "semantic_search is implemented",
            "verified-compatible is implemented",
            "cross-artifact semantic validation is implemented",
        ):
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.lowered)


if __name__ == "__main__":
    unittest.main()
