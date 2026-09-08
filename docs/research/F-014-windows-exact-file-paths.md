# F-014 research — portable exact-file path spelling boundary

## Trigger

Cross-platform F-012 CI exposed an existing I-003 portability defect. On Windows, `file_component_digest(<regular-file> + os.sep + ".")` can reach `os.lstat()` as the underlying regular file, while POSIX rejects the same conceptual spelling. TFont therefore currently lets host pathname normalization decide whether an exact-file component spelling is accepted.

The F-012 object-binding tests themselves pass on Windows. This research is intentionally independent of F-012 production code.

## Existing contract

`file_component_digest()` represents one exact regular file. Unlike directory and TF roots, it does not call `_root_inspection_path()` to strip directory-root spellings. Existing I-003 regression coverage already requires file spellings with terminal directory syntax to fail rather than silently canonicalize.

Ambiguous spellings should fail through `IdentityError` before a host can reinterpret them.

## Host behavior

Windows path parsing can normalize spelling before the final filesystem object is inspected. A `.` path segment denotes the current directory. Microsoft also documents that ordinary Win32 path handling strips trailing ASCII periods and ASCII spaces from path-name components before opening; this can make a spelling resolve to a different stored name.

Primary evidence:

- Microsoft, **Naming Files, Paths, and Namespaces**: period as current-directory component; do not end a file/directory name with space or period.
- Microsoft Windows support, **Whitespace characters in file and folder names**: trailing ASCII space/period are removed by ordinary Windows naming behavior.
- Microsoft Windows Server support, **Can't delete files on NTFS file system**: typical Win32 syntax strips trailing spaces/periods before opening, potentially opening a different file; `\\?\` is a special namespace escape hatch.

The risk is not confined to the basename. An ancestor spelling such as `directory.\file.tf` can also be normalized at the directory component before lookup reaches the final file. Therefore checking only the last component leaves the same cross-platform alias problem in an ancestor.

TFont does not define a separate extended-namespace identity mode. Accepting these spellings on POSIX while allowing ordinary Windows APIs to alias another object would make the same identity input platform-dependent.

## Chosen contract

For `file_component_digest()` only, reject before filesystem inspection when:

1. the supplied path ends in a native path separator; or
2. **any non-empty native path component** ends in ASCII period (`.`) or ASCII space (` `).

Rule 2 includes a component equal to `.` and covers both final and ancestor components. It is cross-platform on purpose: POSIX names with these terminal characters are outside TFont's portable exact-file identity input domain because the same spelling is unsafe under ordinary Win32 path handling.

Do not normalize or rewrite the path. Reject it.

Leading periods (`.hidden`) and internal periods (`a.b`) remain valid. Non-native separator characters retain existing host semantics. Extended Win32 `\\?\` namespace semantics are not introduced by this patch.

Directory and TF roots retain their current `_root_inspection_path()` behavior; changing their naming domain requires separate research because they intentionally accept equivalent root spellings.

## Error category

Use existing `wrong_path_type` for these non-portable exact-file spellings. The original supplied path is retained in `IdentityProblem.path`.

Embedded NUL remains `filesystem_error` through `_lstat()` and is not intercepted by this lexical check.

## RED strategy

The existing `<file>/.` I-003 regression is naturally RED on Windows but GREEN on POSIX. Focused F-014 tests make the lexical contract deterministic on every host by asserting rejection before `_lstat()`.

Focused cases include terminal separators, terminal dot segment, final trailing ASCII period/space, ancestor components ending in ASCII period/space, `.hidden` and `a.b` controls, unchanged fixed digest, unchanged directory/TF root spelling behavior, and embedded-NUL category preservation.

## Review history

The first GREEN fixed terminal directory syntax. Independent adversarial review then found two broader Win32 alias classes:

- trailing ASCII period/space on the final filename;
- the same normalization on ancestor components.

Each finding was converted into deterministic RED coverage before the corresponding production hardening.

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

Exact-file identity needs a lexical portability boundary independent of host filesystem normalization. Reject Win32-ambiguous trailing ASCII period/space in every native path component, plus terminal directory syntax, before `lstat()`.