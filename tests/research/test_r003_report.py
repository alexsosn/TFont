from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-003-ergonomics.md"
RECONCILIATION = ROOT / "docs" / "research" / "R-003-reconciliation.md"


class R003AuthoritativeReportTests(unittest.TestCase):
    def test_accepted_research_dependencies_are_pinned(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("merge is blocked on independent acceptance of R-005", text)
        self.assertIn("R-005 accepted", text)
        self.assertIn("48c8bd78d0c3a0501b2fdec6946db5df90517bdb", text)
        self.assertIn("a9c4d74d4de2f9a15eb1464dce341ecd2f92f898", text)
        self.assertIn("R-001 accepted", text)
        self.assertIn("68b88a820f5519ad65d46b732679a6278e9ca3c9", text)
        self.assertIn("a22a95084a1518882d1e3e87d10e9757121f106d", text)
        self.assertIn("R-002 accepted", text)
        self.assertIn("d82e6ef2726f149f903eb43ddbfb615faf399cd5", text)
        self.assertIn("a554d4fdc36c8854519064f3a7611b80efa29622", text)

    def test_capability_examples_use_evidence_bearing_compatibility_states(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn('"compatibility": "verified"', text)
        self.assertIn("verified-exact", text)
        self.assertIn("verified-compatible", text)
        self.assertIn("unverified", text)
        self.assertIn("incompatible", text)
        self.assertIn("non-executable", text.lower())
        self.assertNotIn("allow_unverified", text)

    def test_parent_compatibility_is_component_aware(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("parent component manifest", text)
        self.assertIn("semantically addressable native component", text)
        self.assertIn("complete dependency closure", text)
        self.assertIn("changed component set", text)
        self.assertNotIn("parent schema/revision mismatch prevents normal semantic execution", text)
        self.assertNotIn("loaded corpus revision/schema does not match profile", text)

    def test_changed_parent_has_safe_executable_and_non_executable_branches(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("changed component set + complete dependency closure", text)
        self.assertIn("verified-compatible", text)
        self.assertIn("executable", text)
        self.assertIn("changed component set without complete validated dependency closure", text)
        self.assertIn("unverified", text)
        self.assertIn("incompatible", text)

    def test_r002_mapping_assessment_semantics_are_preserved(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertNotIn("selected `skos:closematch`-like relation", text)
        self.assertIn("`exact` — the external target and native/source concept are semantically coextensive", text)
        self.assertIn("`close` — the external target and native/source concept substantially overlap or are near-equivalent", text)
        self.assertIn("`broader` — the external target is broader than the native/source concept", text)
        self.assertIn("`narrower` — the external target is narrower than the native/source concept", text)
        self.assertIn("`related` — the external target is related but is not a substitute constraint", text)
        self.assertIn("`ambiguous` — evidence does not justify one unambiguous target assessment", text)
        self.assertIn("`native-only` — the native/source concept is intentionally supported without an external target", text)
        self.assertIn("`unsupported` — the active profile has no supported semantic projection", text)
        self.assertIn("mapping-level `exact` is distinct from parent compatibility `verified-exact`", text)

    def test_broader_and_narrower_query_effects_are_directionally_explicit(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("`broader` can under-cover the external request", text)
        self.assertIn("`narrower` can over-cover the external request", text)
        self.assertIn("no automatic widening", text)

    def test_mapping_assessment_is_separate_from_publication_relation(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("relation: exact", text)
        self.assertNotIn("mapping relation/strength", text.lower())
        self.assertIn("assessment: exact", text)
        self.assertIn("publication_relation: null", text)
        self.assertIn("mapping assessment", text.lower())
        self.assertIn("publication relation", text.lower())

    def test_no_target_and_ambiguity_states_fail_closed(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("`native-only` and `unsupported` have no external target", text)
        self.assertIn("`ambiguous` does not authorize automatic projection", text)
        self.assertIn("not executable", text)

    def test_component_aware_provenance_is_required(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("parent component manifest", text)
        self.assertIn("component identities", text)
        self.assertIn("dependency evidence", text)
        self.assertIn("ontology lock", text)
        self.assertIn("mapping assessment", text)

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

    def test_canonical_measurable_contract_contains_reconciliation_criteria(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertNotIn("forty concrete criteria", text)
        self.assertIn("different parent component set cannot become executable merely because feature names", text)
        self.assertIn("unverified profiles can be inspected but cannot be passed to normal semantic execution", text)
        self.assertIn("research-stage r-005 `s` classification alone cannot compile into an executable `exact` mapping", text)
        self.assertIn("empty-string/`none` dense tf records are excluded from semantic capability domains", text)
        self.assertIn("empty dense records do not expand a feature's advertised applicable node types", text)
        self.assertIn("empty native values cannot satisfy an explicit absence", text)

    def test_reconciliation_note_is_historical_not_competing_normative_source(self):
        text = RECONCILIATION.read_text(encoding="utf-8").lower()
        self.assertIn("historical reconciliation record", text)
        self.assertIn("canonical r-003 report is authoritative", text)
        self.assertNotIn("where this note conflicts", text)
        self.assertNotIn("loaded parent tf semantic bytes", text)


if __name__ == "__main__":
    unittest.main()
