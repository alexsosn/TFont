from __future__ import annotations

import io
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.d006 import test_downstream_ownership_migration as d006

ROOT = Path(__file__).resolve().parents[2]
F_TEST_RE = re.compile(r"^f[0-9]{3}$")


def copy_ownership_tree(destination: Path) -> None:
    shutil.copytree(ROOT / "docs" / "research", destination / "docs" / "research")
    shutil.copytree(ROOT / "docs" / "plans", destination / "docs" / "plans")
    shutil.copytree(ROOT / ".github" / "workflows", destination / ".github" / "workflows")

    tests_dst = destination / "tests"
    tests_dst.mkdir(parents=True)
    for package in sorted((ROOT / "tests").iterdir()):
        if not package.is_dir() or F_TEST_RE.fullmatch(package.name) is None:
            continue
        target = tests_dst / package.name
        target.mkdir()
        sidecar = package / "issue-owner.txt"
        if sidecar.is_file():
            shutil.copy2(sidecar, target / "issue-owner.txt")


class D006ForwardExtensibilityREDTests(unittest.TestCase):
    def test_future_valid_research_only_feature_does_not_break_d006(self):
        original_root = d006.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_ownership_tree(root)
            (root / "docs" / "research" / "F-999-future-research-only.md").write_text(
                "# F-999 future research-only\n\n"
                "**Issue:** #999\n\n"
                "## Scope\n\n"
                "Fixture for forward-extensibility regression.\n",
                encoding="utf-8",
            )

            stream = io.StringIO()
            with mock.patch.object(d006, "ROOT", root):
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(
                    d006.RepositoryMigrationREDTests
                )
                result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)

        self.assertEqual(d006.ROOT, original_root)
        self.assertTrue(result.wasSuccessful(), stream.getvalue())


if __name__ == "__main__":
    unittest.main()
