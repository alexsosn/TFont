# F-014 research — portable exact-file path spelling boundary

## Trigger

Cross-platform F-012 CI exposed an existing I-003 portability defect. On Windows, `file_component_digest(<regular-file> + os.sep + ".")` can reach `os.lstat()` as the underlying regular file, while POSIX rejects the same conceptual spelling. TFont therefore currently lets host pathname normalization decide whether an exact-file component spelling is accepted.

The F-012 object-binding tests themselves pass on Windows. This research is intentionally independent of F-012 production code.

## Existing contract

`file_component_digest()` represents one exact regular file. Unlike directory and TF roots, it does not call `_root_inspection_path()` to strip directory-root spellings. Existing I-003 regression coverage already requires file spellings with terminal directory syntax to fail rather than silently canonicalize.

The public failure category is not semantically tied to a particular host errno: ambiguous spellings should fail through `IdentityError` before a host can reinterpret them.

## Host behavior

Windows path parsing accepts several spellings that can be normalized before the final filesystem object is inspected. A terminal `.` path segment denotes the current directory. Microsoft also documents that ordinary Win32 path handling strips trailing ASCII periods and ASCII spaces before the actual file is opened; a spelling such as `AFile.txt ` can therefore open `AFile.txt` instead. Microsoft explicitly advises not ending file/directory names with a space or period for normal Win32 naming.

Primary evidence:

- Microsoft, **Naming Files, Paths, and Namespaces**: period as current-directory component; do not end a file/directory name with space or period.
- Microsoft Windows support, **Whitespace characters in file and folder names**: trailing ASCII space/period are removed by ordinary Windows naming behavior.
- Microsoft Windows Server support, **Can't delete files on NTFS file system**: typical Win32 syntax strips trailing spaces/periods before opening, potentially opening a different file; `\\?\` is a special namespace escape hatch.

TFont does not currently define a separate extended-namespace identity mode. Accepting these spellings on POSIX while allowing them to alias another object under ordinary Windows APIs would make the same identity input platform-dependent.

Python's `os.path` helpers are host-specific and are not sufficient by themselves to define a cross-platform lexical contract. TFont already has `_native_separators()` and exact-string path handling, so the narrowest repair is an explicit lexical check before `lstat()`.

## Chosen contract

For `file_component_digest()` only, reject a supplied path string before filesystem inspection when its terminal spelling is not portable exact-file syntax:

1. the path ends in a native path separator;
2. after a native separator, the final segment is exactly `.`; or
3. the final path component ends in an ASCII period (`.`) or ASCII space (` `).

Rule 3 is cross-platform on purpose: a POSIX file whose basename literally ends in ASCII period/space is outside TFont's portable exact-file identity input domain because the same spelling is unsafe under ordinary Win32 path handling.

Do not normalize or rewrite the path. Reject it.

Leading periods (`.hidden`) and non-terminal periods (`a.b`) remain valid. Non-native separator characters retain existing host semantics. Extended Win32 `\\?\` namespace semantics are not introduced by this patch.

Directory and TF roots retain their current `_root_inspection_path()` behavior; changing their naming domain requires separate research because they intentionally accept equivalent root spellings.

## Error category

Use existing `wrong_path_type` for these non-portable exact-file spellings. This preserves the existing I-003 expectation that a path shaped as something other than an exact regular-file component is rejected at the path/type boundary.

The original supplied path must be retained in `IdentityProblem.path`.

Embedded NUL remains `filesystem_error` through `_lstat()` and is not intercepted by this lexical check.

## RED strategy

The existing `<file>/.` I-003 regression is naturally RED on Windows but GREEN on POSIX. Focused F-014 tests make the lexical contract deterministic on every host by asserting rejection before `_lstat()`.

Focused cases:

- terminal native separator;
- repeated terminal native separators;
- terminal `.` path segment;
- terminal ASCII period in the basename;
- terminal ASCII space in the basename;
- `.hidden` and `a.b` negative controls;
- plain exact file unchanged fixed digest;
- directory and TF root spelling controls;
- embedded NUL category control.

## Non-goals

- no generic path canonicalizer;
- no change to directory/TF root equivalence;
- no Windows reserved-device-name policy;
- no drive/UNC canonicalization project;
- no case-folding or Unicode filesystem normalization;
- no extended `\\?\` identity mode;
- no digest projection change;
- no F-012 descriptor-binding change.

## Conclusion

Exact-file identity needs a lexical portability boundary independent of host filesystem normalization. Reject terminal directory syntax and Win32-ambiguous trailing ASCII period/space before `lstat()`, while preserving digest bytes for accepted files and existing directory-root semantics.