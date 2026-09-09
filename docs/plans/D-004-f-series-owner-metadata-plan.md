# D-004 plan — backfill F-series research ownership metadata

**Issue:** #104  
**Research:** `docs/research/D-004-f-series-owner-metadata-audit.md`  
**Baseline:** `main` `a09e9d6512877ac5f8c90d4f3887d16908833916`

## Goal

Repair exactly four historical metadata omissions so every audited primary F-series research report has one machine-readable issue owner before F-021 implements a generic uniqueness checker.

This is documentation/repository-state work only. No production, schema, digest, runtime, research conclusion, historical filename, or feature namespace may change.

## Frozen migration

The reviewed audit fixes the complete migration set:

| Primary research report | Required owner header |
|---|---|
| `docs/research/F-012-file-hash-object-binding.md` | `**Issue:** #80` |
| `docs/research/F-014-windows-exact-file-paths.md` | `**Issue:** #84` |
| `docs/research/F-016-custom-schema-recursion-boundary.md` | `**Issue:** #88` |
| `docs/research/F-017-inplace-file-mutation.md` | `**Issue:** #91` |

No fifth primary report is in scope. `F-019-cpython-path-conversion-evidence.md` remains a supporting evidence note and must not receive an independent owner header in D-004.

## Metadata edit shape

For each of the four reports:

1. preserve the existing title byte-for-byte;
2. insert one Markdown metadata line `**Issue:** #N  ` immediately after the title block, separated consistently from the first existing section/metadata;
3. preserve all remaining historical prose byte-for-byte.

The final four research-file patches must therefore contain one added metadata line each and no deletion/rewrite of existing research text.

## RED contract

Before editing any of the four research reports, add:

- `tests/d004/__init__.py`;
- `tests/d004/test_f_series_owner_metadata_migration.py`;
- `.github/workflows/d004-f-series-owner-metadata.yml`.

The focused test must use the frozen four-file mapping above and assert for each target:

- the expected exact `**Issue:** #N` line occurs exactly once;
- no second `**Issue:** #...` owner line exists in that report;
- the document still begins with its existing `# F-NNN` title.

On the plan-reviewed baseline, RED must fail on the four missing expected owner headers. It must not modify or inspect Git history/GitHub at runtime.

Controls must demonstrate that:

- an already-owned neighboring primary report (for example F-013) is not part of the migration set and already has exactly one owner;
- the F-019 supporting evidence note remains excluded from the migration set;
- the migration mapping contains exactly four files and four distinct authoritative issue numbers.

Do **not** implement the future generic F-021 namespace/primary-classifier checker here. The D-004 test is a finite migration contract, not a permanent feature registry.

## GREEN

After observing a clean tests-only RED:

- add only the four required `**Issue:**` lines;
- do not edit research conclusions or supporting evidence notes;
- do not add production code.

No automatic script is needed for four deterministic one-line edits.

## CI

Focused workflow:

- Ubuntu 24.04;
- Python 3.10 and 3.12;
- install editable package only to preserve repository CI conventions;
- run `python -m unittest discover -s tests/d004 -v`;
- run existing `python -m unittest discover -s tests/research -v` as regression coverage.

Repository-wide discovery remains owned by `.github/workflows/full-suite.yml`; D-004 must not duplicate the full suite inside its focused workflow.

Final exact-head merge gate requires:

1. focused D-004 green on Python 3.10/3.12;
2. existing research regressions green;
3. authoritative full repository suite green on Python 3.10/3.12;
4. PR diff confirms the four historical reports have only one-line metadata additions;
5. fresh logically-independent adversarial review of the exact final SHA;
6. unchanged head at merge time.

## Independent review targets

The final reviewer must independently attack:

- wrong issue number assigned to any of the four reports;
- accidental fifth migration target;
- duplicate `**Issue:**` lines;
- accidental edits to historical research prose;
- accidental owner header on the F-019 supporting evidence note;
- leakage of F-021 implementation into D-004;
- stale branch/base or unreviewed head movement.

## Cleanup / branch hygiene

The superseded `chore/f-021-owner-metadata-migration` branch began plan/RED work before the required D-004 research gate and was reset to the current main before this plan branch was created. After D-004 merges, this implementation branch should likewise be aligned with main so no divergent owner-metadata branch remains without active work.

## Non-goals

- no F-021 checker implementation;
- no runtime GitHub API dependency;
- no automatic renumbering or filename cleanup;
- no research-content rewrite;
- no attempt to make metadata immutable beyond what later F-021 CI will enforce.