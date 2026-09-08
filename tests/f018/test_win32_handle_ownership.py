from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import tfont.parent_identity as parent_identity
from tfont.parent_identity import IdentityError


@unittest.skipUnless(os.name == "nt", "Win32 ownership contract")
class Win32HandleOwnershipTests(unittest.TestCase):
    def assert_category(self, category: str, func, *args, **kwargs) -> IdentityError:
        with self.assertRaises(IdentityError) as raised:
            func(*args, **kwargs)
        self.assertEqual(raised.exception.problem.category, category)
        return raised.exception

    def helper(self):
        helper = getattr(parent_identity, "_open_trusted_file_descriptor", None)
        self.assertTrue(callable(helper), "trusted descriptor helper must exist")
        return helper

    def test_reparse_result_closes_raw_handle_once_without_conversion(self):
        helper = self.helper()
        with (
            patch.object(parent_identity, "_win32_create_file_handle", return_value=123, create=True),
            patch.object(parent_identity, "_win32_handle_is_reparse", return_value=True, create=True),
            patch.object(parent_identity, "_win32_close_handle", create=True) as close_handle,
            patch.object(parent_identity.msvcrt, "open_osfhandle") as conversion,
            patch.object(parent_identity.os, "read") as read_mock,
        ):
            self.assert_category("symlink_not_allowed", helper, r"C:\fake\link.bin")
        close_handle.assert_called_once_with(123)
        conversion.assert_not_called()
        read_mock.assert_not_called()

    def test_handle_query_failure_closes_raw_handle_once(self):
        helper = self.helper()
        with (
            patch.object(parent_identity, "_win32_create_file_handle", return_value=123, create=True),
            patch.object(parent_identity, "_win32_handle_is_reparse", side_effect=OSError("query failed"), create=True),
            patch.object(parent_identity, "_win32_close_handle", create=True) as close_handle,
            patch.object(parent_identity.msvcrt, "open_osfhandle") as conversion,
        ):
            self.assert_category("filesystem_error", helper, r"C:\fake\file.bin")
        close_handle.assert_called_once_with(123)
        conversion.assert_not_called()

    def test_conversion_failure_closes_raw_handle_once(self):
        helper = self.helper()
        with (
            patch.object(parent_identity, "_win32_create_file_handle", return_value=123, create=True),
            patch.object(parent_identity, "_win32_handle_is_reparse", return_value=False, create=True),
            patch.object(parent_identity, "_win32_close_handle", create=True) as close_handle,
            patch.object(parent_identity.msvcrt, "open_osfhandle", side_effect=OSError("conversion failed")),
        ):
            self.assert_category("filesystem_error", helper, r"C:\fake\file.bin")
        close_handle.assert_called_once_with(123)

    def test_conversion_success_transfers_ownership_and_sets_binary_mode(self):
        helper = self.helper()
        with (
            patch.object(parent_identity, "_win32_create_file_handle", return_value=123, create=True),
            patch.object(parent_identity, "_win32_handle_is_reparse", return_value=False, create=True),
            patch.object(parent_identity, "_win32_close_handle", create=True) as close_handle,
            patch.object(parent_identity.msvcrt, "open_osfhandle", return_value=456) as conversion,
            patch.object(parent_identity.msvcrt, "setmode", return_value=0) as setmode,
        ):
            descriptor = helper(r"C:\fake\file.bin")
        self.assertEqual(descriptor, 456)
        conversion.assert_called_once_with(123, os.O_RDONLY)
        setmode.assert_called_once_with(456, os.O_BINARY)
        close_handle.assert_not_called()

    def test_setmode_failure_closes_descriptor_not_raw_handle(self):
        helper = self.helper()
        with (
            patch.object(parent_identity, "_win32_create_file_handle", return_value=123, create=True),
            patch.object(parent_identity, "_win32_handle_is_reparse", return_value=False, create=True),
            patch.object(parent_identity, "_win32_close_handle", create=True) as close_handle,
            patch.object(parent_identity.msvcrt, "open_osfhandle", return_value=456),
            patch.object(parent_identity.msvcrt, "setmode", side_effect=OSError("setmode failed")),
            patch.object(parent_identity.os, "close") as close_fd,
        ):
            self.assert_category("filesystem_error", helper, r"C:\fake\file.bin")
        close_handle.assert_not_called()
        close_fd.assert_called_once_with(456)


if __name__ == "__main__":
    unittest.main()
