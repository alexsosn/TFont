from __future__ import annotations

import importlib
import unittest
from dataclasses import replace

from tests.i006._fixtures import compiled_noun_ir
from tests.i006.test_semantic_resolver_contract import prerequisite_for, request_for


RESOLVER = importlib.import_module("tfont.semantic_resolver")


class I006NestedVariantAuthorityRedTests(unittest.TestCase):
    def test_nested_variant_authority_types_fail_closed(self):
        ir = compiled_noun_ir(("bhsa",))
        variant = ir.variants[0]
        state = prerequisite_for(RESOLVER, variant)

        for field in ("key", "release_key", "release_signature"):
            with self.subTest(field=field):
                bad_variant = replace(variant, **{field: object()})
                bad_ir = replace(ir, variants=(bad_variant,))
                with self.assertRaises(RESOLVER.SemanticResolutionError) as raised:
                    RESOLVER.semantic_resolve(
                        bad_ir,
                        request_for(RESOLVER, ("bhsa",)),
                        (state,),
                    )
                self.assertEqual(
                    raised.exception.problem.category,
                    "invalid_compiled_ir",
                )


if __name__ == "__main__":
    unittest.main()
