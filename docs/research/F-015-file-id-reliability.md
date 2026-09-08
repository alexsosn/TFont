# F-015 research — file identity reliability and handle-bound inspection

**Issue:** #90  
**Baseline:** current main after F-012/F-014, branch created from `8f48e3b14b4135ec68aada61ad928c2718cd2171`

## 1. Trigger

F-012 correctly removed the old `stat(path) -> reopen path with ordinary open -> hash whatever is there` behavior. It now compares an expected no-follow `(st_dev, st_ino)` pair with `fstat()` on the opened descriptor before reading bytes.

That closes ordinary regular-file and symlink substitution races, but its documentation overstates what the pair proves across every supported platform/version.

The problem is not that `(st_dev, st_ino)` is useless. Python documents a non-zero `st_ino` as identifying a file for a given `st_dev`. The problem is treating two temporally separated observations of that representation as an unconditional proof that the filesystem object itself is the same forever.

## 2. Authoritative constraints

### 2.1 Python `stat_result`

Python 3.10 documents:

- `st_ino` is platform dependent and, when non-zero, identifies a file for a given `st_dev`;
- on Windows it is the file index when available;
- Windows `DirEntry.stat()` reports zero `st_ino`/`st_dev`, so a fresh `os.stat()` is required for those fields.

Python 3.12 strengthened the Windows representation:

- `st_ino` may now be up to 128 bits depending on the filesystem;
- before 3.12 it would not exceed 64 bits and larger file identifiers were arbitrarily packed;
- `os.stat()` / `os.lstat()` Windows behavior became more accurate.

References:

- https://docs.python.org/3.10/library/os.html
- https://docs.python.org/3.12/library/os.html
- https://docs.python.org/3.12/whatsnew/3.12.html

### 2.2 Windows file IDs are not temporal object capabilities

Microsoft's `BY_HANDLE_FILE_INFORMATION` documentation states that file IDs are not guaranteed unique over time because a filesystem may reuse them. It also notes that the 64-bit identifier is not guaranteed unique on ReFS and points to `FILE_ID_INFO` for the 128-bit identifier.

`FILE_ID_INFO` contains a volume serial number plus a 128-bit file identifier and is the documented comparison representation for determining whether **two open handles** represent the same file.

References:

- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex

### 2.3 Consequence for F-012

The F-012 tuple comparison remains a useful substitution detector, especially on ordinary NTFS/Linux filesystems. It is not a portable temporal capability:

- on pre-3.12 Windows a larger underlying file ID can be represented only through the older 64-bit surface;
- ReFS does not guarantee uniqueness of that legacy 64-bit identifier;
- Windows file IDs can be reused over time after deletion;
- Unix inode numbers are filesystem-local identifiers, not permanent non-reusable capabilities.

Therefore `expected tuple == opened tuple` should not be the final authority for the stronger phrase “the exact inspected object” when an alternative can keep the inspected object itself open.

## 3. Stronger invariant: one open object, one inspection, one read

The robust invariant is simpler:

> The descriptor/handle that passes the no-follow/link/type inspection is the same descriptor/handle from which all digest bytes are read.

No temporal file-ID comparison is needed to prove inspection-to-read continuity. File IDs may remain useful diagnostics or external comparison data, but they are not the authority connecting inspection to bytes.

Pathname replacement after that trusted open is harmless to this invariant: the already-open descriptor remains bound to the inspected object. This is intentionally **not** filesystem snapshot semantics. A replacement that happens before the trusted open simply changes which object reaches the inspection point.

## 4. POSIX / Unix feasibility

Python `os.open()` exposes `O_NOFOLLOW` where the platform C library defines it. Linux and macOS provide no-follow open primitives; macOS additionally exposes `O_NOFOLLOW_ANY` on supported Python versions.

A descriptor-first regular-file path can therefore be:

1. `os.open(path, O_RDONLY | O_NOFOLLOW | optional binary/cloexec flags)`;
2. `os.fstat(fd)`;
3. require regular file;
4. only then stream via `os.read(fd, 1 MiB)`;
5. close the same descriptor in `finally`.

