from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tfont.parent_identity as parent_identity
from tfont.parent_identity import IdentityError, file_component_digest


class HandleBoundFileReadTests(unittest.TestCase):
    def assert_category(self, category: str, func, *args, **kwargs) -> IdentityError:
        with self.assertRaises(IdentityError) as raised:
            func(*args, **kwargs)
        self.assertEqual(raised.exception.problem.category, category)
        return raised.exception

    def make_symlink(self, link: Path, target: Path) -> None:
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

    def test_trusted_descriptor_helpers_exist(self):
        self.assertTrue(callable(getattr(parent_identity, "_open_trusted_file_descriptor", None)))
        self.assertTrue(callable(getattr(parent_identity, "_sha256_descriptor", None)))

    @unittest.skipIf(os.name == "nt", "POSIX no-follow contract")
    def test_posix_zero_nofollow_fails_closed_without_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.bin"
            path.write_bytes(b"payload")
            with (
                patch.object(parent_identity.os, "O_NOFOLLOW", 0, create=True),
                patch.object(parent_identity.os, "read") as read_mock,
            ):
                exc = self.assert_category("filesystem_error", file_component_digest, path)
            read_mock.assert_not_called()
            self.assertEqual(exc.problem.path, str(path))

    def test_post_inspection_link_replacement_is_rejected_by_trusted_open_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            victim = base / "component.bin"
            target = base / "target.bin"
            victim.write_bytes(b"original")
            target.write_bytes(b"target")

            probe = base / "probe-link"
            self.make_symlink(probe, target)
            probe.unlink()

            real_lstat = parent_identity._lstat
            fired = False

            def raced_lstat(path: str):
                nonlocal fired
                st = real_lstat(path)
                if not fired and path == str(victim):
                    fired = True
                    victim.unlink()
                    victim.symlink_to(target)
                return st

            with (
                patch.object(parent_identity, "_lstat", side_effect=raced_lstat),
                patch.object(parent_identity.os, "read") as read_mock,
            ):
                exc = self.assert_category("symlink_not_allowed", file_component_digest, victim)

            self.assertTrue(fired)
            read_mock.assert_not_called()
            self.assertEqual(exc.problem.path, str(victim))

    def test_replacing_path_after_trusted_acquisition_does_not_redirect_reads(self):
        helper = getattr(parent_identity, "_open_trusted_file_descriptor", None)
        self.assertTrue(callable(helper), "trusted opener is required before continuity can be tested")

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            victim = base / "component.bin"
            replacement = base / "replacement.bin"
            original_bytes = b"original-open-object"
            victim.write_bytes(original_bytes)
            replacement.write_bytes(b"replacement-path-object")

            real_helper = helper
            fired = False

            def acquire_then_replace(path: str):
                nonlocal fired
                fd = real_helper(path)
                if not fired:
                    fired = True
                    os.replace(replacement, victim)
                return fd

            with patch.object(parent_identity, "_open_trusted_file_descriptor", side_effect=acquire_then_replace):
                digest = file_component_digest(victim)

            self.assertTrue(fired)
            expected = "sha256:" + hashlib.sha256(original_bytes).hexdigest()
            self.assertEqual(digest, expected)

    def test_descriptor_hashing_never_reopens_path(self):
        descriptor_hasher = getattr(parent_identity, "_sha256_descriptor", None)
        self.assertTrue(callable(descriptor_hasher), "descriptor hashing helper is required")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.bin"
            payload = b"descriptor-only"
            path.write_bytes(payload)
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
            try:
                with patch.object(parent_identity.os, "open", side_effect=AssertionError("pathname reopen")):
                    digest = descriptor_hasher(fd, str(path))
            finally:
                os.close(fd)

            self.assertEqual(digest, "sha256:" + hashlib.sha256(payload).hexdigest())

    @unittest.skipUnless(os.name == "nt", "Windows real-handle contract")
    def test_windows_real_file_uses_open_osfhandle_and_binary_mode_before_read(self):
        import msvcrt

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.bin"
            payload = b"windows-handle-path\r\n\x00"
            path.write_bytes(payload)

            self.assertTrue(hasattr(parent_identity, "msvcrt"), "parent_identity must expose its stdlib msvcrt bridge")
            mode_set = False
            real_open_osfhandle = msvcrt.open_osfhandle
            real_setmode = msvcrt.setmode
            real_read = os.read

            def tracked_open_osfhandle(handle, flags):
                return real_open_osfhandle(handle, flags)

            def tracked_setmode(fd, flags):
                nonlocal mode_set
                result = real_setmode(fd, flags)
                if flags == os.O_BINARY:
                    mode_set = True
                return result

            def tracked_read(fd, size):
                self.assertTrue(mode_set, "binary mode must be set before the first digest read")
                return real_read(fd, size)

            with (
                patch.object(parent_identity.msvcrt, "open_osfhandle", side_effect=tracked_open_osfhandle) as conversion,
                patch.object(parent_identity.msvcrt, "setmode", side_effect=tracked_setmode) as setmode_mock,
                patch.object(parent_identity.os, "read", side_effect=tracked_read),
            ):
                digest = file_component_digest(path)

            self.assertGreater(conversion.call_count, 0)
            self.assertGreater(setmode_mock.call_count, 0)
            self.assertEqual(digest, "sha256:" + hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    unittest.main()
