# F-018 implementation plan — handle-bound exact-file inspection

**Issue:** #90  
**Research:** `docs/research/F-018-handle-bound-file-reads.md`

## 1. Goal

Strengthen every regular-file byte read used by TFont parent/component identity so the same trusted final-component no-follow descriptor/Win32 handle that passes link/reparse/type inspection supplies every digest byte.

Keep the existing expected/opened `(st_dev, st_ino)` comparison only as defense in depth: mismatch fails, equality is never the continuity authority.

No public API or digest algorithm identifier changes.

## 2. Production scope

Only `src/tfont/parent_identity.py` after corrected RED is independently reviewed and observed.

Public functions remain:

- `file_component_digest(path)`;
- `directory_component_digest(path)`;
- `tf_payload_digest(path)`.

Existing fixed file/directory/TF digest vectors must remain byte-identical.

## 3. Private helper boundary

Target internal responsibilities:

```python
def _open_trusted_file_descriptor(path: str) -> int:
    """Return an owned binary read descriptor without following a final link/reparse point."""


def _sha256_descriptor(fd: int, path: str) -> str:
    """Hash an already-authorized descriptor without reopening path."""


def _sha256_file(path: str, expected: os.stat_result) -> str:
    fd = _open_trusted_file_descriptor(path)
    try:
        opened = os.fstat(fd)
        require regular file
        reject expected/opened identity mismatch
        return _sha256_descriptor(fd, path)
    finally:
        os.close(fd)
```

Exact private names may vary only if the RED contract pins equivalent behavior. No second pathname open after trusted acquisition is allowed. No `os.read` before link/reparse/type/mismatch authorization.

## 4. POSIX implementation

On non-Windows:

1. require a real nonzero `os.O_NOFOLLOW` primitive;
2. call `os.open(path, os.O_RDONLY | os.O_NOFOLLOW | optional os.O_CLOEXEC)`;
3. translate a final-component no-follow symlink failure such as attributable `ELOOP` to `symlink_not_allowed`;
4. return the descriptor to common validation/read logic;
5. missing/unusable no-follow support fails closed as `filesystem_error` before reads.

Do not fall back to ordinary `open()` or tuple equality.

## 5. Windows implementation

Use only stdlib `ctypes`, `msvcrt`, `os`.

Pin Kernel32 prototypes/handle widths and use last-error support for:

- `CreateFileW`;
- `GetFileInformationByHandleEx` with `FileAttributeTagInfo`;
- `CloseHandle`.

Define required ABI structures/constants locally, including `FILE_ATTRIBUTE_TAG_INFO`, `FILE_ATTRIBUTE_REPARSE_POINT`, `FILE_FLAG_OPEN_REPARSE_POINT`, `OPEN_EXISTING`, share flags and invalid-handle representation.

Trusted open sequence:

1. `CreateFileW(path, GENERIC_READ, FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE, ..., OPEN_EXISTING, FILE_FLAG_OPEN_REPARSE_POINT, ...)`;
2. query `FileAttributeTagInfo` before ownership transfer;
3. reparse -> close raw handle once and `symlink_not_allowed`;
4. query failure -> close raw handle once and `filesystem_error`;
5. `msvcrt.open_osfhandle(raw_handle, os.O_RDONLY)`;
6. successful conversion transfers ownership; never `CloseHandle` that raw handle afterward;
7. conversion failure -> raw handle closed once;
8. `msvcrt.setmode(fd, os.O_BINARY)` before reads;
9. setmode failure -> descriptor closed once;
10. return descriptor to common `fstat`/mismatch/read logic.

Common caller closes a successfully returned descriptor exactly once.

## 6. Common authorization/read precedence

For standalone, recursive-directory and direct `.tf` files:

1. preserve current caller-side expected no-follow stat and existing lexical/object classification;
2. trusted no-follow acquisition;
3. platform-specific final link/reparse inspection;
4. `os.fstat(fd)`;
5. require regular file;
6. expected/opened identity mismatch -> `filesystem_error`;
7. only then first `os.read`;
8. stream all bytes from the same descriptor;
9. close exactly once.

Path replacement after step 2 cannot redirect bytes. The contract does not claim a pre-open pathname snapshot or in-place mutation protection.

## 7. Corrected RED artifacts

