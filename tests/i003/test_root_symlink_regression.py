from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from tfont.parent_identity import IdentityError, directory_component_digest, tf_payload_digest


class RootSymlinkRegressionTests(unittest.TestCase):
    def assert_symlink_rejected(self, func, path) -> None:
        with self.assertRaises(IdentityError) as raised:
            func(path)
        self.assertEqual(raised.exception.problem.category, "symlink_not_allowed")

    def make_directory_symlink(self, root: Path, target: Path, name: str) -> Path:
        link = root / name
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlink creation unavailable: {exc}")
        return link

    def test_recursive_directory_root_symlink_rejected_with_trailing_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "target"
            target.mkdir()
            (target / "data.bin").write_bytes(b"payload")
            link = self.make_directory_symlink(base, target, "directory-link")

            self.assert_symlink_rejected(directory_component_digest, link)
            self.assert_symlink_rejected(directory_component_digest, str(link) + os.sep)

    def test_tf_root_symlink_rejected_with_trailing_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "tf-target"
            target.mkdir()
            (target / "otype.tf").write_bytes(b"@node\n1\tword\n")
            link = self.make_directory_symlink(base, target, "tf-link")

            self.assert_symlink_rejected(tf_payload_digest, link)
            self.assert_symlink_rejected(tf_payload_digest, str(link) + os.sep)


if __name__ == "__main__":
    unittest.main()
