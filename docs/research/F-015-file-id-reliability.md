# F-015 research — file identity reliability and handle-bound inspection

**Issue:** #90  
**Baseline:** current main after F-012/F-014; research branch integrated with `main=200dcaba593d02d4d903aa424d6c7fec574f2ff2` before this correction.

## 1. Trigger

F-012 correctly removed the old `stat(path) -> reopen path with ordinary open -> hash whatever is there` behavior. It now compares an expected no-follow `(st_dev, st_ino)` pair with `fstat()` on the opened descriptor before reading bytes.

That closes ordinary regular-file and symlink substitution races, but its documentation overstates what equality of the pair proves across every supported platform/version.

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

Microsoft's `BY_HANDLE_FILE_INFORMATION` documentation states that file IDs are not guaranteed unique over time because a filesystem may reuse them. It also notes that the legacy 64-bit identifier is not guaranteed unique on ReFS and points to `FILE_ID_INFO` for the 128-bit identifier.

`FILE_ID_INFO` contains a volume serial number plus a 128-bit file identifier and is the documented comparison representation for determining whether **two open handles** represent the same file.

References:

- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex

### 2.3 Consequence for F-012

The F-012 tuple comparison remains valuable, especially on ordinary NTFS/Linux filesystems. Its two outcomes have different evidentiary strength:

- **mismatch is dispositive**: the opened object is not represented by the same platform identity tuple as the pre-open object, so TFont must fail closed;
- **equality is not universally dispositive**: on pre-3.12 Windows a larger underlying file ID can be represented only through the older 64-bit surface; ReFS does not guarantee uniqueness of that legacy identifier; Windows file IDs can be reused over time after deletion; Unix inode numbers are filesystem-local identifiers rather than permanent non-reusable capabilities.

Therefore F-015 must **retain tuple mismatch detection as defense in depth** while removing tuple equality from the set of facts that authorize the stronger phrase “the exact inspected object.”

## 3. Stronger invariant: one retained open object for inspection and reading

The primary invariant is:

> The descriptor/handle that passes the trusted no-follow/link/type inspection is the same descriptor/handle from which all digest bytes are read.

The pre-open expected stat remains useful for detecting ordinary substitutions. The intended sequence is therefore layered:

1. retain the existing pre-open no-follow stat where the caller already has it;
2. perform a **trusted no-follow open**;
3. inspect the opened descriptor/handle itself for link/reparse/type;
4. compare expected/opened platform identity as a **one-way detector**: mismatch fails; equality does not prove continuity by itself;
5. read every digest byte from that already-inspected open descriptor/handle;
6. never reopen the pathname for hashing.

This preserves F-012's deterministic ordinary regular→regular replacement rejection and adds a stronger inspection→read authority.

Pathname replacement after the trusted open is harmless to the primary invariant: the already-open descriptor remains bound to the inspected object. This is intentionally **not** filesystem snapshot semantics.

There is an irreducible boundary before the trusted open: a pathname object can change after the pre-open stat. The tuple detector catches ordinary changes, but a colliding/truncated/reused identifier can defeat that detector. F-015 must document this rather than claim that a pathname-only pre-open observation is an unforgeable object capability.

## 4. POSIX / Unix feasibility

Python `os.open()` exposes `O_NOFOLLOW` where the platform C library defines it. Linux and macOS provide no-follow open primitives; macOS additionally exposes `O_NOFOLLOW_ANY` on supported Python versions.

A regular-file path can therefore use:

1. the existing expected no-follow stat for defense-in-depth change detection;
2. `os.open(path, O_RDONLY | O_NOFOLLOW | optional platform flags)`;
3. `os.fstat(fd)`;
4. require regular file;
5. fail on expected/opened identity mismatch where the expected tuple is available;
6. only then stream via `os.read(fd, 1 MiB)`;
7. close the same descriptor in `finally`.

For a final symbolic link, `O_NOFOLLOW` prevents following the target. The implementation must preserve the public `symlink_not_allowed` category rather than leak a platform `ELOOP` as a generic filesystem error.

