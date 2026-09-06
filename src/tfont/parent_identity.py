from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from typing import Any

from .digests import DigestError, canonical_json_bytes

FILE_BYTES_ALGORITHM = "tfont-file-bytes-sha256-v1"
DIRECTORY_FILES_ALGORITHM = "tfont-directory-files-sha256-v1"
TF_FILES_ALGORITHM = "tfont-tf-files-sha256-v1"
PARENT_COMPONENTS_ALGORITHM = "tfont-parent-components-sha256-v1"


@dataclass(frozen=True)
class IdentityProblem:
    category: str
    message: str
    path: str | None = None


class IdentityError(ValueError):
    def __init__(self, problem: IdentityProblem):
        self.problem = problem
        super().__init__(f"{problem.category}: {problem.message}")


def _fail(category: str, message: str, path: str | None = None) -> None:
    raise IdentityError(IdentityProblem(category=category, message=message, path=path))


def _path_string(value: str | os.PathLike[str]) -> str:
    try:
        path = os.fspath(value)
    except TypeError as exc:
        _fail("filesystem_error", f"path is not path-like: {exc}")
    if type(path) is not str:
        _fail("filesystem_error", "path must resolve to an exact string")
    return path


def _lstat(path: str) -> os.stat_result:
    try:
        return os.lstat(path)
    except FileNotFoundError:
        _fail("missing_path", "component path does not exist", path)
    except OSError as exc:
        _fail("filesystem_error", str(exc), path)


