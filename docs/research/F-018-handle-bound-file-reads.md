# F-018 research — handle-bound file inspection and hashing

**Issue:** #90  
**Supersedes:** the obsolete F-015 namespace on the pre-correction branch; F-015 belongs to issue #87.  
**Baseline:** current main after F-012/F-014/F-017 research; no production code in this lane yet.

## Question

Can TFont strengthen regular-file digesting so that the object which passes final no-follow/reparse/type inspection is exactly the open object from which digest bytes are read, across supported Python 3.10/3.12 on POSIX and Windows, without treating `(st_dev, st_ino)` equality as an unconditional temporal proof?

## Why this is a separate F-018 ticket

F-012 removed the old `stat(path) -> reopen path -> hash whatever is there` race by comparing an expected no-follow `(st_dev, st_ino)` tuple with `fstat()` on the opened descriptor. That mismatch detector is useful, but equality of two temporally separated identity representations is not a universal object capability:

- Python 3.12 expanded Windows `st_ino` to support up to 128-bit file identifiers; earlier Python versions exposed a narrower representation on some filesystems;
- Microsoft documents file-ID reuse over time and warns that the legacy 64-bit identifier is not guaranteed unique on ReFS;
- Unix inode/device identity is filesystem-local and may be reused after deletion.

Therefore F-018 retains tuple mismatch as defense in depth but does not use tuple equality as the authority for inspection-to-read continuity.

Primary references retained from the reviewed predecessor research:

- Python `os.stat_result`, `os.open`, `os.fstat`, and open-flag documentation for Python 3.10/3.12;
- Microsoft `BY_HANDLE_FILE_INFORMATION`, `FILE_ID_INFO`, `CreateFileW`, reparse-point operations, and `GetFileInformationByHandleEx` documentation;
- Python `msvcrt.open_osfhandle` and Microsoft `_open_osfhandle` ownership documentation.

## Strong invariant

The authoritative invariant is:

> The same trusted no-follow descriptor/Win32 handle that passes final-object link/reparse/type inspection supplies every byte accepted by the digest.

Layered sequence:

1. keep the existing pre-open no-follow stat where callers already have it;
2. obtain a trusted final-component no-follow descriptor/handle;
3. inspect that opened object for link/reparse and file type;
4. compare expected/opened platform identity as a one-way mismatch detector;
5. read every digest byte from the already-inspected descriptor/handle;
6. never reopen the pathname for hashing.

A pathname rename/replacement after trusted acquisition cannot redirect reads. The contract deliberately does not claim a filesystem snapshot before acquisition or immutability of the same opened object while it is being read.

## POSIX feasibility

On POSIX-like supported runners, use `os.open(path, O_RDONLY | O_NOFOLLOW | optional O_CLOEXEC)` with a real `O_NOFOLLOW` primitive. Then:

- `os.fstat(fd)` validates the opened object;
- require regular-file type;
- reject expected/opened identity mismatch;
- stream bytes with `os.read` from that descriptor only;
- close it exactly once in `finally`.

A final symbolic-link failure attributable to no-follow open must preserve `symlink_not_allowed`. If a trustworthy no-follow primitive is unavailable, F-018 fails closed as `filesystem_error`; it does not silently fall back to ordinary `open()` plus tuple equality.

This protects only the final component. Ancestor-directory traversal remains F-013's distinct boundary.

## Windows feasibility with the standard library

Python's ordinary `os.open()` does not expose the required final reparse-point semantics, but `ctypes` and `msvcrt` are sufficient.

### Trusted Win32 acquisition

Use `CreateFileW` with:

- `GENERIC_READ`;
- `FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE`;
- `OPEN_EXISTING`;
- `FILE_FLAG_OPEN_REPARSE_POINT`.

Pin ctypes prototypes and handle widths explicitly and load Kernel32 with last-error support.