`O_NOFOLLOW` is not universal. For F-015's exact handle-continuity mode, a platform without a trustworthy final-component no-follow opener must **fail closed as `filesystem_error`** rather than silently fall back to tuple equality as proof. This ticket does not introduce a second public “weaker mode.” Current Ubuntu CI has the required primitive.

Reference:

- https://docs.python.org/3/library/os.html#os.open

## 5. Windows feasibility using only the Python standard library

Python's ordinary `os.open()` does not expose the Win32 `FILE_FLAG_OPEN_REPARSE_POINT` behavior needed for a strong no-follow handle open. However, Python's standard library includes `ctypes` and `msvcrt`, so no third-party native dependency is required.

### 5.1 Trusted Win32 open

`CreateFileW` with:

- `GENERIC_READ`;
- compatible share flags (`FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE`) so F-015 does not invent a stronger lock policy;
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

The implementation must also validate regular-file type on the opened object before reading. This may use `os.fstat(fd)` after conversion, with the Win32 reparse-attribute query occurring before the descriptor is authorized for hashing.

### 5.3 Read the same Win32 handle through Python

`msvcrt.open_osfhandle()` converts an existing Win32 `HANDLE` into a CRT file descriptor. Python documents this standard-library bridge; Microsoft documents that `_open_osfhandle` **transfers ownership** of the Win32 handle to the CRT descriptor. Closing the descriptor closes the underlying handle, so the raw handle must not also be closed after successful conversion.

References:

- https://docs.python.org/3.10/library/msvcrt.html#msvcrt.open_osfhandle
- https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/open-osfhandle

The plan must use a documented ownership/binary sequence:

1. `CreateFileW(... FILE_FLAG_OPEN_REPARSE_POINT ...)`;
2. query handle-bound reparse attributes;
3. reject reparse objects;
4. call `msvcrt.open_osfhandle(handle, os.O_RDONLY)`; on success ownership transfers to the CRT descriptor;
5. put that descriptor in binary mode with the documented `msvcrt.setmode(fd, os.O_BINARY)` path before byte reads;
6. `os.fstat(fd)` and require regular file;
7. apply the retained expected/opened tuple **mismatch** detector where available;
8. stream via `os.read(fd, 1 MiB)`;
9. `os.close(fd)` exactly once.

If conversion fails before ownership transfer, F-015 must call `CloseHandle` exactly once. If conversion succeeds, all later cleanup goes through `os.close(fd)` and never `CloseHandle` on the original raw value.

This works independently of whether Python 3.10 exposes a 64-bit or Python 3.12 exposes a 128-bit `st_ino` for the **primary** inspection→read guarantee, because the same retained handle supplies the bytes. A tuple mismatch still catches ordinary substitution; tuple equality never authorizes continuity.

`FILE_ID_INFO` may remain useful for diagnostics/research but should not become a new temporal equality authority when the actual inspected handle can simply be retained.

## 6. Applying the layered invariant to TFont's three byte-bearing paths

### Standalone `file_component_digest`

F-014 lexical portability validation remains first. Preserve the current pre-open stat for existing error classification and mismatch detection. The trusted no-follow open then produces the handle/descriptor that is itself checked and hashed without a pathname reopen.

### Recursive `directory_component_digest`

For a discovered path that is going to contribute file bytes, retain the current fresh no-follow stat as the ordinary-substitution detector, then obtain a trusted no-follow open and keep that descriptor through hashing.

This does **not** solve replacement of an ancestor directory or subtree enumeration by pathname; that is the distinct F-013 boundary. F-015 only strengthens the final regular-file byte-reading boundary.

### Direct `tf_payload_digest`

Apply the same expected-stat + trusted-open + same-descriptor-read helper to each selected direct `.tf` path.

## 7. F-012 race semantics are preserved, not discarded

F-012's deterministic tests inject a replacement between expected pathname stat and later open and require an identity mismatch.

Those tests remain valid and should stay. F-015 adds a second class of tests around the retained handle:

