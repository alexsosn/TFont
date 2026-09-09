from __future__ import annotations

import importlib
import unittest
from dataclasses import replace

from tests.i006._fixtures import compiled_noun_ir, with_bundle_digest
from tests.i006.test_semantic_resolver_contract import prerequisite_for, request_for


RESOLVER = importlib.import_module("tfont.semantic_resolver")


def assert_problem(testcase: unittest.TestCase, category: str, callable_, *args):
    with testcase.assertRaises(RESOLVER.SemanticResolutionError) as raised:
        callable_(*args)
    testcase.assertEqual(raised.exception.problem.category, category)


class I006AdversarialReviewContractTests(unittest.TestCase):
    def test_request_validation_precedes_malformed_ir_lookup(self):
        ir = compiled_noun_ir(("bhsa",))
        bad_ir = replace(ir, variants=(ir.variants[0], ir.variants[0]))
        bad_request = request_for(RESOLVER, ("bhsa",), semantic_mode="approximate")
        assert_problem(
            self,
            "unsupported_semantic_mode",
            RESOLVER.semantic_resolve,
            bad_ir,
            bad_request,
            (),
        )

    def test_verified_required_bundle_without_digest_is_invalid_prerequisite(self):
        ir = with_bundle_digest(
            compiled_noun_ir(("bhsa",)),
            "sha256:" + "6" * 64,
        )
        state = prerequisite_for(RESOLVER, ir.variants[0])
        state = replace(
            state,
            active_ontology_bundle_digest=None,
            ontology_bundle_state="verified",
        )
        assert_problem(
            self,
            "invalid_prerequisite",
            RESOLVER.semantic_resolve,
            ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_duplicate_stale_same_variant_is_invalid_before_freshness(self):
        ir = compiled_noun_ir(("bhsa",))
        state = prerequisite_for(RESOLVER, ir.variants[0])
        stale = replace(
            state,
            profile_release_fingerprint="sha256:" + "0" * 64,
        )
        assert_problem(
            self,
            "invalid_prerequisite",
            RESOLVER.semantic_resolve,
            ir,
            request_for(RESOLVER, ("bhsa",)),
            (stale, stale),
        )

    def test_variant_repeated_mapping_digests_must_match_release_signature(self):
        ir = compiled_noun_ir(("bhsa",))
        variant = ir.variants[0]
        bad_variant = replace(variant, mapping_digests=())
        bad_ir = replace(ir, variants=(bad_variant,))
        state = prerequisite_for(RESOLVER, bad_variant)
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_variant_repeated_ontology_locks_must_match_release_signature(self):
        ir = compiled_noun_ir(("bhsa",))
        variant = ir.variants[0]
        bad_variant = replace(variant, ontology_locks=())
        bad_ir = replace(ir, variants=(bad_variant,))
        state = prerequisite_for(RESOLVER, bad_variant)
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_variant_repeated_contract_fields_must_match_release_signature(self):
        ir = compiled_noun_ir(("bhsa",))
        variant = ir.variants[0]
        mutations = {
            "profile_schema_version": variant.profile_schema_version + 1,
            "profile_catalog_version": variant.profile_catalog_version + 1,
            "dependency_contract_version": variant.dependency_contract_version + 1,
            "mapping_schema_version": variant.mapping_schema_version + 1,
            "mapping_semantic_algorithm": variant.mapping_semantic_algorithm + "-forged",
            "projection_semantic_algorithm": variant.projection_semantic_algorithm + "-forged",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                bad_variant = replace(variant, **{field: value})
                bad_ir = replace(ir, variants=(bad_variant,))
                state = prerequisite_for(RESOLVER, bad_variant)
                assert_problem(
                    self,
                    "invalid_compiled_ir",
                    RESOLVER.semantic_resolve,
                    bad_ir,
                    request_for(RESOLVER, ("bhsa",)),
                    (state,),
                )

    def test_malformed_native_binding_steps_fail_through_compiled_ir_boundary(self):
        ir = compiled_noun_ir(("bhsa",))
        key, rows = ir.semantic_index[0]
        malformed_binding = replace(
            rows[0].native_execution_binding,
            steps=(object(),),
        )
        malformed_row = replace(rows[0], native_execution_binding=malformed_binding)
        bad_ir = replace(ir, semantic_index=((key, (malformed_row,)),))
        state = prerequisite_for(RESOLVER, bad_ir.variants[0])
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )


if __name__ == "__main__":
    unittest.main()
