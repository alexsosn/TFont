from __future__ import annotations

from dataclasses import replace
import unittest

from tests.i005._fixtures import OLIA_NOUN
from tests.i006.test_exact_resolver_red import compiled_three, prerequisite_for
from tfont import CapabilityKey, SemanticKey
from tfont.semantic_resolver import (
    SemanticResolveRequest,
    SemanticResolutionError,
    profile_release_fingerprint,
    runtime_prerequisite_fingerprint,
    semantic_resolve,
)


def request(*, corpora=("bhsa",), mode="exact", capability="linguistic.part-of-speech"):
    return SemanticResolveRequest(
        key=SemanticKey(
            profile_id="linguistic",
            capability_id=capability,
            target=OLIA_NOUN,
            formal_kind="class",
            semantic_role="annotation-value",
        ),
        corpora=corpora,
        semantic_mode=mode,
    )


def bhsa_context():
    ir = compiled_three()
    variant = next(item for item in ir.variants if item.key.corpus_id == "bhsa")
    prerequisite = prerequisite_for(variant)
    return ir, variant, prerequisite


class ResolverFailClosedTests(unittest.TestCase):
    def assert_problem(self, category, ir, req, prerequisites):
        with self.assertRaises(SemanticResolutionError) as raised:
            semantic_resolve(ir, req, prerequisites)
        self.assertEqual(raised.exception.problem.category, category)
        return raised.exception.problem

    def test_unsupported_mode_fails_before_lookup(self):
        ir, _, prerequisite = bhsa_context()
        self.assert_problem("unsupported_semantic_mode", ir, request(mode="approximate"), (prerequisite,))

    def test_duplicate_corpus_selection_fails(self):
        ir, _, prerequisite = bhsa_context()
        self.assert_problem("invalid_corpus_selection", ir, request(corpora=("bhsa", "bhsa")), (prerequisite,))

    def test_missing_prerequisite_fails(self):
        ir, _, _ = bhsa_context()
        self.assert_problem("missing_prerequisite", ir, request(), ())

    def test_stale_profile_release_fingerprint_fails(self):
        ir, _, prerequisite = bhsa_context()
        stale = replace(prerequisite, profile_release_fingerprint="sha256:" + "0" * 64)
        self.assert_problem("stale_prerequisite", ir, request(), (stale,))

    def test_parent_unverified_fails(self):
        ir, _, prerequisite = bhsa_context()
        value = replace(prerequisite, parent_state="unverified")
        self.assert_problem("parent_unverified", ir, request(), (value,))

    def test_parent_incompatible_fails(self):
        ir, _, prerequisite = bhsa_context()
        value = replace(prerequisite, parent_state="incompatible")
        self.assert_problem("parent_incompatible", ir, request(), (value,))

    def test_dependency_failure_fails(self):
        ir, _, prerequisite = bhsa_context()
        dependency = replace(prerequisite.dependency_results[0], result="fail")
        value = replace(prerequisite, dependency_results=(dependency,))
        self.assert_problem("dependency_unavailable", ir, request(), (value,))

    def test_duplicate_exact_variant_prerequisite_fails_even_if_identical(self):
        ir, _, prerequisite = bhsa_context()
        self.assert_problem("invalid_prerequisite", ir, request(), (prerequisite, prerequisite))

    def test_empty_source_contract_fails(self):
        ir, _, prerequisite = bhsa_context()
        value = replace(prerequisite, source_contract="")
        self.assert_problem("invalid_prerequisite", ir, request(), (value,))

    def test_source_contract_changes_prerequisite_fingerprint(self):
        _, _, prerequisite = bhsa_context()
        other = replace(prerequisite, source_contract="other-attestation-v1")
        self.assertNotEqual(runtime_prerequisite_fingerprint(prerequisite), runtime_prerequisite_fingerprint(other))

    def test_capability_absent_fails(self):
        ir, _, prerequisite = bhsa_context()
        filtered = tuple(
            row for row in ir.capability_facts
            if not (row[0].variant.corpus_id == "bhsa" and row[0].profile_id == "linguistic" and row[0].capability_id == "linguistic.part-of-speech")
        )
        malformed = replace(ir, capability_facts=filtered)
        self.assert_problem("capability_absent", malformed, request(), (prerequisite,))

    def test_non_exact_only_binding_fails(self):
        ir, _, prerequisite = bhsa_context()
        rows = []
        for key, bindings in ir.semantic_index:
            changed = tuple(replace(item, assessment="close") if item.corpus_id == "bhsa" else item for item in bindings)
            rows.append((key, changed))
        malformed = replace(ir, semantic_index=tuple(rows))
        self.assert_problem("non_exact_mapping", malformed, request(), (prerequisite,))

    def test_multiple_exact_bindings_fail_without_implicit_composition(self):
        ir, _, prerequisite = bhsa_context()
        rows = []
        for key, bindings in ir.semantic_index:
            bhsa = tuple(item for item in bindings if item.corpus_id == "bhsa")
            rows.append((key, bindings + bhsa))
        malformed = replace(ir, semantic_index=tuple(rows))
        self.assert_problem("multiple_exact_bindings", malformed, request(), (prerequisite,))

    def test_duplicate_variant_key_in_public_ir_fails(self):
        ir, _, prerequisite = bhsa_context()
        malformed = replace(ir, variants=ir.variants + (ir.variants[0],))
        self.assert_problem("invalid_compiled_ir", malformed, request(), (prerequisite,))

    def test_duplicate_semantic_key_in_public_ir_fails(self):
        ir, _, prerequisite = bhsa_context()
        malformed = replace(ir, semantic_index=ir.semantic_index + (ir.semantic_index[0],))
        self.assert_problem("invalid_compiled_ir", malformed, request(), (prerequisite,))

    def test_duplicate_capability_key_in_public_ir_fails(self):
        ir, _, prerequisite = bhsa_context()
        malformed = replace(ir, capability_facts=ir.capability_facts + (ir.capability_facts[0],))
        self.assert_problem("invalid_compiled_ir", malformed, request(), (prerequisite,))

    def test_binding_not_anchored_in_release_mapping_digest_fails(self):
        ir, _, prerequisite = bhsa_context()
        rows = []
        for key, bindings in ir.semantic_index:
            changed = tuple(
                replace(item, mapping_semantic_digest="sha256:" + "9" * 64)
                if item.corpus_id == "bhsa" else item
                for item in bindings
            )
            rows.append((key, changed))
        malformed = replace(ir, semantic_index=tuple(rows))
        self.assert_problem("invalid_compiled_ir", malformed, request(), (prerequisite,))


if __name__ == "__main__":
    unittest.main()
