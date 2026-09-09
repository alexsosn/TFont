# F-021 implementation plan — enforce unique F-series research ownership

**Issue:** #99  
**Research:** `docs/research/F-021-feature-id-uniqueness.md` + `docs/research/F-021-post-d004-reconciliation.md`  
**Baseline:** `main` `696b2c050e9d8fca518a9a129a11760d30e5c3b0`  
**Type:** repository ergonomics / merge-time invariant

## 1. Goal

Add a deterministic, directly runnable repository checker that prevents one `F-NNN` research namespace from carrying multiple GitHub issue owners and rejects invalid/missing ownership metadata before merge.

The checker operates only on current checked-out repository state. It does not use Git history, a hand-maintained feature registry, or the GitHub API.

## 2. Frozen authority surface

F-021 v1 scans every regular file matching:

```text
docs/research/F-[0-9][0-9][0-9]-*.md
```

The `F-NNN` prefix in the filename is the feature identifier. There is no primary/supporting/evidence exemption.

Research artifacts are allocation authority. Multiple same-ID artifacts are legal only when every valid artifact declares the same issue owner.

F-021 v1 does **not** infer issue ownership from `docs/plans`, workflow filenames, or `tests/fNNN` paths. Follow-up issue #112 owns research for richer downstream ownership metadata.

## 3. Implementation location and public repository-tool surface

Create:

- `scripts/check_f_series_ownership.py`
- `tests/f021/__init__.py`
- `tests/f021/test_feature_id_ownership.py`
- `.github/workflows/f021-feature-id-ownership.yml`

No `src/tfont/**`, schema, package metadata, digest, semantic-validator, runtime, or ontology file is in scope.

The script is repository tooling rather than an installed TFont API. It must remain directly executable with the repository Python:

```bash
python scripts/check_f_series_ownership.py
```

It must also expose pure functions that tests can load by file path without making `scripts` an installed/importable package.

Planned functions:

```python
check_artifacts(artifacts: Mapping[str, str]) -> list[str]
scan_repository(root: Path) -> dict[str, str]
check_repository(root: Path) -> list[str]
main(argv: Sequence[str] | None = None) -> int
```

`artifacts` maps repository-relative paths to UTF-8 Markdown content. Returned diagnostics are already sorted strings.

The CLI accepts at most one optional repository-root positional argument. With no argument, the default root is `Path(__file__).resolve().parents[1]`. It prints one diagnostic per line to stderr and exits `1` when diagnostics exist; it prints nothing and exits `0` on success. Invalid CLI argument count may use `argparse`'s standard exit behavior and is not part of the ownership contract.

## 4. Filename and enumeration contract

`scan_repository(root)`:

1. resolves only `root / "docs" / "research"` as the authority directory;
2. enumerates `F-[0-9][0-9][0-9]-*.md` entries;
3. includes regular files only;
4. stores repository-relative POSIX-style paths such as `docs/research/F-019-...md`;
5. reads UTF-8 text;
6. returns entries in no semantically significant order; `check_artifacts()` is responsible for deterministic sorting.

Filesystem/read failures must not be silently ignored. The checker should convert an expected repository read failure into a deterministic diagnostic of the form:

```text
read_error: <path>: <ExceptionClass>: <message>
```

The implementation must not catch process-fatal exceptions broadly. Ordinary `OSError`, `UnicodeError`, and path-value failures at this repository-read boundary are sufficient.

Unrelated R/P/I/A/D research files are outside enumeration and ignored.

## 5. Bounded ownership metadata grammar

For each F-series artifact, inspect a bounded header region only:

- physical lines 2 through 12 inclusive (line 1 is the H1/title position);
- stop earlier at the first line beginning exactly `## `;
- body prose after that boundary is never ownership metadata.

A canonical owner line is:

```text
**Issue:** #<positive decimal integer>
```

with optional trailing whitespace only.

Canonical regex:

```regex
^\*\*Issue:\*\* #([1-9][0-9]*)\s*$
```

### Owner-like malformed lines

Within the bounded header region, **any** line whose left-stripped text begins with `**Issue:**` but does not match the canonical regex is malformed ownership metadata.

This includes, for example:

