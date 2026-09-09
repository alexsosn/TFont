# F-024 implementation plan — contain ownership namespace scan failures

**Issue:** #121  
**Research:** `docs/research/F-024-ownership-namespace-scan-failures.md` and `docs/research/F-024-scan-exception-boundary-amendment.md`  
**Baseline:** `main` `0f6d09fbdae5754fb874c7b6d08539218648aa66`

## 1. Goal

Make F-series ownership namespace discovery fail deterministically when filesystem classification or enumeration fails, without changing valid-repository ownership semantics or F-021/F-023 public-to-tool compatibility.

The checker must never treat an unobservable ownership namespace as successfully empty and must not leak an injected `(OSError, ValueError)` from the reviewed scan/classification boundaries.

## 2. Phase ownership

### Plan phase

This file only after reviewed research.

### Tests-only RED

Add only:

- `tests/f024/__init__.py`;
- `tests/f024/issue-owner.txt` containing exactly `Issue: #121\n`;
- `tests/f024/test_ownership_namespace_scan_failures.py`;
- `.github/workflows/f024-namespace-scan-failures.yml` with `# Issue: #121` in its first 12 physical lines.

Do not edit `scripts/check_f_series_ownership.py` before exact RED evidence is recorded.

F-024 itself is a valid downstream claim while RED runs:

- research owns F-024 -> #121;
- this plan repeats #121;
- the focused workflow repeats #121;
- `tests/f024/issue-owner.txt` repeats #121.

Therefore F-021/F-023/D-006 controls must remain green during RED. Intended failures belong only to the new scan-failure contract.

### Minimal GREEN

Edit only:

- `scripts/check_f_series_ownership.py`.

No contributor-documentation change is required because F-024 changes failure containment, not contributor metadata syntax or commands.

## 3. Compatibility surface

Preserve exactly:

- `check_artifacts(artifacts) -> list[str]`, research-only;
- `scan_repository(root) -> tuple[dict[str, str], list[str]]`;
- `check_repository(root) -> list[str]`;
- `main(argv) -> int` and `python scripts/check_f_series_ownership.py [root]`;
- silent success;
- stderr diagnostics and exit 1 on checker failure;
- every existing F-021/F-023 diagnostic for successfully discovered files.

Private helper signatures may change.

## 4. Stable scan diagnostic

For namespace enumeration or filesystem classification failures, emit:

```text
scan_error: <repository-relative-path>: <ExceptionType>
```

Catch exactly:

```python
(OSError, ValueError)
```

Do not include exception text.

`UnicodeError` remains part of `_read_text()` / `read_error`; do not add it to the scan boundary.

Do not catch `Exception` broadly.

## 5. Private filesystem seam

Introduce a small private seam with two responsibilities.

### `_safe_kind(path, root, *, directory)`

Conceptual return:

```python
tuple[bool | None, str | None]
```

Behavior:

- when `directory=True`, call `path.is_dir()`;
- otherwise call `path.is_file()`;
- on success return `(True|False, None)`;
- on `(OSError, ValueError)` return `(None, "scan_error: <relative>: <ExceptionType>")`.

`None` means classification is unknown and must never be treated as absence.

### `_safe_children(directory, root)`

Conceptual return:

```python
tuple[list[Path] | None, str | None]
```

Behavior:

- call `directory.iterdir()`;
- materialize and lexically sort children;
- on `(OSError, ValueError)` return `(None, "scan_error: <relative>: <ExceptionType>")`.

No recursive walk.

These helpers are private. Exact names may vary during implementation only if the semantics and RED patch points stay equivalent.

## 6. Namespace discovery algorithm

For each namespace, use explicit one-level discovery. Do not use `Path.glob()` for F-series ownership enumeration after GREEN.

### Common sequence

1. safely classify the namespace path as a directory;
2. if classification errors, emit its `scan_error`;
3. if classification is known false, apply caller-specific absent/non-directory semantics;
4. safely enumerate children;
5. if enumeration errors, emit namespace `scan_error`;
6. sort children;
7. apply the namespace's lexical F-series filename/name regex **before** entry classification;
8. safely classify only matching entries;
9. on matching-entry classification error, emit entry `scan_error` and skip semantic processing for that entry;
10. process successfully classified in-scope entries using existing parser/read/relationship behavior.

Unrelated child names are not classified for F-024 purposes after enumeration and cannot create entry-level ownership diagnostics.

## 7. Research authority behavior

Namespace: `docs/research`.

Existing semantic states remain:

