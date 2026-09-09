from __future__ import annotations

import importlib
import unittest
from dataclasses import replace

from tests.i006._fixtures import compiled_noun_ir
from tests.i006.test_semantic_resolver_contract import prerequisite_for, request_for


RESOLVER = importlib.import_module("tfont.semantic_resolver")


def assert_problem(testcase: unittest.TestCase, category: str, callable_, *args):
    with testcase.assertRaises(RESOLVER.SemanticResolutionError) as raised:
        callable_(*args)
    testcase.assertEqual(raised.exception.problem.category, category)


class I006AdversarialIRContainmentTests(unittest.TestCase):
    def test_mutable_native_dependencies_cannot_enter_frozen_plan(self):
        ir = compiled_noun_ir(("bhsa",))
        key, rows = ir.semantic_index[0]
        forged_row = replace(
            rows[0],
            native_dependencies=list(rows[0].native_dependencies),
        )
        bad_ir = replace(ir, semantic_index=((key, (forged_row,)),))
        state = prerequisite_for(RESOLVER, bad_ir.variants[0])
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_mutable_evidence_cannot_enter_frozen_plan(self):
        ir = compiled_noun_ir(("bhsa",))
        key, rows = ir.semantic_index[0]
        forged_row = replace(
            rows[0],
            mapping_evidence=list(rows[0].mapping_evidence),
        )
        bad_ir = replace(ir, semantic_index=((key, (forged_row,)),))
        state = prerequisite_for(RESOLVER, bad_ir.variants[0])
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_malformed_evidence_element_is_invalid_compiled_ir(self):
        ir = compiled_noun_ir(("bhsa",))
        key, rows = ir.semantic_index[0]
        forged_row = replace(rows[0], mapping_evidence=(object(),))
        bad_ir = replace(ir, semantic_index=((key, (forged_row,)),))
        state = prerequisite_for(RESOLVER, bad_ir.variants[0])
        assert_problem(
            self,
            "invalid_compiled_ir",
            RESOLVER.semantic_resolve,
            bad_ir,
            request_for(RESOLVER, ("bhsa",)),
            (state,),
        )

    def test_malformed_bundle_requirement_is_invalid_compiled_ir(self):
        ir = compiled_noun_ir(("bhsa",))
        key, rows = ir.semantic_index[0]
        forged_row = replace(rows[0], ontology_bundle_requirement=object())
        bad_ir = replace(ir, semantic_index=((key, (forged_row,)),))
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