For a final symbolic link, `O_NOFOLLOW` prevents following the target. The implementation must preserve the public `symlink_not_allowed` category rather than leaking a platform `ELOOP` as a generic filesystem error.

`O_NOFOLLOW` is not universal. The exact-object implementation must not silently fall back to the temporal `(dev, ino)` proof on a platform where no trustworthy no-follow open exists. Research conclusion: such a platform must fail closed for this exact guarantee or be explicitly classified as a weaker unsupported portability tier. Current CI's Ubuntu path has the required primitive.

Reference:

- https://docs.python.org/3/library/os.html#os.open

## 5. Windows feasibility using only the Python standard library

Python's ordinary `os.open()` does not expose the Win32 `FILE_FLAG_OPEN_REPARSE_POINT` behavior needed for a strong no-follow handle open. However, Python's standard library includes `ctypes` and `msvcrt`, so no third-party native dependency is required.

### 5.1 Trusted Win32 open

`CreateFileW` with:

- `GENERIC_READ`;
- compatible share flags (`FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE`) to avoid introducing an unnecessary lock policy;
- `OPEN_EXISTING`;
- `FILE_FLAG_OPEN_REPARSE_POINT`;

returns a handle without normal final reparse-point processing. Microsoft documents that:

- if the existing final file is a symbolic link and the flag is set, the returned handle is to the symbolic link itself;
- if the object is not a reparse point, the flag is ignored and the ordinary file is opened.

References:

- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points-and-file-operations

### 5.2 Inspect the opened handle before reading

`GetFileInformationByHandleEx(..., FileAttributeTagInfo, ...)` returns `FILE_ATTRIBUTE_TAG_INFO`, including `FileAttributes` and `ReparseTag`. That provides a handle-bound way to reject a final reparse point before any file bytes are accepted.

Reference:

- https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_attribute_tag_info

The implementation should also validate regular-file type on the opened object before reading. This may use the descriptor's `os.fstat()` after conversion, with the Win32 attribute check still occurring first so a reparse handle is never treated as ordinary content.

### 5.3 Read the same Win32 handle through Python

`msvcrt.open_osfhandle()` converts an existing Win32 `HANDLE` into a CRT file descriptor. Python documents this standard-library bridge; Microsoft documents that `_open_osfhandle` transfers ownership of the Win32 handle to the CRT descriptor. Closing the descriptor closes the underlying handle and the original handle must not then be closed separately.

References:

- https://docs.python.org/3.10/library/msvcrt.html#msvcrt.open_osfhandle
- https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/open-osfhandle

For an ordinary regular file the sequence can therefore be:

1. `CreateFileW(... FILE_FLAG_OPEN_REPARSE_POINT ...)`;
2. query handle-bound reparse attributes;
3. reject reparse objects;
4. convert that same handle with `msvcrt.open_osfhandle` in binary/read-only mode;
5. `os.fstat(fd)` and require regular file;
6. stream via `os.read(fd, 1 MiB)`;
7. `os.close(fd)` exactly once.

This works independently of whether Python 3.10 exposes a 64-bit or Python 3.12 exposes a 128-bit `st_ino`, because no file-ID equality is needed for inspection-to-read continuity.

`FILE_ID_INFO` may still be useful for diagnostics/tests, but should not become a new temporal equality authority when the same handle can simply be retained.

## 6. Applying the invariant to TFont's three byte-bearing paths

### Standalone `file_component_digest`

The trusted open itself becomes the final-file inspection. F-014 lexical portability validation remains first. The opened object is checked for link/reparse/type and the same descriptor is hashed.

### Recursive `directory_component_digest`

For a discovered path that is going to contribute file bytes, TFont should obtain a trusted no-follow open and keep that descriptor through hashing instead of `stat -> later open`.

This does **not** solve replacement of an ancestor directory or subtree enumeration by pathname; that is the distinct F-013 boundary. F-015 only prevents a final regular-file byte read from being redirected after its trusted open.

