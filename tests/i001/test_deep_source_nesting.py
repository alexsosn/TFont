from __future__ import annotations

import sys
import unittest

from tfont.source_validation import SourceValidationError, loads_source


def _deep_json(depth: int) -> str:
    return "[" * depth + "0" + "]" * depth


def _deep_yaml(depth: int) -> str:
    return "- " * depth + "0\n"


def _list_depth(value) -> tuple[int, object]:
    depth = 0
    current = value
    while type(current) is list and len(current) == 1:
        depth += 1
        current = current[0]
    return depth, current


class DeepSourceNestingTests(unittest.TestCase):
    def assert_deep_decode_error(self, text: str, *, format: str, source_name: str) -> None:
        try:
            loads_source(text, format=format, source_name=source_name)
        except Exception as exc:  # inspect the public boundary, including the pre-fix raw error
            self.assertIsInstance(exc, SourceValidationError)
            problem = exc.problem
            self.assertEqual(problem.category, "decode_error")
            self.assertEqual(problem.source_name, source_name)
            self.assertEqual(problem.instance_path, ())
            self.assertEqual(problem.schema_path, ())
            return
        self.fail("excessively deep source unexpectedly loaded without an error")

    def test_deep_json_does_not_leak_recursion_error(self):
        depth = sys.getrecursionlimit() + 100
        self.assert_deep_decode_error(
            _deep_json(depth),
            format="json",
            source_name="deep.json",
        )

    def test_deep_yaml_does_not_leak_recursion_error(self):
        depth = sys.getrecursionlimit() + 100
        self.assert_deep_decode_error(
            _deep_yaml(depth),
            format="yaml",
            source_name="deep.yaml",
        )

    def test_moderate_nested_json_and_yaml_still_load(self):
        depth = 32
        json_value = loads_source(_deep_json(depth), format="json")
        yaml_value = loads_source(_deep_yaml(depth), format="yaml")
        self.assertEqual(_list_depth(json_value), (depth, 0))
        self.assertEqual(_list_depth(yaml_value), (depth, 0))

    def test_existing_error_categories_are_not_broadened(self):
        cases = [
            ("json", '{"a": 1, "a": 2}', "duplicate_key"),
            ("yaml", "a: 1\na: 2\n", "duplicate_key"),
            ("json", '{"value": NaN}', "decode_error"),
            ("yaml", "value: .nan\n", "non_json_value"),
        ]
        for format, text, category in cases:
            with self.subTest(format=format, category=category):
                with self.assertRaises(SourceValidationError) as raised:
                    loads_source(text, format=format, source_name=f"control.{format}")
                self.assertEqual(raised.exception.problem.category, category)


if __name__ == "__main__":
    unittest.main()