def _is_link_like(st: os.stat_result) -> bool:
    if stat.S_ISLNK(st.st_mode):
        return True
    attributes = getattr(st, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _require_real_directory(path: str) -> None:
    st = _lstat(path)
    if _is_link_like(st):
        _fail("symlink_not_allowed", "link-like component root is not allowed", path)
    if not stat.S_ISDIR(st.st_mode):
        _fail("wrong_path_type", "component root must be a directory", path)


def _sha256_bytes(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        _fail("filesystem_error", str(exc), path)
    return f"sha256:{digest.hexdigest()}"


def _validate_segment(segment: str, *, filesystem_path: str) -> str:
    if type(segment) is not str or not segment or segment in {".", ".."}:
        _fail("invalid_logical_path", "invalid component-relative path segment", filesystem_path)
    if "/" in segment or "\\" in segment:
        _fail("invalid_logical_path", "logical path segment contains a non-portable separator", filesystem_path)
    try:
        segment.encode("utf-8")
    except UnicodeEncodeError as exc:
        _fail("unicode_domain", str(exc), filesystem_path)
    return segment


def _utf16_key(value: str) -> bytes:
    try:
        return value.encode("utf-16be")
    except UnicodeEncodeError as exc:
        _fail("unicode_domain", str(exc))


def _file_record(relative_logical_path: str, filesystem_path: str) -> dict[str, str]:
    return {
        "relative_logical_path": relative_logical_path,
        "sha256": _sha256_file(filesystem_path),
    }


def _hash_file_records(records: list[dict[str, str]]) -> str:
    records.sort(key=lambda record: _utf16_key(record["relative_logical_path"]))
    try:
        encoded = canonical_json_bytes(records)
    except DigestError as exc:
        category = "unicode_domain" if exc.problem.category == "unicode_domain" else "projection_error"
        _fail(category, exc.problem.message)
    return _sha256_bytes(encoded)


def file_component_digest(path: str | os.PathLike[str]) -> str:
    filesystem_path = _path_string(path)
    st = _lstat(filesystem_path)
    if _is_link_like(st):
        _fail("symlink_not_allowed", "link-like file component is not allowed", filesystem_path)
    if not stat.S_ISREG(st.st_mode):
        _fail("wrong_path_type", "file component must be a regular file", filesystem_path)
    return _sha256_file(filesystem_path)


def directory_component_digest(path: str | os.PathLike[str]) -> str:
    root = _path_string(path)
    _require_real_directory(root)
    records: list[dict[str, str]] = []

    def walk(directory: str, relative_segments: tuple[str, ...]) -> None:
        try:
            with os.scandir(directory) as entries:
                current = list(entries)
        except OSError as exc:
            _fail("filesystem_error", str(exc), directory)

        for entry in current:
            entry_path = entry.path
            segment = _validate_segment(entry.name, filesystem_path=entry_path)
            try:
                st = entry.stat(follow_symlinks=False)
            except OSError as exc:
                _fail("filesystem_error", str(exc), entry_path)
            if _is_link_like(st):
                _fail("symlink_not_allowed", "link-like entry is not allowed", entry_path)

            segments = relative_segments + (segment,)
            if stat.S_ISDIR(st.st_mode):
                walk(entry_path, segments)
            elif stat.S_ISREG(st.st_mode):
                logical_path = "/".join(segments)
                records.append(_file_record(logical_path, entry_path))
            else:
                _fail("unsupported_entry", "addressed directory contains a non-file/non-directory entry", entry_path)

    walk(root, ())
    return _hash_file_records(records)


def tf_payload_digest(path: str | os.PathLike[str]) -> str:
    root = _path_string(path)
    _require_real_directory(root)
    records: list[dict[str, str]] = []

    try:
        with os.scandir(root) as entries:
            current = list(entries)
    except OSError as exc:
        _fail("filesystem_error", str(exc), root)

    for entry in current:
        if not entry.name.endswith(".tf"):
            continue
        entry_path = entry.path
        logical_path = _validate_segment(entry.name, filesystem_path=entry_path)
        try:
            st = entry.stat(follow_symlinks=False)
        except OSError as exc:
            _fail("filesystem_error", str(exc), entry_path)
        if _is_link_like(st):
            _fail("symlink_not_allowed", "selected TF entry is link-like", entry_path)
        if stat.S_ISREG(st.st_mode):
            records.append(_file_record(logical_path, entry_path))

    if not records:
        _fail("empty_component", "TF payload contains no direct regular .tf files", root)
    return _hash_file_records(records)


def _require_nonempty_string(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        _fail("projection_error", f"{field} must be a non-empty exact string")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        _fail("unicode_domain", str(exc))
    return value


def parent_manifest_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    if type(manifest) is not dict:
        _fail("projection_error", "parent manifest must be an exact object")
    allowed_top = {"algorithm", "components"}
    unknown_top = sorted(manifest.keys() - allowed_top) if all(type(key) is str for key in manifest) else []
    if any(type(key) is not str for key in manifest):
        _fail("projection_error", "parent manifest keys must be exact strings")
    if unknown_top:
        _fail("projection_error", f"unknown parent manifest fields: {', '.join(unknown_top)}")
    missing_top = sorted(allowed_top - manifest.keys())
    if missing_top:
        _fail("projection_error", f"missing parent manifest fields: {', '.join(missing_top)}")
    if manifest["algorithm"] != PARENT_COMPONENTS_ALGORITHM:
        _fail("projection_error", f"algorithm must be {PARENT_COMPONENTS_ALGORITHM}")

    source_components = manifest["components"]
    if type(source_components) is not list or not source_components:
        _fail("projection_error", "components must be a non-empty exact list")

    required = {"component_id", "kind", "identity_algorithm", "content_digest"}
    optional = {"logical_locator", "license_ref"}
    result: list[dict[str, str]] = []
    seen: set[str] = set()

    for index, source in enumerate(source_components):
        if type(source) is not dict:
            _fail("projection_error", f"components[{index}] must be an exact object")
        if any(type(key) is not str for key in source):
            _fail("projection_error", f"components[{index}] keys must be exact strings")
        missing = sorted(required - source.keys())
        if missing:
            _fail("projection_error", f"components[{index}] missing fields: {', '.join(missing)}")
        unknown = sorted(source.keys() - required - optional)
        if unknown:
            _fail("projection_error", f"components[{index}] unknown fields: {', '.join(unknown)}")

        component_id = _require_nonempty_string(source["component_id"], field=f"components[{index}].component_id")
        if component_id in seen:
            _fail("projection_error", f"duplicate component_id: {component_id}")
        seen.add(component_id)

        for field in optional:
            if field in source:
                _require_nonempty_string(source[field], field=f"components[{index}].{field}")

        result.append(
            {
                "component_id": component_id,
                "kind": _require_nonempty_string(source["kind"], field=f"components[{index}].kind"),
                "identity_algorithm": _require_nonempty_string(
                    source["identity_algorithm"], field=f"components[{index}].identity_algorithm"
                ),
                "content_digest": _require_nonempty_string(
                    source["content_digest"], field=f"components[{index}].content_digest"
                ),
            }
        )

    result.sort(key=lambda component: _utf16_key(component["component_id"]))
    return {"components": result}


def parent_manifest_digest(manifest: dict[str, Any]) -> str:
    projection = parent_manifest_projection(manifest)
    try:
        encoded = canonical_json_bytes(projection)
    except DigestError as exc:
        category = "unicode_domain" if exc.problem.category == "unicode_domain" else "projection_error"
        _fail(category, exc.problem.message)
    return _sha256_bytes(encoded)
