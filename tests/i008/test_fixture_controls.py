from __future__ import annotations

import unittest

from tests.i008._fixtures import compiled_executable_noun_ir
from tests.i006._fixtures import DEFAULT_CORPORA, noun_semantic_key


class I008FixtureControls(unittest.TestCase):
    def test_release_slice_compiles_with_explicit_value_predicate_shape(self):
        ir = compiled_executable_noun_ir()
        self.assertEqual(
            tuple(sorted(variant.key.corpus_id for variant in ir.variants)),
            tuple(sorted(DEFAULT_CORPORA)),
        )
        rows = dict(ir.semantic_index)[noun_semantic_key()]
        self.assertEqual(len(rows), 3)
        self.assertEqual({row.assessment for row in rows}, {"exact"})
        self.assertEqual(
            {row.native_execution_binding.execution_shape for row in rows},
            {"value-predicate"},
        )
        self.assertEqual(
            {(row.native_execution_binding.node_type, row.native_execution_binding.feature, row.native_execution_binding.value) for row in rows},
            {("word", "sp", "subs")},
        )


if __name__ == "__main__":
    unittest.main()
