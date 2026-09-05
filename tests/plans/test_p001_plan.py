from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs" / "plans" / "P-001-foundation-poc-design.md"


class P001FoundationDesignContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PLAN.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()

    def test_pins_all_accepted_foundation_dependencies(self):
        for value in (
            "48c8bd78d0c3a0501b2fdec6946db5df90517bdb",
            "a9c4d74d4de2f9a15eb1464dce341ecd2f92f898",
            "68b88a820f5519ad65d46b732679a6278e9ca3c9",
            "a22a95084a1518882d1e3e87d10e9757121f106d",
            "d82e6ef2726f149f903eb43ddbfb615faf399cd5",
            "a554d4fdc36c8854519064f3a7611b80efa29622",
            "6747379a4aa68c17c156344f3ed3b0c2cb29d423",
            "02abd89b5b7d4c83027e1e8503a02eef23cab91e",
            "3dcadc0b32aef95ecbf6ad94f6bbc062f8c6200f",
            "00a5d6b7de777074b01bb70ac425d7f187781298",
        ):
            self.assertIn(value, self.text)

    def test_artifact_flow_has_one_canonical_source_path(self):
        required = (
            "profile manifest",
            "parent component manifest",
            "ontology lock",
            "canonical mapping source",
            "normalized semantic ir",
            "runtime sidecar",
            "reference json",
            "publication output",
        )
        for phrase in required:
            self.assertIn(phrase, self.lower)
        self.assertIn("canonical source", self.lower)
        self.assertIn("generated derivative", self.lower)
        self.assertIn("deterministic", self.lower)

    def test_profile_manifest_contract_is_explicit(self):
        required = (
            "profile_id",
            "profile_version",
            "parent_component_manifest",
            "ontology_locks",
            "mapping_sources",
            "required_components",
        )
        for field in required:
            self.assertIn(f"`{field}`", self.text)

    def test_parent_component_manifest_is_component_aware(self):
        required = (
            "semantically addressable native component",
            "tf payload",
            "external/native sidecar",
            "catalogue",
            "zero-span",
            "native-adapter",
            "component identities",
            "complete dependency closure",
        )
        for phrase in required:
            self.assertIn(phrase, self.lower)
        self.assertIn("tf bytes stay identical", self.lower)
        self.assertIn("must not remain `verified-exact`", self.lower)

    def test_all_compatibility_states_and_execution_gate_are_defined(self):
        for state in ("verified-exact", "verified-compatible", "unverified", "incompatible"):
            self.assertIn(f"`{state}`", self.text)
        self.assertIn("only `verified-exact` and `verified-compatible` are executable", self.lower)
        self.assertIn("`unverified`", self.text)
        self.assertIn("non-executable", self.lower)

    def test_mapping_object_preserves_r002_contract(self):
        for assessment in (
            "exact",
            "close",
            "broader",
            "narrower",
            "related",
            "ambiguous",
            "native-only",
            "unsupported",
        ):
            self.assertRegex(self.text, rf"(?m)^\s*-?\s*`?{re.escape(assessment)}`?\b")
        required_fields = (
            "mapping_id",
            "profile_id",
            "native_selector",
            "native_dependencies",
            "external_target",
            "assessment",
            "publication_relation",
            "applicability",
            "evidence",
            "review",
            "ontology_lock",
        )
        for field in required_fields:
            self.assertIn(f"`{field}`", self.text)
        self.assertIn("native/source", self.lower)
        self.assertIn("external target", self.lower)
        self.assertIn("assessment and publication relation", self.lower)
        self.assertIn("independent", self.lower)

    def test_no_target_and_ambiguity_states_are_fail_closed(self):
        self.assertIn("`native-only` and `unsupported` have no external target", self.lower)
        self.assertIn("`ambiguous`", self.text)
        self.assertIn("must not", self.lower)
        self.assertIn("automatically executable", self.lower)

    def test_ambiguity_represents_target_and_relation_candidates(self):
        self.assertIn("candidate_projections", self.text)
        self.assertIn("assessment_candidate", self.text)
        self.assertIn("same external target", self.lower)
        self.assertIn("different candidate assessments", self.lower)
        self.assertIn("external_target: null", self.lower)

    def test_canonicalization_and_digest_rules_are_concrete(self):
        required = (
            "utf-8",
            "sorted",
            "canonical json",
            "sha-256",
            "line endings",
            "timestamps",
            "semantic digest",
            "source digest",
        )
        for phrase in required:
            self.assertIn(phrase, self.lower)
        self.assertIn("must not affect", self.lower)

    def test_semantic_digest_excludes_release_label_but_bundle_identity_includes_it(self):
        self.assertIn("profile_version must not affect `semantic_digest`", self.lower)
        self.assertIn("profile_id + profile_version + semantic_digest", self.lower)
        self.assertIn("exact-parent rebase", self.lower)
        self.assertIn("does not by itself require a major version", self.lower)

    def test_required_components_have_one_authority(self):
        self.assertIn("`required_components` is authoritative", self.lower)
        self.assertIn("component records do not carry an independent `required` flag", self.lower)
        self.assertIn("every active mapping dependency", self.lower)
        self.assertIn("must reference one of those components", self.lower)

    def test_review_is_bound_to_mapping_semantic_content(self):
        self.assertIn("mapping_semantic_digest", self.text)
        self.assertIn("reviewed_mapping_digest", self.text)
        self.assertIn("must match", self.lower)
        self.assertIn("review record itself", self.lower)
        self.assertIn("stale review", self.lower)
        self.assertIn("non-executable", self.lower)

    def test_ir_and_runtime_handoff_are_defined(self):
        required = (
            "capability",
            "resolution plan",
            "native_constraints",
            "compatibility",
            "assessment",
            "publication_relation",
            "provenance",
            "resolution fingerprint",
            "protocol-independent",
            "mcp session state",
        )
        for phrase in required:
            self.assertIn(phrase, self.lower)

    def test_native_data_edge_cases_are_explicit(self):
        required = (
            "zero-span",
            "technical anchor",
            "semantic extent",
            "dense tf empty",
            "observed small domain",
            "documented bounded",
            "explicit absence",
        )
        for phrase in required:
            self.assertIn(phrase, self.lower)

    def test_documentation_and_semantic_diff_contract_is_explicit(self):
        for phrase in (
            "native -> semantic",
            "semantic -> corpora",
            "mapping assessment changed",
            "publication relation changed",
            "native selector/path changed",
            "ontology lock",
            "parent compatibility evidence changed",
            "prose-only",
        ):
            self.assertIn(phrase, self.lower)

    def test_fixture_matrix_has_positive_and_adversarial_cases(self):
        for phrase in (
            "bhsa",
            "changed-parent",
            "zero-span",
            "technical-anchor",
            "dense-empty",
            "native-only",
            "unsupported",
        ):
            self.assertIn(phrase, self.lower)

    def test_plan_ends_with_dependency_ordered_implementation_decomposition(self):
        self.assertIn("implementation ticket decomposition", self.lower)
        ticket_ids = re.findall(r"`I-\d{3}`", self.text)
        self.assertGreaterEqual(len(set(ticket_ids)), 5)
        self.assertIn("dependency order", self.lower)
        self.assertIn("red", self.lower)
        self.assertIn("green", self.lower)
        self.assertIn("independent review", self.lower)

    def test_design_ticket_contains_no_production_artifacts(self):
        self.assertFalse((ROOT / "schemas").exists())
        self.assertFalse((ROOT / "profiles").exists())
        self.assertFalse((ROOT / "src").exists())


if __name__ == "__main__":
    unittest.main()