- ordinary expected/opened tuple mismatch still fails `filesystem_error` before bytes are read;
- after trusted descriptor acquisition and handle inspection, replacing/renaming the pathname cannot redirect subsequent reads;
- bytes come from the already-open inspected object;
- no second pathname open occurs for hashing;
- a pre-existing final symlink/reparse point is rejected by the trusted open path;
- no bytes are read before the opened object passes link/reparse/type validation.

The two layers serve different purposes:

- tuple mismatch = useful evidence that a pre-open substitution occurred;
- retained handle = authoritative continuity from trusted-open inspection through hashing.

A tuple equality on a lossy/reused representation is **not** proof that no pre-open substitution occurred. That residual limitation must remain explicit.

## 8. Error and compatibility policy

Preserve existing public categories:

- trusted-open final link/reparse: `symlink_not_allowed`;
- non-regular standalone file: `wrong_path_type` where that is already the caller contract;
- trusted-open/handle-query/descriptor-conversion/binary-mode/read failures: `filesystem_error`;
- missing trusted no-follow primitive: `filesystem_error` fail-closed;
- recursive unsupported entry types retain `unsupported_entry` where applicable.

No filesystem metadata enters digest projection bytes. Existing algorithm identifiers and fixed digest vectors must remain unchanged.

No silent fallback to tuple equality as exact proof is allowed.

## 9. RED requirements before any production change

A plan must first freeze the helper/ownership/error API. Then deterministic RED must establish at least:

1. **F-012 mismatch preservation:** ordinary regular→different-regular replacement between expected stat and trusted open still fails before read;
2. **single-object continuity:** replace/rename the pathname after trusted descriptor acquisition and prove hashing still reads the inspected descriptor, not the replacement path;
3. **no reopen:** hashing after trusted inspection makes no second pathname open;
4. **read precedence:** no `os.read` occurs before link/reparse/type and mismatch checks complete;
5. **pre-existing link:** final symlink/reparse remains `symlink_not_allowed` on supported platforms;
6. **Windows handle ownership:** conversion success transfers ownership exactly once; conversion failure closes the raw Win32 handle exactly once;
7. **Windows binary mode:** descriptor is placed in documented binary mode before reads;
8. **unsupported primitive:** a simulated platform without a trustworthy no-follow opener fails closed rather than using tuple equality as exact proof;
9. **digest compatibility:** fixed file/directory/TF vectors stay byte-identical;
10. **F-014 controls:** lexical path portability remains unchanged.

Windows-specific tests must run on actual Windows 3.10 and 3.12 runners. POSIX tests must run on Ubuntu 3.10 and 3.12. Mock-only tests are insufficient for the Win32 handle conversion path.

## 10. Non-goals and residual risks

F-015 does not claim:

- recursive directory-handle binding (F-013 researched that separately);
- protection against ancestor symlink/reparse traversal beyond existing contracts;
- filesystem snapshot/locking semantics;
- detection of in-place writes to the same already-open file object during hashing;
- proof of which object occupied the pathname before trusted open when a colliding/reused identifier defeats the mismatch detector;
- stable identity across process restarts;
- external object identity publication based on file IDs.

## 11. Research conclusion

**Implementation is feasible and justified, with a layered contract.**

The correct fix is not to make `(st_dev, st_ino)` progressively more elaborate and not to throw away F-012's useful mismatch detector.

- Retain the current expected/opened tuple comparison as **defense-in-depth**: mismatch fails; equality does not prove sameness.
- Make the retained no-follow descriptor/handle the **authority** for continuity from trusted-open inspection through every digest read.
- On Windows, use standard-library `ctypes` for `CreateFileW(... FILE_FLAG_OPEN_REPARSE_POINT ...)` and handle-bound reparse inspection, then transfer ownership exactly once with `msvcrt.open_osfhandle`, set binary mode, and hash that descriptor.
- On Unix, use a real no-follow descriptor open; if that primitive is unavailable, fail closed rather than downgrade silently.

This design preserves F-012's ordinary substitution rejection while removing ReFS/pre-3.12 truncation and file-ID reuse from the *inspection-to-read* proof. It also states the remaining pre-open non-snapshot boundary instead of overclaiming it.

Proceed to a reviewed implementation plan only after a fresh skeptical review of this corrected research head; no production code should change before that gate.