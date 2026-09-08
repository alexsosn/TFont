# F-014 plan — reject terminal directory syntax for exact files

## Gate order

Research is committed first in `docs/research/F-014-windows-exact-file-paths.md`. Production edits must follow a tests-only RED commit.

## Production change

In `src/tfont/parent_identity.py` add one private lexical helper for exact-file spellings. It must operate on the exact string returned by `_path_string()` and return/reject based only on terminal native directory syntax.

`file_component_digest()` calls it after `_path_string()` and before `_lstat()`.

No directory/TF root code changes. No digest projection or algorithm identifiers change.

## Required RED

Add `tests/f014/test_exact_file_path_spelling.py` before production edits. Pin:

- terminal native separator;
- terminal `/.` or `\\.` according to host separator;
- terminal dot segment followed by separator;
- repeated terminal separators;
- ordinary dotted filenames as negative controls;
- unchanged exact-file digest;
- directory/TF equivalent-root spelling controls;
- embedded-NUL category control.

The private lexical-helper assertions must fail on current main on every host because the helper does not exist. The existing public I-003 `<file>/.` test supplies the Windows-specific behavioral RED in CI.

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

Fresh review over exact final SHA must attack over-rejection, Windows drive/UNC implications, ordinary dotted filenames, non-native separators, error category/path preservation, embedded-NUL behavior, and accidental changes to directory/TF root semantics.