- known absent/non-directory -> `authority_error: docs/research: missing_or_not_directory`;
- known directory with a complete successful scan but zero regular matching F-series research files -> `authority_error: docs/research: no_f_series_artifacts`.

New behavior:

- namespace classification failure -> `scan_error: docs/research: <ExceptionType>`, global failure;
- namespace enumeration failure -> same namespace `scan_error`, global failure;
- matching research entry classification failure -> `scan_error: docs/research/<name>: <ExceptionType>`, global failure.

Any research scan error can make authority incomplete. `check_repository()` must not perform downstream relationship scanning when such a global scan failure occurs.

Public `scan_repository(root)` still returns the artifacts that were safely read plus diagnostics. It must not raise the reviewed scan exceptions.

## 8. Optional downstream behavior

Namespaces:

- `docs/plans`;
- `.github/workflows`;
- `tests`.

Known absence/non-directory remains an empty optional namespace, preserving F-023 behavior.

For each namespace independently:

- classification failure -> namespace `scan_error`; skip that namespace; continue other downstream namespaces;
- enumeration failure -> namespace `scan_error`; skip that namespace; continue others;
- matching entry classification failure -> entry `scan_error`; skip only that entry; continue other entries and namespaces.

The final checker remains nonzero because diagnostics are present.

### Plans

Lexically match `F-[0-9][0-9][0-9]-*.md` before safe `is_file()` classification.

### Workflows

Lexically match exact existing `fNNN-*.yml|yaml` regex before safe `is_file()` classification.

### Test packages

Lexically match direct child name `fNNN` before safe `is_dir()` classification.

After a test package is safely known to be a directory, safely classify its expected `issue-owner.txt` as a regular file.

- known `False` -> existing `missing_owner`;
- classification error -> sidecar `scan_error`, **not** `missing_owner`.

## 9. Diagnostic precedence and suppression

For one concrete path, preserve root-cause precedence:

1. `scan_error` for inability to enumerate/classify;
2. `read_error` for a known carrier that cannot be read/decode;
3. local malformed/duplicate/missing metadata;
4. relationship `unknown_feature` / downstream `conflicting_owner`.

Do not emit later diagnostics for a path whose scan/classification state is unknown.

Research scan failure is globally authoritative: no downstream relationship avalanche.

Optional downstream scan failure is local: independent namespaces and entries still produce their own legitimate diagnostics.

Final diagnostic ordering remains lexical via the existing repository-wide sorting convention.

## 10. Tests-only RED

Create deterministic temporary filesystem fixtures, then inject failures with `unittest.mock` only while invoking the real checker.

Do not use chmod, ACL manipulation, platform-specific filesystem mounts, subprocess races, or symlink behavior.

The permanent tests assert desired GREEN behavior. No RED-only expected value may remain after implementation.

Required tests:

### Research authority global failures

1. **research namespace classification OSError**
   - selectively make `Path.is_dir()` raise `PermissionError` for `docs/research`;
   - expect exactly `scan_error: docs/research: PermissionError`;
   - prove downstream orphan claims do not add `unknown_feature` noise.

2. **research enumeration OSError**
   - selectively make `Path.iterdir()` raise `OSError` for `docs/research`;
   - expect namespace `scan_error` only;
   - current pre-GREEN code may not exercise this seam because it uses `glob()`; absence of the expected diagnostic is valid RED attribution.

3. **research enumeration ValueError**
   - same as test 2 with `ValueError`;
   - pins the amended exception tuple.

4. **matching research entry classification OSError**
   - directory enumeration succeeds;
   - selectively make `is_file()` raise for one lexically matching F-series research entry;
   - expect entry `scan_error` and global downstream suppression.

### Optional plan namespace

5. **plans enumeration failure is local**
   - valid research authority;
   - plan `iterdir()` raises `OSError`;
   - a separately malformed workflow remains observable;
   - expect plan namespace `scan_error` plus workflow local diagnostic.

6. **matching plan entry classification failure is local**
   - `is_file()` raises only for one matching F-plan;
   - another matching workflow is still checked;
   - expect plan entry `scan_error` plus any independent workflow diagnostic.

### Workflow namespace

7. **workflow enumeration failure is local**
   - `iterdir()` raises for `.github/workflows`;
   - an independent missing test sidecar remains observable.

8. **matching workflow entry classification failure is local**
   - `is_file()` raises for one `fNNN-*.yml`;
   - expect workflow entry `scan_error` without relationship/missing noise for that path.

### Tests namespace

9. **tests enumeration failure is local**
   - `iterdir()` raises for `tests`;
   - an independent bad plan remains observable.

