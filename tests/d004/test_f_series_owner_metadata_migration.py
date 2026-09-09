from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_RE = re.compile(r"^\*\*Issue:\*\*\s+#(\d+)\s*$")

MIGRATION = {
    "docs/research/F-012-file-hash-object-binding.md": (
        "80",
        "# F-012 research — bind file hashing to the inspected filesystem object",
    ),
    "docs/research/F-014-windows-exact-file-paths.md": (
        "84",
        "# F-014 research — portable exact-file path spelling boundary",
    ),
    "docs/research/F-016-custom-schema-recursion-boundary.md": (
        "88",
        "# F-016 research — custom schema recursion failure boundary",
    ),
    "docs/research/F-017-inplace-file-mutation.md": (
        "91",
        "# F-017 research — in-place mutation during identity hashing",
    ),
}


def owner_numbers(text: str) -> list[str]:
    return [match.group(1) for line in text.splitlines() if (match := OWNER_RE.fullmatch(line))]


class D004OwnerMetadataMigrationTests(unittest.TestCase):
    def test_migration_set_is_exact_and_has_distinct_owners(self):
        self.assertEqual(len(MIGRATION), 4)
        self.assertEqual({owner for owner, _ in MIGRATION.values()}, {"80", "84", "88", "91"})
        self.assertNotIn("docs/research/F-019-cpython-path-conversion-evidence.md", MIGRATION)

    def test_each_migration_target_has_exact_expected_owner_and_preserved_title(self):
        for relative_path, (expected_owner, expected_title) in MIGRATION.items():
            with self.subTest(path=relative_path):
                text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertEqual(text.splitlines()[0], expected_title)
                self.assertEqual(owner_numbers(text), [expected_owner])

    def test_neighboring_owned_primary_report_is_control(self):
        relative_path = "docs/research/F-013-directory-handle-binding.md"
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        self.assertEqual(owner_numbers(text), ["81"])
        self.assertNotIn(relative_path, MIGRATION)

    def test_f019_supporting_evidence_note_remains_non_owner_bearing(self):
        relative_path = "docs/research/F-019-cpython-path-conversion-evidence.md"
        text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# F-019 evidence note"))
        self.assertEqual(owner_numbers(text), [])
        self.assertNotIn(relative_path, MIGRATION)


if __name__ == "__main__":
    unittest.main()
