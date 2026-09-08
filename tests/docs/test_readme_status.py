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
        self.assertIn("### Cross-artifact semantic validation", self.readme)

    def test_parent_identity_is_not_described_as_future_work(self):
        self.assertNotIn("parent-component identity, cross-artifact semantic validation", self.lowered)

    def test_semantic_validation_is_documented_as_shipped_without_runtime_overclaim(self):
        self.assertIn("common ontology semantic-adapter", self.lowered)
        self.assertIn("accepted architecture", self.lowered)
        self.assertIn("semanticsourcebundle", self.lowered)
        self.assertIn("validate_semantic_bundle", self.readme)
        for stale in (
            "cross-artifact semantic validation, compatibility evaluation",
            "not yet shipped cross-artifact semantic validation",
            "validator or resolver is already implemented on `main`",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, self.lowered)

    def test_future_semantic_stages_remain_explicit(self):
        for future_surface in (
            "compatibility evaluation",
            "semantic ir/compiler",
            "runtime resolution",
            "corpus-specific mappings",
        ):
            with self.subTest(future_surface=future_surface):
                self.assertIn(future_surface, self.lowered)

    def test_source_checkout_install_is_documented(self):
        self.assertIn("python -m pip install -e .", self.readme)

    def test_examples_use_current_public_api_names(self):
        for public_name in (
            "load_and_validate",
            "canonical_json_bytes",
            "directory_component_digest",
            "parent_manifest_digest",
            "SemanticSourceBundle",
            "validate_semantic_bundle",
        ):
            with self.subTest(public_name=public_name):
                self.assertIn(public_name, self.readme)

    def test_unmerged_surfaces_are_not_claimed_as_implemented(self):
        for claim in (
            "semantic_search is implemented",
            "verified-compatible is implemented",
            "runtime resolution is implemented",
        ):
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.lowered)


if __name__ == "__main__":
    unittest.main()