- `**Issue:** #0`
- `**Issue:** 99`
- `**Issue:** #abc`
- ` **Issue:** #99` (leading indentation is not canonical)
- `**Issue:** #99 extra`

A file containing one canonical owner plus one malformed owner-like line is still invalid. Malformed metadata cannot be hidden by also supplying a valid line.

Lines elsewhere containing `#99`, `Issue`, or prose references do not count unless they are owner-like inside the bounded header region.

## 6. Per-artifact validity contract

For each scanned path, ownership is valid only when:

1. there are zero malformed owner-like header lines; and
2. there is exactly one canonical owner line.

Diagnostics are frozen as follows:

- no canonical owner and no malformed owner-like line:
  `missing_owner: <path>`
- one or more malformed owner-like lines:
  one diagnostic per malformed physical line:
  `malformed_owner: <path>:<line>: <repr(line_text)>`
- two or more canonical owner lines, regardless of whether values match:
  `duplicate_owner: <path>: lines <comma-separated line numbers>`

When an artifact has any malformed or duplicate-owner diagnostic, it contributes no owner to cross-artifact conflict grouping. This prevents a syntactically invalid file from manufacturing secondary conflict noise.

If an artifact has malformed lines and zero canonical owners, do not additionally emit `missing_owner`; malformed diagnostics are sufficient and more specific.

If an artifact has malformed lines plus multiple canonical owners, emit malformed diagnostics and the duplicate-owner diagnostic; do not use the artifact for conflict grouping.

## 7. Cross-artifact ownership contract

After validating artifacts independently, group valid artifacts by filename-derived `F-NNN`.

If one feature ID has more than one distinct issue number among valid artifacts, emit exactly one deterministic conflict diagnostic:

```text
conflicting_owner: F-NNN: #<issue>=<path>[,<path>...]; #<issue>=<path>[,<path>...]
```

Issue groups are sorted numerically; paths within each issue group are lexically sorted.

Same-feature/same-owner multi-artifact groups pass.

## 8. Global determinism

`check_artifacts()` returns the complete diagnostic list sorted lexically after all per-artifact and conflict diagnostics are generated.

Synthetic tests must permute input dictionary insertion order and still receive byte-identical diagnostic ordering.

The checker must not depend on filesystem enumeration order, locale, Git state, network state, issue titles, or timestamps.

## 9. Tests-only RED

Before `scripts/check_f_series_ownership.py` exists, add `tests/f021/**` and the focused workflow only. Do not add an empty/placeholder checker.

The test module should have two classes:

### `RepositoryMetadataControls`

These controls do not import the planned checker. They independently establish the post-D-004 prerequisite state:

- every current F-series research artifact has one canonical owner in the reviewed bounded region;
- no current same-ID group has multiple owner values;
- F-019 primary and CPython evidence both carry #94;
- no unexpected headerless artifact exists.

These controls must pass on the tests-only RED head.

### `FeatureOwnershipCheckerREDTests`

These load `scripts/check_f_series_ownership.py` by exact file path using `importlib.util`. On RED, loading must fail because the checker file does not exist.

Once GREEN adds the checker, the same tests exercise the planned contract with synthetic temporary/input mappings and the real repository.

Required intended cases after the module becomes loadable:

1. different owners under one F ID -> one `conflicting_owner` failure;
2. same owner under one F ID -> pass;
3. new F ID with one canonical owner -> pass;
4. missing owner -> `missing_owner`;
5. duplicate same owner lines -> `duplicate_owner`;
6. duplicate different owner lines -> `duplicate_owner` and no conflict from that invalid artifact;
7. malformed owner alone -> `malformed_owner`, no redundant `missing_owner`;
8. malformed owner plus canonical owner -> still `malformed_owner`;
9. malformed plus duplicate canonical -> both malformed and duplicate diagnostics, no conflict grouping from that file;
10. body prose issue mention after `## ` does not count;
11. owner on physical line 12 is accepted; line 13 is outside the contract;
12. first `## ` stops metadata scanning earlier;
13. unrelated namespace paths supplied to `check_artifacts()` are ignored or rejected according to the function's documented input precondition; repository enumeration itself must never include them;
14. diagnostics are stable across input order;
15. `check_repository(current_root)` passes on the post-D-004 tree;
16. CLI exits `0` and is silent on current repository;
17. CLI on a temporary synthetic repository with a conflict exits `1` and prints the sorted diagnostic.

