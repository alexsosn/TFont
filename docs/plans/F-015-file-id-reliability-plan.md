# F-015 implementation plan — handle-bound exact-file inspection

**Issue:** #90  
**Research:** `docs/research/F-015-file-id-reliability.md`

## 1. Goal

Strengthen the byte-reading boundary for every regular file that contributes to a TFont parent-component digest.

The authoritative invariant is:

> the same trusted no-follow descriptor/Win32 handle that passes final-object link/reparse and type inspection is the object from which every digest byte is read.

Retain the existing expected-stat versus opened-object `(st_dev, st_ino)` comparison as defense in depth:

- mismatch always fails closed;
- equality never authorizes exact continuity;
- the retained open descriptor/handle is the continuity authority from trusted-open inspection through hashing.

Do not claim a pathname snapshot before the trusted open, stable identity across process lifetime, ancestor-directory binding, or in-place mutation detection.

## 2. Public compatibility contract

No public function signatures or digest algorithm identifiers change:

- `file_component_digest(path)`;
- `directory_component_digest(path)`;
- `tf_payload_digest(path)`;
- `FILE_BYTES_ALGORITHM = tfont-file-bytes-sha256-v1`;
- `DIRECTORY_FILES_ALGORITHM = tfont-directory-files-sha256-v1`;
- `TF_FILES_ALGORITHM = tfont-tf-files-sha256-v1`.

Existing fixed digest vectors must remain byte-identical.

Preserve public error categories:

- final link/reparse detected by the trusted-open path -> `symlink_not_allowed`;
- standalone non-regular file -> existing `wrong_path_type` caller behavior;
- trusted-open, descriptor conversion, handle query, binary mode, fstat, mismatch, read, or unsupported no-follow primitive -> `filesystem_error` unless an existing caller contract already requires a more specific category;
- recursive unsupported object types remain `unsupported_entry` where applicable.

F-014 lexical path portability remains before filesystem inspection for standalone files.

## 3. Internal helper boundary

Replace pathname-reopening hash logic with one private descriptor-returning opener plus one descriptor-reading helper.

Target internal shape, names may differ only if RED pins equivalent behavior:

```python
def _open_trusted_file_descriptor(path: str) -> int:
    """Return an owned binary read descriptor for the final object without following a final link/reparse point."""


def _sha256_descriptor(fd: int, path: str) -> str:
    """Read digest bytes from an already-authorized descriptor; never reopen path."""


def _sha256_file(path: str, expected: os.stat_result) -> str:
    fd = _open_trusted_file_descriptor(path)
    try:
        opened = os.fstat(fd)
        require regular-file type
        fail if opened identity != expected identity
        return _sha256_descriptor(fd, path)
    finally:
        os.close(fd)
```

The trusted opener is responsible only for final-component no-follow acquisition and platform-specific link/reparse rejection. Type and expected/opened mismatch checks remain common and must complete before `_sha256_descriptor()` performs the first `os.read()`.

No second pathname open is permitted after the trusted descriptor has been acquired.

## 4. POSIX implementation contract

On non-Windows platforms:

1. require a real `os.O_NOFOLLOW` primitive; do not replace it with integer zero;
2. call `os.open(path, os.O_RDONLY | os.O_NOFOLLOW | optional os.O_CLOEXEC)`;
3. map a final-component no-follow link failure such as platform `ELOOP` to `symlink_not_allowed` where the failure is attributable to the final link boundary;
4. return the descriptor to common type/mismatch/read logic;
5. if `O_NOFOLLOW` is unavailable, fail closed as `filesystem_error` before any bytes are read.

`O_NOFOLLOW` protects only the final path component. Ancestor traversal remains the separate F-013 boundary.

No fallback from missing/failed no-follow support to ordinary `open()` or tuple-equality authorization is allowed.

## 5. Windows implementation contract

Use only Python standard-library facilities: `ctypes`, `msvcrt`, `os`.

### 5.1 Win32 ABI

Load Kernel32 with last-error support and pin function prototypes explicitly; do not rely on ctypes default integer coercions for 64-bit handles.

Required APIs:

- `CreateFileW`;
- `GetFileInformationByHandleEx` using `FileAttributeTagInfo`;
- `CloseHandle`.

Define the required structures/constants locally from the documented Win32 ABI, including `FILE_ATTRIBUTE_TAG_INFO`, `FILE_ATTRIBUTE_REPARSE_POINT`, `INVALID_HANDLE_VALUE`, and the `FileAttributeTagInfo` information class.

### 5.2 Trusted open

Call `CreateFileW` with:

- `GENERIC_READ`;
- `FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE`;
- `OPEN_EXISTING`;
- `FILE_FLAG_OPEN_REPARSE_POINT`.

No lock/snapshot semantics are introduced by this ticket.

After a successful raw handle open and before ownership transfer:

1. call `GetFileInformationByHandleEx(... FileAttributeTagInfo ...)`;
2. if `FILE_ATTRIBUTE_REPARSE_POINT` is present, close the raw handle exactly once and fail `symlink_not_allowed`;
3. query failure is `filesystem_error` and closes the raw handle exactly once.

### 5.3 Handle-to-descriptor ownership

Convert only after reparse inspection:

