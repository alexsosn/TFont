# F-014 plan — portable exact-file spelling boundary

## Gate order

Research was committed before the initial implementation plan. Initial production edits followed tests-only RED. Adversarial review then identified additional Win32 alias classes; each was researched from Microsoft primary documentation, converted into deterministic RED coverage, and only then hardened in production.

## Production change

`src/tfont/parent_identity.py` has one private lexical helper for exact-file spellings. It operates on the exact string returned by `_path_string()` and rejects before `_lstat()` when:

- the path ends in a native separator; or
- any non-empty native path component ends in ASCII period or ASCII space.

The latter includes a `.` component and applies to ancestors as well as the final filename, because ordinary Win32 normalization can alias either.

`file_component_digest()` calls the helper after `_path_string()` and before `_lstat()`.

No directory/TF root code changes. No digest projection or algorithm identifiers change.

## RED evidence

Initial tests-only RED pinned terminal separators and terminal dot-segment rejection before filesystem inspection. Ubuntu cells failed the focused contract before production changed, proving RED independently of Windows normalization. Existing I-003 coverage reproduced the concrete `<file>/.` defect on Windows.

Review-driven RED stages then pinned:

1. final filename ending in ASCII period/space against the first GREEN;
2. ancestor components ending in ASCII period/space against the second GREEN.

Production hardening followed each RED stage.

Focused controls cover leading/internal periods, unchanged exact-file digest, directory/TF equivalent-root spellings, and embedded-NUL category preservation.

## CI

Focused workflow matrix:

- Ubuntu + Windows;
- Python 3.10 + 3.12;
- `tests/f014`;
- `tests/i003`.

Repository-wide discovery remains owned only by `full-suite.yml`.

## GREEN acceptance

- all focused tests green on all four matrix cells;
- full suite green on exact head;
- exact-file fixed digest unchanged;
- directory/TF root spellings unchanged;
- no F-012 production code included in this PR.

## Independent review

Fresh review over exact final SHA must attack over-rejection, Windows drive/UNC and `\\?\` implications, leading/internal dots, POSIX filenames intentionally excluded for portability, ancestor aliases, non-native separators, error category/path preservation, embedded-NUL behavior, and accidental changes to directory/TF root semantics.