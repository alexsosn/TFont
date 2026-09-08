# F-014 plan — portable exact-file spelling boundary

## Gate order

Research is committed first in `docs/research/F-014-windows-exact-file-paths.md`. Initial production edits followed a tests-only RED commit. Adversarial review of the first GREEN identified Win32 trailing-period/space aliasing; research was extended from Microsoft primary documentation, new focused tests were committed RED against that first GREEN, and production was hardened again.

## Production change

In `src/tfont/parent_identity.py` keep one private lexical helper for exact-file spellings. It operates on the exact string returned by `_path_string()` and rejects before `_lstat()` when:

- the path ends in a native separator;
- the final component is `.`;
- the final component ends in ASCII period or ASCII space, which ordinary Win32 path handling can strip before opening.

`file_component_digest()` calls it after `_path_string()` and before `_lstat()`.

No directory/TF root code changes. No digest projection or algorithm identifiers change.

## RED evidence

Initial tests-only RED pinned terminal separators and terminal dot-segment rejection before filesystem inspection. Ubuntu cells failed the focused contract before production changed, proving the RED independently of Windows filesystem normalization. Existing I-003 coverage reproduced the concrete `<file>/.` defect on Windows.

The review extension then added deterministic pre-`lstat()` RED cases for trailing ASCII period/space against the first GREEN implementation before the second production hardening commit.

Focused controls cover:

- terminal native separator and repeated separators;
- terminal `.` segment;
- trailing ASCII period and ASCII space;
- `.hidden` and `a.b` accepted controls;
- unchanged exact-file digest;
- directory/TF equivalent-root spelling controls;
- embedded-NUL category control.

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

Fresh review over exact final SHA must attack over-rejection, Windows drive/UNC and `\\?\` implications, leading/internal dots, POSIX filenames that are intentionally excluded for portability, non-native separators, error category/path preservation, embedded-NUL behavior, and accidental changes to directory/TF root semantics.