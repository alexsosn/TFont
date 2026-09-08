from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tfont.parent_identity as parent_identity
from tfont.parent_identity import IdentityError, directory_component_digest, file_component_digest, tf_payload_digest


FILE_ALPHA_DIGEST = "sha256:b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060"
EMPTY_DIRECTORY_DIGEST = "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"


class ExactFileSpellingTests(unittest.TestCase):
    def assert_wrong_path_before_lstat(self, spelling: str) -> None:
        with patch.object(parent_identity, "_lstat") as lstat_mock:
            with self.assertRaises(IdentityError) as raised:
                file_component_digest(spelling)
        self.assertEqual(raised.exception.problem.category, "wrong_path_type")
        self.assertEqual(raised.exception.problem.path, spelling)
        lstat_mock.assert_not_called()

    def test_terminal_native_separator_is_rejected_before_filesystem_normalization(self):
        self.assert_wrong_path_before_lstat("component.bin" + os.sep)
        self.assert_wrong_path_before_lstat("component.bin" + os.sep * 2)

    def test_terminal_dot_segment_is_rejected_before_filesystem_normalization(self):
        self.assert_wrong_path_before_lstat("component.bin" + os.sep + ".")
        self.assert_wrong_path_before_lstat("component.bin" + os.sep + "." + os.sep)
        self.assert_wrong_path_before_lstat("component.bin" + os.sep + "." + os.sep * 2)

    def test_ordinary_dotted_file_names_are_not_lexically_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name in ("a.", ".hidden", "a.b"):
                path = base / name
                path.write_bytes(b"alpha\n")
                self.assertEqual(file_component_digest(path), FILE_ALPHA_DIGEST)

    def test_plain_exact_file_digest_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.bin"
            path.write_bytes(b"alpha\n")
            self.assertEqual(file_component_digest(path), FILE_ALPHA_DIGEST)

    def test_directory_root_equivalent_spellings_remain_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "directory"
            root.mkdir()
            expected = directory_component_digest(root)
            self.assertEqual(expected, EMPTY_DIRECTORY_DIGEST)
            self.assertEqual(directory_component_digest(str(root) + os.sep), expected)
            self.assertEqual(directory_component_digest(str(root) + os.sep + "."), expected)

    def test_tf_root_equivalent_spellings_remain_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tf"
            root.mkdir()
            (root / "otype.tf").write_bytes(b"@node\n1\tword\n")
            expected = tf_payload_digest(root)
            self.assertEqual(tf_payload_digest(str(root) + os.sep), expected)
            self.assertEqual(tf_payload_digest(str(root) + os.sep + "."), expected)

    def test_embedded_nul_keeps_filesystem_error(self):
        spelling = "component\x00.bin"
        with self.assertRaises(IdentityError) as raised:
            file_component_digest(spelling)
        self.assertEqual(raised.exception.problem.category, "filesystem_error")
        self.assertEqual(raised.exception.problem.path, spelling)


if __name__ == "__main__":
    unittest.main()
