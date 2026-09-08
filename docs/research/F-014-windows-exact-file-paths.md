# F-014 research — portable exact-file path spelling boundary

## Trigger

Cross-platform F-012 CI exposed an existing I-003 portability defect. On Windows, `file_component_digest(<regular-file> + os.sep + ".")` can reach `os.lstat()` as the underlying regular file, while POSIX rejects the same conceptual spelling. TFont therefore currently lets host pathname normalization decide whether an exact-file component spelling is accepted.

The F-012 object-binding tests themselves pass on Windows. This research is intentionally independent of F-012 production code.

## Existing contract

`file_component_digest()` represents one exact regular file. Unlike directory and TF roots, it does not call `_root_inspection_path()` to strip directory-root spellings. Existing I-003 regression coverage already requires file spellings with terminal directory syntax to fail rather than silently canonicalize.

The public failure category is not semantically tied to a particular host errno: these spellings are not valid exact-file component spellings, so they should fail through `IdentityError` before a host can reinterpret them.

## Host behavior

Windows path parsing accepts several spellings that can be normalized before the final filesystem object is inspected. In particular, a terminal `.` segment denotes the current directory in Windows pathname syntax. POSIX commonly rejects `<file>/.` because the prefix is not a directory. Depending on the host to reject it therefore creates platform-dependent identity input semantics.

Python's `os.path` helpers are host-specific and are not sufficient by themselves to define a cross-platform lexical contract. TFont already has `_native_separators()` and exact-string path handling, so the narrowest repair is an explicit lexical check using the current host's native separators before `lstat()`.

## Chosen contract

For `file_component_digest()` only, reject a supplied path string before filesystem inspection when its terminal spelling requires directory semantics:

1. the path ends in a native path separator; or
2. after a native separator, the final segment is exactly `.` (with or without further terminal native separators).

Do not normalize or rewrite the path. Reject it.

This deliberately does **not** reject dots inside an ordinary filename (`a.`, `.hidden`, `a.b`) and does not reinterpret non-native separator characters. Existing Windows backslash semantics and POSIX literal-backslash semantics remain host-correct.

Directory and TF roots retain their current `_root_inspection_path()` behavior; their API contract intentionally accepts equivalent directory-root spellings.

## Error category

Use existing `wrong_path_type` for a lexically directory-shaped exact-file spelling. This is consistent with the intended failure: the caller supplied a spelling that denotes/traverses directory syntax where an exact regular-file component is required.

The exact message may state that the exact-file path must not end in directory syntax. The original supplied path must be retained in `IdentityProblem.path`.

Embedded NUL remains `filesystem_error` through `_lstat()` and is not intercepted by this lexical check.

## RED strategy

The existing `<file>/.` I-003 regression is naturally RED on Windows but GREEN on POSIX. Add a focused F-014 suite whose RED is deterministic on every host by testing a private lexical predicate/helper directly, rather than pretending POSIX can reproduce Windows filesystem normalization.

Focused cases:

- `file + native-separator + "."` rejected lexically;
- `file + native-separator` rejected lexically;
- repeated terminal native separators rejected;
- `file + separator + "." + separator` rejected;
- ordinary names containing dots are not classified as directory-shaped;
- plain exact file remains accepted with unchanged fixed digest;
- directory and TF root spelling behavior remains unchanged;
- embedded NUL still reaches existing `filesystem_error` boundary.

The cross-platform CI then proves the public `<file>/.` regression on Windows and guards POSIX behavior.

## Non-goals

- no generic path canonicalizer;
- no change to directory/TF root equivalence;
- no Windows reserved-name policy;
- no drive/UNC canonicalization project;
- no case-folding or Unicode filesystem normalization;
- no digest projection change;
- no F-012 descriptor-binding change.

## Conclusion

Exact-file identity needs a small lexical precondition independent of host filesystem normalization. Reject terminal directory syntax before `lstat()` and preserve all existing digest bytes and directory-root semantics.