from __future__ import annotations

from dataclasses import replace
import unittest

from tests.i006.test_exact_resolver_red import compiled_three, prerequisite_for
from tfont.semantic_ir import CapabilityFactsIR
from tfont.semantic_resolver import semantic_capabilities


class CapabilityDiscoveryTests(unittest.TestCase):
    def test_declared_capability_without_fact_is_reported_absent(self):
        ir = compiled_three()
        variant = next(item for item in ir.variants if item.key.corpus_id == "bhsa")
        prerequisite = prerequisite_for(variant)
        malformed = replace(
            ir,
            capability_facts=tuple(
                row for row in ir.capability_facts
                if not (
                    row[0].variant == variant.key
                    and row[0].profile_id == "linguistic"
                    and row[0].capability_id == "linguistic.part-of-speech"
                )
            ),
        )

        views = semantic_capabilities(malformed, (prerequisite,), corpora=("bhsa",))

        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual((view.profile_id, view.capability_id), ("linguistic", "linguistic.part-of-speech"))
        self.assertEqual(view.state, "absent")
        self.assertEqual(view.facts, CapabilityFactsIR(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ()))
        self.assertFalse(view.executable_exact)

    def test_positive_capability_with_unverified_parent_is_unavailable_not_executable(self):
        ir = compiled_three()
        variant = next(item for item in ir.variants if item.key.corpus_id == "bhsa")
        prerequisite = replace(prerequisite_for(variant), parent_state="unverified")

        views = semantic_capabilities(ir, (prerequisite,), corpora=("bhsa",))

        view = next(item for item in views if item.capability_id == "linguistic.part-of-speech")
        self.assertEqual(view.state, "unavailable")
        self.assertFalse(view.executable_exact)


if __name__ == "__main__":
    unittest.main()