1. call `msvcrt.open_osfhandle(raw_handle, os.O_RDONLY)`;
2. successful conversion transfers ownership of the Win32 handle to the CRT descriptor;
3. after successful conversion never call `CloseHandle(raw_handle)`;
4. on conversion failure before transfer, call `CloseHandle(raw_handle)` exactly once;
5. call `msvcrt.setmode(fd, os.O_BINARY)` before any digest read;
6. if binary-mode setup fails, close the descriptor exactly once;
7. return the descriptor to common `os.fstat` / mismatch / read logic.

The common caller owns and closes a successfully returned descriptor exactly once.

`FILE_ID_INFO` is not required for continuity because the retained handle is the continuity primitive. The expected/opened Python tuple remains only a mismatch detector.

## 6. Common validation/read precedence

For each standalone, recursive-directory, or direct `.tf` file:

1. obtain expected no-follow stat using the current caller path;
2. reject already-detected link/reparse and existing unsupported/non-regular cases as today;
3. obtain trusted no-follow descriptor/handle;
4. platform-specific final reparse inspection completes;
5. `os.fstat(fd)` completes;
6. opened object must be regular;
7. expected/opened identity mismatch fails `filesystem_error`;
8. only now may `os.read(fd, 1 MiB)` begin;
9. hash all bytes from that same descriptor;
10. close descriptor exactly once.

If the pathname is renamed/replaced after step 3, later digest reads still consume the already-open inspected object.

## 7. RED sequence

Production code must not change until deterministic tests have been committed and observed RED.

### RED-A — helper boundary and POSIX continuity

On Ubuntu/POSIX, pin:

1. trusted opener uses an actual no-follow descriptor path;
2. simulated missing `O_NOFOLLOW` fails `filesystem_error` and reads zero bytes;
3. final symlink remains `symlink_not_allowed` and reads zero bytes;
4. regular-file expected/opened mismatch remains `filesystem_error` before read;
5. replacing/renaming the pathname immediately after trusted descriptor acquisition does not redirect bytes; digest equals the originally opened object;
6. no second pathname open occurs after descriptor acquisition;
7. no `os.read` before final-object/type/mismatch authorization.

Use deterministic monkeypatch/seams, not sleep/timing races.

### RED-B — Windows real-handle contract

On actual Windows runners, pin at minimum:

1. a normal regular file is opened through the Win32 trusted path and hashes correctly on Python 3.10 and 3.12;
2. handle -> CRT descriptor conversion is exercised for real, not only mocked;
3. descriptor is binary before bytes are consumed;
4. pathname replacement after trusted acquisition cannot redirect descriptor reads;
5. F-012 ordinary replacement mismatch remains fail-closed;
6. final reparse/link rejection is tested on a real reparse object where runner permissions support deterministic creation; if runner policy prevents creation, keep a focused mocked reparse-classification test **in addition to**, not instead of, real handle-conversion tests.

### RED-C — ownership and failure matrix

Mock only the failure boundaries that cannot be forced portably:

- `CreateFileW` failure -> no stray `CloseHandle` on invalid value;
- attribute query failure -> raw handle closed once;
- reparse result -> raw handle closed once and no conversion/read;
- `open_osfhandle` failure -> raw handle closed once;
- successful conversion -> raw handle never manually closed; descriptor closed once;
- `setmode` failure -> converted descriptor closed once;
- `fstat`, mismatch, and read failures -> descriptor closed once.

### RED-D — integration controls

Pin unchanged behavior for all three digest paths:

- standalone file;
- recursive directory regular files;
- direct `.tf` payload files.

Keep F-012 replacement-race tests, F-014 lexical-portability tests, I-003 identity tests, fixed digest vectors, and directory/TF controls green after GREEN implementation.

## 8. Minimal GREEN implementation order

1. add platform-private trusted descriptor opener(s);
2. add descriptor-stream hashing helper;
3. route current `_sha256_file(path, expected)` through trusted opener -> common fstat/mismatch -> descriptor hash;
4. preserve callers and all digest projection code unchanged;
5. add no new public mode, schema, digest field, or algorithm identifier.

Do not implement F-013 directory-handle traversal or F-017 in-place mutation detection in this ticket.

## 9. CI gates

Exact-head CI before final review must include:

- Ubuntu 24.04 × Python 3.10, 3.12;
- Windows latest × Python 3.10, 3.12;
- focused F-015 tests;
- F-012 regressions;
- F-014 regressions;
- I-003 parent identity regressions;
- authoritative repository full suite.

The focused workflow must use current action majors and must not duplicate the repository-wide full-suite command owned by `full-suite.yml`.

## 10. Independent review gate

After GREEN CI, perform a new exact-head adversarial review that does not rely on implementation reasoning. It must attack at least:

- accidental pathname reopen after trusted acquisition;
- use of tuple equality as authorization;
- read-before-inspection ordering;
- final-link/reparse classification;
- Windows ctypes handle-width/last-error ABI;
- raw-handle/descriptor double-close or leak paths;
- binary-mode placement;
- real Windows 3.10 behavior;
- POSIX missing-`O_NOFOLLOW` fail-closed behavior;
- digest-vector changes;
- regression into F-013/F-017 scope claims.

Any finding returns to RED -> minimal GREEN -> exact-head CI -> fresh review.

## 11. Exit condition

F-015 is complete only when:

- trusted-open inspection and digest reads are bound to one retained descriptor/handle;
- ordinary F-012 mismatch detection is retained but equality is never described or used as proof;
- supported Linux/Windows matrix passes on exact head;
- fixed digests and public categories remain compatible;
- documentation states the residual pre-open pathname and in-place-mutation boundaries;
- fresh logically-independent adversarial review reports no blockers.
