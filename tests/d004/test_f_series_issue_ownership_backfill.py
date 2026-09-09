from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "docs" / "research"

FILENAME_RE = re.compile(r"^(F-[0-9]{3})-.*\.md$")
ISSUE_RE = re.compile(r"^\*\*Issue:\*\* #([1-9][0-9]*)\s*$")

EXPECTED_BACKFILLS = {
    "F-012-file-hash-object-binding.md": 80,
    "F-014-windows-exact-file-paths.md": 84,
    "F-016-custom-schema-recursion-boundary.md": 88,
    "F-017-inplace-file-mutation.md": 91,
    "F-019-cpython-path-conversion-evidence.md": 94,
}


def parse_header_owners(text: str) -> list[int]:
    owners: list[int] = []
    for index, line in enumerate(text.splitlines()[:12]):
        if index == 0:
            continue
        if line.startswith("## "):
            break
        match = ISSUE_RE.fullmatch(line)
        if match:
            owners.append(int(match.group(1)))
    return owners


def scan_f_series() -> dict[str, tuple[str, list[int]]]:
    result: dict[str, tuple[str, list[int]]] = {}
    for path in sorted(RESEARCH_DIR.glob("F-[0-9][0-9][0-9]-*.md")):
        match = FILENAME_RE.fullmatch(path.name)
        if match is None:
            continue
        result[path.name] = (
            match.group(1),
            parse_header_owners(path.read_text(encoding="utf-8")),
        )
    return result


def conflicting_feature_owners(
    records: dict[str, tuple[str, list[int]]],
) -> dict[str, list[int]]:
    by_feature: dict[str, set[int]] = {}
    for feature, owners in records.values():
        if len(owners) == 1:
            by_feature.setdefault(feature, set()).add(owners[0])
    return {
        feature: sorted(owners)
        for feature, owners in sorted(by_feature.items())
        if len(owners) > 1
    }


class OwnershipParserControls(unittest.TestCase):
    def test_owner_is_read_only_from_bounded_header_region(self):
        text = (
            "# F-900 fixture\n\n"
            "**Issue:** #123  \n\n"
            "## Body\n\n"
            "**Issue:** #999\n"
        )
        self.assertEqual(parse_header_owners(text), [123])

    def test_body_issue_mention_does_not_count_as_owner(self):
        text = "# F-900 fixture\n\n## Body\n\nRelated to issue #123.\n"
        self.assertEqual(parse_header_owners(text), [])

    def test_duplicate_header_owners_are_visible_for_rejection(self):
        text = "# F-900 fixture\n\n**Issue:** #123\n**Issue:** #123\n\n## Body\n"
        self.assertEqual(parse_header_owners(text), [123, 123])

    def test_header_scan_is_hard_bounded(self):
        lines = ["# F-900 fixture"] + [""] * 11 + ["**Issue:** #123"]
        self.assertEqual(parse_header_owners("\n".join(lines)), [])

    def test_same_feature_same_owner_multi_artifact_is_not_a_conflict(self):
        records = {
            "F-900-primary.md": ("F-900", [123]),
            "F-900-evidence.md": ("F-900", [123]),
        }
        self.assertEqual(conflicting_feature_owners(records), {})

    def test_same_feature_different_owners_is_a_conflict(self):
        records = {
            "F-900-primary.md": ("F-900", [123]),
            "F-900-evidence.md": ("F-900", [456]),
        }
        self.assertEqual(conflicting_feature_owners(records), {"F-900": [123, 456]})


class RepositoryOwnershipREDTests(unittest.TestCase):
    def setUp(self):
        self.records = scan_f_series()

    def test_no_unexpected_missing_owner_artifacts(self):
        missing = {
            name for name, (_feature, owners) in self.records.items() if not owners
        }
        self.assertEqual(missing - set(EXPECTED_BACKFILLS), set())

    def test_no_duplicate_owner_headers(self):
        duplicates = sorted(
            name for name, (_feature, owners) in self.records.items() if len(owners) > 1
        )
        self.assertEqual(duplicates, [])

    def test_current_declared_feature_owners_do_not_conflict(self):
        self.assertEqual(conflicting_feature_owners(self.records), {})

    def test_every_f_series_research_artifact_has_one_owner(self):
        missing = sorted(
            name for name, (_feature, owners) in self.records.items() if len(owners) == 0
        )
        self.assertEqual(missing, [], f"missing F-series issue owners: {missing}")

    def test_backfill_targets_have_authoritative_expected_owners(self):
        for name, expected_owner in sorted(EXPECTED_BACKFILLS.items()):
            with self.subTest(path=name):
                self.assertIn(name, self.records)
                self.assertEqual(self.records[name][1], [expected_owner])


if __name__ == "__main__":
    unittest.main()
