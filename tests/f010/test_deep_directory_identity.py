from __future__ import annotations

import stat
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import tfont.parent_identity as parent_identity
from tfont.parent_identity import IdentityError, directory_component_digest


EMPTY_DIRECTORY_DIGEST = "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
VIRTUAL_ROOT = "virtual-root"


class FakeEntry:
    def __init__(self, *, name: str, path: str, mode: int, stat_error: OSError | None = None):
        self.name = name
        self.path = path
        self._mode = mode
        self._stat_error = stat_error

    def stat(self, *, follow_symlinks: bool = True):
        if follow_symlinks:
            raise AssertionError("F-010 must preserve follow_symlinks=False")
        if self._stat_error is not None:
            raise self._stat_error
        return SimpleNamespace(st_mode=self._mode, st_file_attributes=0)


class FakeScandir:
    def __init__(self, entries):
        self._entries = list(entries)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return iter(self._entries)


class VirtualDirectoryTree:
    def __init__(
        self,
        *,
        depth: int,
        terminal_mode: int | None = None,
        scandir_error_level: int | None = None,
        stat_error_level: int | None = None,
    ):
        self.depth = depth
        self.terminal_mode = terminal_mode
        self.scandir_error_level = scandir_error_level
        self.stat_error_level = stat_error_level

    def _level(self, path: str) -> int:
        if path == VIRTUAL_ROOT:
            return 0
        prefix = "virtual-directory-"
        if not path.startswith(prefix):
            raise AssertionError(f"unexpected virtual path: {path}")
        return int(path[len(prefix) :])

    def scandir(self, path: str):
        level = self._level(path)
        if self.scandir_error_level == level:
            raise OSError(f"scan failed at level {level}")
        if level >= self.depth:
            if self.terminal_mode is None:
                return FakeScandir([])
            return FakeScandir(
                [
                    FakeEntry(
                        name="terminal",
                        path=f"virtual-terminal-{level}",
                        mode=self.terminal_mode,
                    )
                ]
            )

        child_level = level + 1
        return FakeScandir(
            [
                FakeEntry(
                    name="d",
                    path=f"virtual-directory-{child_level}",
                    mode=stat.S_IFDIR,
                    stat_error=(
                        OSError(f"stat failed at level {child_level}")
                        if self.stat_error_level == child_level
                        else None
                    ),
                )
            ]
        )


class DeepDirectoryIdentityTests(unittest.TestCase):
    def digest_virtual(self, tree: VirtualDirectoryTree):
        with (
            patch.object(parent_identity, "_require_real_directory", return_value=None),
            patch.object(parent_identity.os, "scandir", side_effect=tree.scandir),
        ):
            return directory_component_digest(VIRTUAL_ROOT)

    def assert_category(self, category: str, tree: VirtualDirectoryTree) -> IdentityError:
        with self.assertRaises(IdentityError) as raised:
            self.digest_virtual(tree)
        self.assertEqual(raised.exception.problem.category, category)
        return raised.exception

    def test_hierarchy_deeper_than_interpreter_stack_hashes_without_raw_recursion(self):
        tree = VirtualDirectoryTree(depth=sys.getrecursionlimit() + 100)
        self.assertEqual(self.digest_virtual(tree), EMPTY_DIRECTORY_DIGEST)

    def test_nested_symlink_keeps_symlink_not_allowed(self):
        tree = VirtualDirectoryTree(depth=64, terminal_mode=stat.S_IFLNK)
        error = self.assert_category("symlink_not_allowed", tree)
        self.assertEqual(error.problem.path, "virtual-terminal-64")

    def test_nested_special_entry_keeps_unsupported_entry(self):
        tree = VirtualDirectoryTree(depth=64, terminal_mode=stat.S_IFIFO)
        error = self.assert_category("unsupported_entry", tree)
        self.assertEqual(error.problem.path, "virtual-terminal-64")

    def test_nested_scandir_failure_keeps_filesystem_error_and_child_path(self):
        tree = VirtualDirectoryTree(depth=64, scandir_error_level=32)
        error = self.assert_category("filesystem_error", tree)
        self.assertEqual(error.problem.path, "virtual-directory-32")

    def test_nested_stat_failure_keeps_filesystem_error_and_entry_path(self):
        tree = VirtualDirectoryTree(depth=64, stat_error_level=32)
        error = self.assert_category("filesystem_error", tree)
        self.assertEqual(error.problem.path, "virtual-directory-32")


if __name__ == "__main__":
    unittest.main()