### Direct `tf_payload_digest`

Apply the same trusted no-follow open-and-read helper to each selected direct `.tf` path.

## 7. What happens to F-012 race semantics

F-012's current deterministic tests inject a replacement between an expected pathname stat and the later open, then require an identity mismatch.

Under handle-bound inspection, that temporal gap disappears. The stronger tests should instead pin the real invariant:

- after the trusted handle/descriptor is opened and inspected, replacing the pathname cannot redirect subsequent reads;
- bytes come from the already-open inspected object;
- no second pathname open occurs for hashing;
- a pre-existing final symlink/reparse point is rejected by the trusted open path;
- no bytes are read before the opened object passes link/type validation.

This is not weakening the guarantee. It removes the race window that the F-012 tuple comparison was attempting to detect.

A pathname replacement **before** the trusted open is outside snapshot semantics: the replacement is the object that is inspected. A pathname replacement **after** trusted open may succeed at the filesystem level, but cannot redirect the descriptor's bytes.

## 8. Error and compatibility policy

Preserve existing public categories:

- trusted-open final link/reparse: `symlink_not_allowed`;
- non-regular standalone file: `wrong_path_type` where that is already the caller contract;
- trusted-open/handle-query/descriptor-conversion/read failures: `filesystem_error`;
- recursive unsupported entry types retain `unsupported_entry` where applicable.

No file-system metadata enters digest projection bytes. Existing algorithm identifiers and fixed digest vectors must remain unchanged.

No silent fallback to a known-weaker file-ID comparison is allowed when the trusted no-follow open primitive is unavailable.

## 9. RED requirements before any production change

A plan must first freeze the helper/ownership/error API. Then deterministic RED must establish at least:

1. **single-object continuity:** replace/rename the pathname after trusted descriptor acquisition and prove hashing still reads the inspected descriptor, not the replacement path;
2. **no reopen:** hashing after inspection makes no second pathname `open`;
3. **read precedence:** no `os.read` occurs before link/reparse/type checks complete;
4. **pre-existing link:** final symlink/reparse remains `symlink_not_allowed` on supported platforms;
5. **Windows handle ownership:** conversion success transfers ownership exactly once; conversion failure closes the raw Win32 handle exactly once;
6. **unsupported primitive:** a simulated platform without a trustworthy no-follow opener fails closed rather than using `(dev, ino)` equality as exact proof;
7. **digest compatibility:** fixed file/directory/TF vectors stay byte-identical;
8. **F-014/F-012 controls:** lexical path portability and existing ordinary replacement coverage are reconciled explicitly rather than accidentally discarded.

Windows-specific tests should run on actual Windows 3.10 and 3.12 runners. POSIX tests should run on Ubuntu 3.10 and 3.12. Mock-only tests are insufficient for the Win32 handle conversion path.

## 10. Non-goals and residual risks

F-015 does not claim:

- recursive directory-handle binding (F-013 researched that separately);
- protection against ancestor symlink/reparse traversal beyond existing contracts;
- filesystem snapshot/locking semantics;
- detection of in-place writes to the same already-open file object during hashing;
- stable identity across process restarts;
- external object identity publication based on file IDs.

## 11. Research conclusion

**Implementation is feasible and justified.**

The correct fix is not to make `(st_dev, st_ino)` progressively more elaborate. It is to stop using a temporally compared identifier as the authority connecting inspection to bytes.

For supported Unix, use a no-follow descriptor open and hash that same descriptor. For Windows, use standard-library `ctypes` to obtain a `CreateFileW(... FILE_FLAG_OPEN_REPARSE_POINT ...)` handle, inspect the same handle for reparse/type, transfer it once to a CRT descriptor with `msvcrt.open_osfhandle`, and hash that descriptor.

This design removes the ReFS/pre-3.12 truncation and file-ID reuse problem from the inspection-to-read proof because the proof is the retained open object itself. File IDs become optional metadata, not trust authority.

Proceed to a reviewed implementation plan; no production code should change before plan review and deterministic RED.