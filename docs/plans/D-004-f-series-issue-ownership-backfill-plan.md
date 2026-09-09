# D-004 implementation plan — backfill F-series research issue ownership

**Issue:** #104  
**Research:** `docs/research/D-004-f-series-issue-ownership-backfill.md`  
**Baseline:** `main` `6934649ae64c1df60032240d1a82a350c509e77a`

## 1. Goal

Make issue ownership complete and machine-readable across the current `docs/research/F-NNN-*.md` namespace so F-021 can later enforce its accepted current-tree uniqueness invariant without a permanent legacy allowlist.

This ticket is a repository-metadata migration. It does not implement F-021's reusable checker.

## 2. Frozen migration set

Only these five existing artifacts receive metadata edits:

| Artifact | Owner |
| --- | --- |
| `docs/research/F-012-file-hash-object-binding.md` | `#80` |
| `docs/research/F-014-windows-exact-file-paths.md` | `#84` |
| `docs/research/F-016-custom-schema-recursion-boundary.md` | `#88` |
| `docs/research/F-017-inplace-file-mutation.md` | `#91` |
| `docs/research/F-019-cpython-path-conversion-evidence.md` | `#94` |

For each, insert exactly one canonical line below the H1 title:

```markdown
**Issue:** #N
```

plus the normal blank line before the existing content.

No existing prose, title, conclusion, baseline SHA, citation, filename, feature number, or already-present metadata may be rewritten.

## 3. Repository-state parser contract for D-004 RED/GREEN

Create `tests/d004/test_f_series_issue_ownership_backfill.py` as a migration contract, not production code.

Enumeration:

- include every regular file matching `docs/research/F-[0-9][0-9][0-9]-*.md` in the checked-out repository;
- derive the F ID only from the basename prefix;
- ignore R/P/I/A/D research namespaces.

Ownership parsing:

- inspect a bounded metadata region: lines after the H1 and before the first `## ` section heading, with a hard maximum of the first 12 physical lines;
- recognize only a full metadata line matching `**Issue:** #<positive decimal integer>` with optional Markdown trailing spaces;
- require exactly one matching owner line per F-series artifact after GREEN;
- a mention of `#N` in prose outside the bounded header is not ownership metadata.

Grouping:

- group every scanned artifact by F ID;
- multiple files for one F ID are legal only when every file declares the same owner;
- deterministic diagnostics/path lists must be sorted.

The D-004 test need not expose a reusable library API. F-021 may later extract/refactor the policy after its own plan/RED gate.

## 4. Tests-only RED

Before any of the five metadata files changes, add the D-004 test and focused workflow.

The RED contract must include:

1. `test_every_f_series_research_artifact_has_one_owner` — expected to fail on current main and report exactly the five headerless paths;
2. `test_feature_artifacts_have_consistent_owners` — all already-owned/current same-ID groups must remain non-conflicting; F-019 cannot be considered complete while its evidence note is headerless;
3. `test_backfill_targets_have_authoritative_expected_owners` — freeze the explicit map F-012/#80, F-014/#84, F-016/#88, F-017/#91, F-019/#94 and fail until the scanned artifacts expose those values;
4. parser fixture tests proving header ownership is bounded, duplicate header lines fail, prose issue mentions do not count, and same-ID/same-owner multi-file artifacts are legal;
5. deterministic sorted missing/conflict diagnostics independent of input order.

On the tests/workflow-only RED head:

- no `docs/research/F-*.md` file is edited;
- parser fixture/control tests are green;
- repository-state ownership completeness and exact backfill-map tests fail only because the five frozen artifacts lack headers.

If RED finds another headerless or conflicting current artifact, stop and return to research rather than add it opportunistically.

## 5. Focused workflow

Add `.github/workflows/d004-f-series-issue-ownership.yml`.

Run on Ubuntu 24.04 with Python 3.10 and 3.12 because the contract is pure Python/repository text and has no OS-specific filesystem semantics.

Steps:

1. exact-head checkout;
2. setup matrix Python;
3. run `python -m unittest discover -s tests/d004 -v`;
4. under `if: always()`, run any existing CI-policy/static ownership-related controls that become relevant once present;
5. repository-wide discovery remains owned by `full-suite.yml`.

Triggers should cover:

- `docs/research/F-*.md`;
- `tests/d004/**`;
- the D-004 plan/research artifacts;
- the focused workflow itself.

## 6. Minimal GREEN

Only after valid RED evidence, edit the five frozen research artifacts and insert their issue lines.

No Python production/source file, schema, package metadata, workflow outside D-004, or unrelated documentation changes are allowed.

The GREEN must make the unchanged D-004 repository-state tests pass without weakening parsing or hard-coding exemptions.

## 7. Regression / exact-head gate

Before final review require:

- focused D-004 Python 3.10 and 3.12 green;
- authoritative full repository suite green on supported Python versions;
- F-007 single-full-suite ownership and F-011 action-major policy green if triggered;
- compare against then-current `main` contains only:
  - D-004 research;
  - D-004 plan;
  - D-004 tests/workflow;
  - the five issue-header insertions;
- no changes under `src/**`, `schemas/**`, packaging/runtime/digest/semantic code, or unrelated docs.

If `main` moves, integrate/rebuild on current main and rerun exact-head CI. If a new `F-NNN` research artifact appears during integration, rerun the repository-state audit; do not assume the five-file set remains complete.

## 8. Independent adversarial review

Fresh exact-head review must attack at least:

- wrong issue number on any of the five files;
- accidental prose/history rewriting alongside the metadata insertion;
- a parser that counts issue mentions in body prose;
- a parser that ignores supporting evidence/amendment files;
- duplicate owner headers passing silently;
- same F ID with conflicting owners passing silently;
- an exemption/allowlist that would undermine F-021;
- hidden implementation of F-021 beyond the migration contract;
- new current-main F-series artifacts introduced after the research audit;
- full-suite/workflow ownership regressions.

Any blocker returns to the earliest affected gate.

## 9. Exit condition

D-004 completes when every current `docs/research/F-NNN-*.md` artifact declares exactly one owner, all same-ID artifacts agree, the five researched backfills match #80/#84/#88/#91/#94 exactly, metadata is the only change to those historical files, focused/full exact-head CI is green, and a fresh logically-independent review finds no blocker. At that point F-021 planning/implementation is unblocked.
