# F-012 research — bind file hashing to the inspected filesystem object

## Scope

F-012 hardens only the regular-file byte-reading boundary used by I-003 identity functions. It builds on merged F-010, so recursive traversal is already iterative, but it does not change F-010 traversal semantics.

Affected call paths:

- `file_component_digest()` → `_sha256_file()`;
- `directory_component_digest()` → `_file_record()` → `_sha256_file()`;
- `tf_payload_digest()` → `_file_record()` → `_sha256_file()`.

No schema, semantic, compatibility, ontology, parent-manifest projection, digest algorithm identifier, canonical JSON, or corpus-specific behavior is in scope.

## Current defect

The current code checks a pathname without following links (`os.lstat()` or `DirEntry.stat(follow_symlinks=False)`), proves that it is a regular file, and later calls `open(path, "rb")` to hash bytes. The pathname is therefore checked and used in two separate filesystem operations.

A path can change between those operations. In particular, a regular file that passed inspection can be replaced by a symlink/reparse point or by another regular file before `open()`. The current hasher then follows the new pathname and hashes bytes from an object that never passed the original inspection.

This violates the intended identity boundary: the bytes must belong to the filesystem object that was accepted as the component entry, not merely whatever object happens to occupy the same pathname later.

## Platform evidence

Python documents `os.stat_result.st_ino` as the platform-specific file identifier (inode on Unix, file index on Windows) and `st_dev` as the device identifier. When `st_ino` is non-zero, the pair `(st_dev, st_ino)` identifies the file object for the device.

Python also documents that `os.fstat(fd)` returns `stat_result` for an already-open descriptor. Once the descriptor is open, subsequent reads are bound to that open object even if the pathname later changes.

`os.DirEntry.stat()` is not suitable as the authoritative identity source for F-012: it is cached, and Python documents that on Windows `DirEntry.stat()` reports zero for `st_ino` and `st_dev`. A fresh `os.stat(path, follow_symlinks=False)` / `os.lstat(path)` is required when current object identity is needed.

Some POSIX-like platforms expose `os.O_NOFOLLOW`; Python explicitly documents it as a platform-dependent C-library extension. It is useful defense-in-depth for the final path component, but it cannot be the portable contract because it is not guaranteed to exist on every supported platform and by itself does not prove that an ordinary regular file was not replaced by a different ordinary regular file.

Primary references:

- Python `os.stat`, `os.lstat`, `os.fstat`, `os.stat_result`, `DirEntry.stat`: https://docs.python.org/3/library/os.html
- Python `os.open` flag constants including `O_NOFOLLOW`: https://docs.python.org/3/library/os.html#open-flag-constants

## Chosen object-binding contract

For every regular file whose bytes contribute to an I-003 identity digest:

1. Obtain a **fresh no-follow** `stat_result` for the pathname at the point where the caller accepts that entry.
2. Reject link-like objects before hashing using the existing `symlink_not_allowed` contract.
3. Reject non-regular objects using the existing path/type contract for that caller.
4. Treat the fresh `(st_dev, st_ino)` pair as the expected file-object identity.
5. If that identity cannot be proven (`st_ino == 0` or an otherwise unavailable identity pair), fail closed as `IdentityError(category="filesystem_error")`. F-012 must not silently downgrade to path-only trust.
6. Open the file as a descriptor. Add `O_NOFOLLOW` where Python exposes it, but do not rely on it for portability.
7. Immediately call `os.fstat(fd)` **before reading bytes**.
8. Require the opened descriptor to still be a regular file and require its `(st_dev, st_ino)` pair to equal the expected pair.
9. If the pathname changed, `O_NOFOLLOW` rejects the open, the descriptor is not regular, or the identity pair differs, fail `filesystem_error` at the affected filesystem path before reading bytes.
10. Only then stream the file through SHA-256 using the existing 1 MiB chunking behavior.

The semantic distinction is intentional:

- a link/reparse point already present when the component entry is inspected remains `symlink_not_allowed`;
- a path that changes **after** a regular-file inspection is a filesystem race and is reported as `filesystem_error`.

## Call-site consequences

### Standalone file component

`file_component_digest()` already has a fresh `_lstat()` result. It should pass that expected stat into the hashing helper instead of reopening without an object expectation.

### Recursive directory identity

F-010 currently calls `DirEntry.stat(follow_symlinks=False)` and later hashes the path. F-012 should replace the authoritative file-entry stat with a fresh path `os.stat(entry_path, follow_symlinks=False)` before accepting the file and pass that `stat_result` into `_file_record()` / `_sha256_file()`.

This also avoids the documented Windows `DirEntry.stat()` zero-identity behavior for file records.

### Direct TF payload identity

Use the same fresh no-follow stat and pass it into `_file_record()` for direct regular `.tf` files.

## Digest compatibility

The digest projection does not contain filesystem metadata. `st_dev`/`st_ino` are validation-only runtime facts and are never serialized or hashed.

For unchanged regular files, the bytes, chunk order, SHA-256, logical-path records, UTF-16 path ordering, canonical JSON, and public algorithm identifiers therefore remain byte-for-byte identical.

## Deterministic RED strategy

Do not rely on timing or threads. Use a temporary regular file plus a second object with different bytes. Inject the replacement immediately after inspection and before the hash-open boundary. A deterministic regular-file replacement is mandatory because it proves the identity comparison independently of `O_NOFOLLOW`.

Controls pin unchanged fixed vectors and existing pre-inspection symlink classification.

## Error behavior

Reuse existing public categories; do not introduce a new API category.

- pre-existing link/reparse point: `symlink_not_allowed`;
- open/fstat/read failure: `filesystem_error`;
- expected identity unavailable: `filesystem_error`;
- opened object not regular: `filesystem_error`;
- expected/opened `(st_dev, st_ino)` mismatch: `filesystem_error`;
- problem path: exact filesystem pathname being hashed.

## Explicit non-goals

F-012 does **not** claim snapshot semantics for concurrent in-place writes. If the same file object is modified while its descriptor is being read, `(st_dev, st_ino)` remains the same.

F-012 also does **not** atomically bind directory traversal to an inspected directory object. F-013 researched that separately and established that a uniform Python-stdlib cross-platform directory-handle guarantee is not currently available.

## Current-main reconciliation

This research is being replayed on current `main` after F-014 merged. Final implementation must preserve F-014's exact-file lexical portability guard, F-010 iterative traversal, F-007 centralized full-suite ownership, and F-011 Node-24 action majors.

## Conclusion

F-012 should bind every hashed regular file to the exact inspected file object using a fresh no-follow expected stat plus immediate descriptor `fstat()` identity verification. This closes silent final-file pathname substitution without changing digest bytes or the now-merged portable path-spelling rules.