10. **matching test-package classification failure**
    - `is_dir()` raises for `tests/fNNN`;
    - expect `scan_error: tests/fNNN: <type>`.

11. **sidecar classification failure**
    - package directory is known valid;
    - `issue-owner.txt.is_file()` raises;
    - expect sidecar `scan_error`, explicitly not `missing_owner`.

### Controls

12. unrelated child names must not have `is_file()` / `is_dir()` classification injected or diagnosed after lexical filtering;
13. existing content `read_error` stays unchanged;
14. current real repository passes;
15. F-021 research-only callable tests remain unchanged;
16. F-023 downstream behavior remains unchanged;
17. D-006 migration regressions remain green.

Tests should assert exact diagnostic lists.

## 11. RED workflow

Add `.github/workflows/f024-namespace-scan-failures.yml`.

Metadata:

```yaml
# Issue: #121
```

within the first 12 physical lines.

Events:

- push on `research/f024-namespace-scan-failures`;
- pull requests touching:
  - `docs/research/F-*.md`;
  - `docs/plans/F-*.md`;
  - `.github/workflows/f*.yml`;
  - `.github/workflows/f*.yaml`;
  - `tests/f*/**`;
  - `scripts/check_f_series_ownership.py`;
  - `tests/f024/**`;
  - `docs/research/F-024-*.md`;
  - `docs/plans/F-024-*.md`;
  - `.github/workflows/f024-*.yml`.

Matrix:

- Ubuntu 24.04;
- Python 3.10;
- Python 3.12.

Steps:

1. exact-head checkout;
2. Python setup;
3. run `python -m unittest discover -s tests/f024 -v`;
4. `if: always()` run F-023 tests;
5. `if: always()` run F-021 tests;
6. `if: always()` run D-006 tests;
7. `if: always()` run `python scripts/check_f_series_ownership.py .`.

Do not run the generic repository-wide unittest command here; `full-suite.yml` owns it.

## 12. Valid RED evidence

Before editing the checker require:

- F-024 failures attributable to the new scan contract;
- research namespace/current `glob()` mismatch or raw classification error is visible in F-024 tests;
- workflow/tests current raw `iterdir()` / classification errors are visible as F-024 failures/errors;
- F-023 GREEN;
- F-021 GREEN;
- D-006 GREEN;
- direct checker GREEN on the real branch;
- no `scripts/check_f_series_ownership.py` diff on the RED head.

Both Python versions must demonstrate intended RED.

## 13. Minimal GREEN

Edit only `scripts/check_f_series_ownership.py`.

Implementation should:

- add the reviewed safe filesystem seam;
- replace F-series research/plan `glob()` enumeration with explicit one-level enumeration;
- route workflows/tests through the same safe semantics;
- safely classify the expected test sidecar;
- preserve all existing parser and relationship logic;
- preserve public callable shapes;
- preserve existing diagnostics where discovery succeeds.

No dependency change.

## 14. Integration and regression gate

Before final review require:

- F-024 Python 3.10/3.12 GREEN;
- F-023 GREEN;
- F-021 GREEN;
- D-006 GREEN;
- direct ownership checker GREEN;
- authoritative full repository suite GREEN on Python 3.10/3.12;
- F-007/F-011 CI policy GREEN where triggered;
- compare against current `main` is limited to F-024 research/plan/tests/workflow and checker implementation;
- branch is zero behind current main.

If main moves, integrate and rerun exact-head gates. If ownership namespace structure or semantics changed, return to the earliest affected research/plan gate rather than adding an exception.

## 15. Final adversarial review

Review exact final head and attack at least:

- scan failure accidentally treated as absence;
- downstream scan failure accidentally made global;
- research scan failure allowing downstream relationship noise;
- `glob()` still used for authority/plan F-series enumeration;
- unrelated entries being classified/diagnosed;
- `ValueError` omitted from scan boundary;
- `UnicodeError` incorrectly moved from read to scan boundary;
- sidecar classification failure becoming `missing_owner`;
- duplicate/malformed/read/conflict diagnostics changed on successful scans;
- F-021 `scan_repository()` return shape changed;
- focused workflow duplicating full-suite ownership;
- symlink policy or runtime scope creeping into F-024.

Any material repair requires exact-head CI and fresh review.

## 16. Exit condition

F-024 completes when filesystem failures during ownership namespace discovery/classification produce deterministic `scan_error` diagnostics instead of raw exceptions or silent omission, required research failures stop relationship checking, optional downstream failures remain local, and all existing ownership behavior remains green.