Before ownership transfer, query `GetFileInformationByHandleEx(... FileAttributeTagInfo ...)`. If `FILE_ATTRIBUTE_REPARSE_POINT` is set, close the raw handle once and report `symlink_not_allowed`. Query/open failures remain `filesystem_error` with correct one-owner cleanup.

### Handle to descriptor

After the raw handle is accepted:

1. call `msvcrt.open_osfhandle(raw_handle, os.O_RDONLY)`;
2. successful conversion transfers ownership to the CRT descriptor;
3. never manually `CloseHandle` after successful transfer;
4. if conversion fails before transfer, close the raw handle exactly once;
5. call `msvcrt.setmode(fd, os.O_BINARY)` before reads;
6. on setmode failure close the descriptor exactly once;
7. use common `os.fstat`, mismatch check and `os.read` logic;
8. close the descriptor exactly once.

The retained handle/descriptor—not file-ID equality—is the continuity primitive, so the primary guarantee is not dependent on Python 3.10 versus 3.12 `st_ino` width.

## TFont call paths

The same helper boundary applies to all byte-bearing parent identity paths:

- `file_component_digest()`;
- recursive regular files in `directory_component_digest()`;
- direct `.tf` payload files in `tf_payload_digest()`.

F-014 lexical exact-file checks stay before filesystem inspection. F-012 ordinary regular-to-different-regular replacement mismatch remains a required defense-in-depth regression.

## Error compatibility

Preserve existing public categories:

- final link/reparse through trusted acquisition -> `symlink_not_allowed`;
- standalone non-regular file -> existing `wrong_path_type` behavior;
- trusted open/query/conversion/setmode/fstat/mismatch/read or missing no-follow primitive -> `filesystem_error` unless an existing caller contract is more specific;
- recursive unsupported entry types -> existing `unsupported_entry` behavior.

No filesystem identity metadata enters digest projection bytes. Existing algorithm identifiers and fixed digest vectors remain unchanged.

## RED requirements

Before production code, deterministic tests must prove at least:

1. helper boundary exists only after implementation, so current head is RED;
2. POSIX missing/zero no-follow primitive fails closed with zero reads;
3. after expected regular-file stat, replacing final path with a symlink before trusted acquisition is rejected by the trusted opener with zero reads;
4. ordinary expected/opened regular-file mismatch still fails before read;
5. pathname replacement immediately after trusted descriptor acquisition cannot redirect subsequent reads;
6. descriptor hashing performs no pathname reopen;
7. no digest read occurs before final-object/type/mismatch authorization;
8. actual Windows 3.10/3.12 exercises normal-file `CreateFileW -> open_osfhandle -> binary descriptor -> read` behavior;
9. Win32 raw-handle/descriptor ownership failure matrix closes exactly one owner;
10. F-012, F-014, I-003 and fixed digest controls remain green.

Use Ubuntu 24.04 and Windows latest, each on Python 3.10 and 3.12. Windows normal-file handle conversion must be exercised for real; mocks are limited to difficult failure/ownership seams.

## Non-goals

F-018 does not claim or implement:

- ancestor-directory handle binding (F-013);
- filesystem snapshot or locking semantics;
- detection/prevention of in-place writes to the same open object (F-017 research);
- proof of which object occupied a pathname before trusted acquisition when a colliding/reused identity defeats the mismatch detector;
- stable object identity across process restarts;
- third-party native extensions.

## Research conclusion

Implementation is feasible and justified with a layered contract. Retain tuple mismatch as useful evidence, but make a single trusted no-follow descriptor/handle authoritative from final-object inspection through every digest read. POSIX uses a real no-follow descriptor primitive and fails closed if unavailable. Windows uses standard-library ctypes for a no-follow/reparse-aware handle, then transfers ownership exactly once to a binary CRT descriptor. Existing digest bytes and public categories remain compatible.

This corrected F-018 research replaces the obsolete F-015 naming only; it does not authorize production until the corrected plan and renamed RED artifacts are reviewed and rerun.