The corrected F-018 RED package is `tests/f018/` and the focused workflow is `.github/workflows/f018-handle-bound-file-reads.yml`.

Mandatory tests:

### POSIX/common

- trusted descriptor helpers absent on current production -> intended RED;
- simulated zero/missing `O_NOFOLLOW` -> `filesystem_error`, zero reads;
- expected ordinary file replaced by symlink before trusted acquisition -> trusted opener itself returns `symlink_not_allowed`, zero reads;
- pathname replacement after trusted descriptor acquisition does not redirect reads;
- descriptor hasher never reopens path;
- ordinary expected/opened mismatch still fails before read;
- pre-existing symlink compatibility remains intact.

### Real Windows

On Windows latest for Python 3.10 and 3.12:

- ordinary file goes through the real Win32 handle -> `msvcrt.open_osfhandle` path;
- binary mode is set before first digest read;
- digest bytes equal ordinary fixed expected bytes;
- pathname replacement after trusted acquisition does not redirect descriptor reads where the common test is portable.

### Ownership/failure seams

Mock only difficult failure paths:

- reparse query result -> raw handle closed once, no conversion/read;
- handle query failure -> raw handle closed once;
- conversion failure -> raw handle closed once;
- conversion success -> no manual raw close, binary mode set;
- setmode failure -> descriptor closed once, raw handle not double-closed;
- later common fstat/mismatch/read errors -> descriptor closed once.

### Regression controls

Under `if: always()` run:

- `tests/f012`;
- `tests/f014`;
- `tests/i003`.

Central `full-suite.yml` owns repository-wide tests; focused workflow must not duplicate that command.

## 8. RED acceptance

Before production changes, exact renamed F-018 head must run Ubuntu 24.04 + Windows latest × Python 3.10/3.12 and show:

- focused F-018 contract fails because trusted helper/Win32 boundary is not implemented;
- F-012/F-014/I-003 regressions remain green;
- failures arise from intended missing behavior rather than namespace/import/setup mistakes.

The obsolete F-015 RED evidence does not satisfy this gate after the material namespace correction.

## 9. Minimal GREEN order

Only after RED evidence:

1. add POSIX trusted descriptor opener;
2. add Windows trusted handle helpers and ownership conversion;
3. add descriptor-stream SHA-256 helper;
4. route existing `_sha256_file(path, expected)` through trusted acquisition -> common fstat/type/mismatch -> descriptor hashing;
5. preserve every caller and digest projection unchanged.

Do not implement F-013 ancestor-directory traversal or F-017 in-place mutation semantics.

## 10. Error compatibility

Preserve public categories:

- trusted final link/reparse -> `symlink_not_allowed`;
- standalone non-regular file -> existing `wrong_path_type` behavior;
- trusted-open/query/conversion/setmode/fstat/mismatch/read/missing primitive -> `filesystem_error` unless an existing caller path is more specific;
- recursive unsupported entries -> existing `unsupported_entry`.

No file-ID metadata enters digest bytes. Algorithm constants remain unchanged.

## 11. CI before final review

Require exact-head:

- focused F-018 Ubuntu/Windows × Python 3.10/3.12 GREEN;
- F-012 GREEN;
- F-014 GREEN;
- I-003 GREEN;
- authoritative full repository suite GREEN;
- compare against current main contains only F-018 research/plan/tests/workflow plus the narrow `parent_identity.py` production delta.

If main moves, integrate current main and rerun exact-head CI before final review.

## 12. Independent adversarial review

Fresh exact-head logically-independent review is mandatory after GREEN. It must attack:

- accidental pathname reopen;
- tuple equality used as authorization;
- read-before-inspection ordering;
- trusted-opener final symlink/reparse replacement;
- Windows ctypes handle-width and last-error ABI;
- raw-handle/descriptor leaks or double-close;
- binary-mode placement;
- actual Windows 3.10 behavior;
- POSIX missing-`O_NOFOLLOW` fail-closed behavior;
- digest-vector changes;
- scope creep into F-013/F-017.

Any material repair invalidates prior final review and returns through RED/GREEN/CI.

## 13. Exit condition

F-018 is complete only when trusted-open inspection and all digest reads use one retained descriptor/handle; tuple mismatch remains defense in depth without equality overclaim; exact Linux/Windows matrix and full suite are green; existing digest bytes/categories remain compatible; and fresh independent review reports no blocker.