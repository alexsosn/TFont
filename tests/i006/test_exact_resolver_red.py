from __future__ import annotations

import unittest

from tests.i005._fixtures import OLIA_NOUN, validated_noun_bundle
from tfont import SemanticKey, compile_semantic_ir
from tfont.semantic_resolver import (
    DependencyPrerequisiteResult,
    RuntimePrerequisiteState,
    SemanticResolveRequest,
    profile_release_fingerprint,
    semantic_resolve,
)


def compiled_three():
    return compile_semantic_ir(
        (
            validated_noun_bundle("bhsa", parent_char="a"),
            validated_noun_bundle("syriac", parent_char="b"),
            validated_noun_bundle("extrabiblical", parent_char="c"),
        )
    )


def prerequisite_for(variant):
    signature = variant.release_signature
    return RuntimePrerequisiteState(
        variant=variant.key,
        profile_release_fingerprint=profile_release_fingerprint(signature),
        observed_parent_manifest_digest=variant.key.expected_parent_manifest_digest,
        parent_state="verified-exact",
        dependency_results=tuple(
            DependencyPrerequisiteResult(
                dependency_id=dependency_id,
                result="pass",
                observed_evidence_digest=None,
                evaluator_rule_version="fixture-rule-v1",
            )
            for dependency_id, _ in signature.dependency_records
        ),
        active_ontology_bundle_digest=variant.key.ontology_bundle_digest,
        ontology_bundle_state=("verified" if variant.key.ontology_bundle_digest is not None else "not-required"),
        source_contract="manual-test-attestation-v1",
    )


class ExactResolverRedTests(unittest.TestCase):
    def test_exact_olia_noun_resolves_three_native_tf_plans(self):
        ir = compiled_three()
        prerequisites = tuple(prerequisite_for(variant) for variant in ir.variants)
        request = SemanticResolveRequest(
            key=SemanticKey(
                profile_id="linguistic",
                capability_id="linguistic.part-of-speech",
                target=OLIA_NOUN,
                formal_kind="class",
                semantic_role="annotation-value",
            ),
            corpora=("syriac", "bhsa", "extrabiblical"),
            semantic_mode="exact",
        )

        result = semantic_resolve(ir, request, prerequisites)

        self.assertEqual(tuple(plan.corpus_id for plan in result.plans), ("bhsa", "extrabiblical", "syriac"))
        self.assertEqual(result.request.corpora, ("bhsa", "extrabiblical", "syriac"))
        self.assertEqual(result.comparison_state, "exactly-comparable")
        self.assertEqual(result.losses, ())
        self.assertTrue(result.resolution_fingerprint.startswith("sha256:"))
        for plan in result.plans:
            self.assertEqual(plan.reference_kind, "semantic-pivot")
            self.assertEqual(plan.query_role, "semantic-constraint")
            self.assertEqual(plan.assessment, "exact")
            self.assertEqual(plan.semantic_mode, "exact")
            self.assertEqual(plan.capability_state, "active")
            self.assertEqual(plan.native_execution_binding.node_type, "word")
            self.assertEqual(plan.native_execution_binding.feature, "sp")
            self.assertEqual(plan.native_execution_binding.value, "subs")
            self.assertEqual(plan.prerequisite_source_contract, "manual-test-attestation-v1")
            self.assertTrue(plan.plan_fingerprint.startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