The RED workflow is valid only when repository metadata controls pass and intended checker tests fail because the planned checker file/API is absent—not because current ownership metadata is broken.

## 10. Focused workflow

Create `.github/workflows/f021-feature-id-ownership.yml`.

Matrix:

- Ubuntu 24.04
- Python 3.10
- Python 3.12

Steps:

1. checkout exact PR/source head;
2. setup Python;
3. run repository metadata controls;
4. run intended F-021 checker tests;
5. under `if: always()`, run D-004 repository-state ownership tests as a migration regression;
6. under `if: always()`, run `python scripts/check_f_series_ownership.py` once the checker exists; on the RED head this step may be conditionally skipped by file-existence guard so RED attribution remains the intended test module absence.

Repository-wide discovery remains owned only by `.github/workflows/full-suite.yml`.

Workflow triggers cover:

- `docs/research/F-*.md`
- `docs/research/F-021-*.md`
- `docs/plans/F-021-*.md`
- `scripts/check_f_series_ownership.py`
- `tests/f021/**`
- `tests/d004/**`
- `.github/workflows/f021-feature-id-ownership.yml`

## 11. Minimal GREEN

After valid RED evidence, add only `scripts/check_f_series_ownership.py` as the implementation needed to make the intended tests pass.

Do not weaken/change RED assertions unless a test defect is independently demonstrated. Any new production/runtime TFont code is out of scope.

If the checker needs no third-party dependencies, do not add any.

## 12. Documentation / contributor ergonomics

After core GREEN, update `CONTRIBUTING.md` in a separate docs-only substep driven by a failing docs/static assertion added **before** the documentation change.

The contributor rule should state concisely:

- new `docs/research/F-NNN-*.md` artifacts require exactly one canonical `**Issue:** #N` header;
- same F ID may have multiple research/evidence/amendment artifacts only when all share the same issue owner;
- run `python scripts/check_f_series_ownership.py` before opening/finalizing a PR.

This documentation substep must not alter checker semantics. If current `CONTRIBUTING.md` already states the exact rule sufficiently, document the finding in the PR and skip the change rather than duplicating it.

## 13. Exact-head regression gate

Before final review require:

- focused F-021 Python 3.10/3.12 green;
- D-004 ownership regression green;
- authoritative full repository suite green on Python 3.10/3.12;
- F-007 single-full-suite ownership green;
- F-011 Node-24 action-major policy green;
- direct CLI invocation green on exact head;
- compare against then-current `main` contains only F-021 research amendment, plan, tests/workflow, repository checker, and any separately TDD-gated CONTRIBUTING change;
- no `src/**`, schemas, package metadata, digest/runtime/semantic code, or unrelated docs changes.

If `main` moves, integrate current main and rerun exact-head CI. Re-scan current F-series research ownership after integration; a newly added artifact must satisfy the checker rather than be added to an allowlist.

## 14. Fresh independent adversarial review

Final review must attack at least:

- primary/supporting exemption accidentally reintroduced;
- malformed owner-like lines accepted because one canonical line also exists;
- duplicate same-owner lines accepted;
- invalid artifacts participating in conflict grouping and producing misleading extra diagnostics;
- body prose or line-13 owner references counted as metadata;
- nondeterminism from dict/filesystem ordering;
- conflict formatting/order instability;
- missing read-error containment;
- CLI exit/output contract;
- use of Git, GitHub API, registry, or hidden allowlist;
- downstream workflow/test owner claims leaking into v1 despite lack of metadata;
- accidental TFont runtime/package changes;
- current-main integration drift.

Any blocker returns to the earliest affected research/plan/RED/GREEN gate.

## 15. Exit condition

F-021 completes when the checked-out repository can deterministically enforce exactly one valid issue owner per F-series research artifact and exactly one owner per F ID through a directly runnable pure-Python checker and CI gate, with no registry/network/history dependency, focused/full exact-head CI green, and fresh logically-independent adversarial review approving the exact final head.
