# F-024 research — ownership-checker namespace scan failures

**Issue:** #121

## Question

How should `scripts/check_f_series_ownership.py` behave when it cannot enumerate or classify files in one of the F-series ownership namespaces?

The current checker has stable diagnostics for file-content reads, but directory discovery and entry classification use several `pathlib` APIs with different failure behavior. F-024 should make discovery failures deterministic without changing valid-repository behavior, F-021 compatibility, F-023 one-way authority semantics, or D-006 migration evidence.

## Scope

In scope:

- required research authority namespace `docs/research`;
- optional downstream plan namespace `docs/plans`;
- optional focused-workflow namespace `.github/workflows`;
- optional test-package namespace `tests`;
- failures while determining whether a namespace is a directory;
- failures while enumerating a present namespace;
- failures while classifying a discovered entry as file/directory;
- deterministic repository-relative diagnostics;
- Python 3.10/3.12 compatibility;
- F-021/F-023 callable and diagnostic compatibility.

Out of scope:

- symlink acceptance/rejection policy;
- filesystem race hardening beyond failure containment;
- Git index/history inspection;
- GitHub API access;
- automatic metadata repair;
- runtime/package/schema/digest/ontology behavior.

Symlinks remain governed by current `pathlib` behavior for this ticket. A separate ticket is appropriate if the project wants a no-symlink repository-metadata policy.

## Current implementation audit

At `main=0f6d09fbdae5754fb874c7b6d08539218648aa66`, the checker has four relevant discovery patterns.

### Research authority

`_scan_research_repository()`:

1. calls `research_dir.is_dir()`;
2. calls `research_dir.glob("F-[0-9][0-9][0-9]-*.md")`;
3. filters candidates with `path.is_file()`;
4. catches `(OSError, UnicodeError, ValueError)` only around `read_text()`.

A failure from `is_dir()`, enumeration, or `is_file()` is outside the stable diagnostic boundary.

### Plans

`_check_downstream()`:

1. calls `plans_dir.is_dir()`;
2. calls `plans_dir.glob("F-[0-9][0-9][0-9]-*.md")`;
3. filters with `path.is_file()`;
4. `_check_plan()` catches only content-read failures.

### Workflows

`_check_downstream()`:

1. calls `workflows_dir.is_dir()`;
2. enumerates `workflows_dir.iterdir()`;
3. filters with `path.is_file()`;
4. `_check_workflow()` catches only content-read failures.

### Test packages

`_check_downstream()`:

1. calls `tests_dir.is_dir()`;
2. enumerates `tests_dir.iterdir()`;
3. filters with `package.is_dir()`;
4. `_check_test_package()` calls `sidecar.is_file()` before the content-read boundary.

The surfaces therefore do not currently share one discovery-failure contract.

## Python filesystem API evidence

Python 3.12 `pathlib` documentation states:

- `Path.iterdir()` raises `OSError` if the directory is inaccessible;
- `Path.is_file()` and `Path.is_dir()` return `False` for absence/broken symlinks but propagate other errors such as permission errors;
- `Path.glob()` calls `Path.is_dir()` for the top-level directory and propagates that error, but subsequent `OSError` exceptions while scanning directories are suppressed.

Reference:

- https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.iterdir
- https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.glob
- https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_file
- https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_dir

This matters even though F-series matching is only one directory level deep. The checker needs to know whether enumeration succeeded; a suppressed scan failure must not be indistinguishable from a genuinely empty namespace.

Python 3.10 is also a supported repository-test runtime, so implementation should use APIs available there. `Path.iterdir()`, `is_file()`, and `is_dir()` satisfy that compatibility requirement; no 3.12-only `Path.walk()` API is needed.

## Failure classes

There are three distinct operations and they should not be conflated.

### 1. Namespace classification/access

Examples:

- checking whether `docs/research` is a directory;
- checking whether optional `docs/plans`, `.github/workflows`, or `tests` exists as a directory.

A filesystem exception here means the checker cannot determine namespace state.

### 2. Namespace enumeration

Examples:

- obtaining children from `.github/workflows`;
- obtaining candidate research files.

A filesystem exception here means the checker cannot prove completeness of that namespace.

### 3. Entry classification

Examples:

- determining whether a matching child is a regular file;
- determining whether `tests/fNNN` is a directory;
- determining whether `tests/fNNN/issue-owner.txt` is a regular file.

A filesystem exception here means a concrete repository-relative candidate cannot be classified safely.

Content `read_text()` failures are already represented as `read_error` and should stay distinct.

## Required versus optional namespaces

The research authority namespace has stronger semantics than downstream namespaces.

### Research authority

`docs/research` is required and is the sole allocation authority. If its namespace cannot be classified, enumerated, or completely classified, downstream relationship checks are not trustworthy.

Recommendation: treat a research namespace discovery failure as a **global authority failure**. Preserve any already-known stable diagnostics, but do not scan downstream relationships after the authority set may be incomplete.

### Downstream namespaces

Plans, workflows, and tests are optional collections. A genuinely absent namespace is still an empty namespace and remains valid.

However, “absent” and “present but unscannable” are different. If a downstream namespace exists but cannot be classified/enumerated completely, emit a stable diagnostic and continue scanning other independent downstream namespaces where possible. The overall checker exits nonzero.

This preserves the F-023 rule that research-only features are valid while preventing filesystem failure from masquerading as “no downstream claims”.

## Diagnostic contract recommendation

Introduce one repository-scan diagnostic family distinct from content reads:

`scan_error: <repository-relative-path>: <ExceptionType>`

Examples:

- `scan_error: docs/research: PermissionError`
- `scan_error: .github/workflows: OSError`
- `scan_error: tests/f024: PermissionError`

Rationale:

- `read_error` already means bytes/text for a known carrier could not be read;
- `scan_error` means the checker could not establish the namespace/candidate set or classify an entry;
- exception type is stable across runs while exception text may contain platform-specific paths/messages;
- repository-relative paths match existing diagnostics.

Do not reuse `authority_error` for arbitrary OS failures. Existing `authority_error: docs/research: missing_or_not_directory` and `authority_error: docs/research: no_f_series_artifacts` describe semantic namespace states that were successfully observed. A scan failure means the state could not be observed reliably.

## Enumeration architecture recommendation

Replace one-level `Path.glob()` enumeration used by research/plans with explicit one-level deterministic enumeration shared with workflows/tests.

A private helper should conceptually:

1. determine whether the namespace is a directory under a caught filesystem boundary;
2. if genuinely absent/non-directory, return the caller-specific semantic state;
3. call `iterdir()` under a caught filesystem boundary;
4. sort child paths lexically;
5. let the caller apply its exact filename regex;
6. classify relevant matching entries under a caught filesystem boundary;
7. return children plus stable scan diagnostics rather than raising.

This avoids `Path.glob()` scan-error suppression and makes all four namespace surfaces use one explicit failure model.

The helper should not recursively walk the repository.

## Entry-classification policy

Only matching/in-scope entries need classification failures reported.

For example, an inaccessible unrelated `.github/workflows/release.yml` is outside the `fNNN-*` ownership namespace and should not create F-024 noise merely because the checker enumerated it. Apply the lexical filename/directory-name regex before a potentially failing `is_file()` / `is_dir()` where possible.

For test packages, direct child name `fNNN` establishes that the entry is in scope before `is_dir()` classification.

For the expected test sidecar, `tests/fNNN/issue-owner.txt` is an in-scope carrier path. Failure of `is_file()` for that path should be a scan/classification error rather than being converted to `missing_owner`.

## Diagnostic precedence

Recommended precedence:

1. namespace-level scan/classification failure;
2. entry-level scan/classification failure;
3. content `read_error`;
4. local metadata structural diagnostics;
5. relationship diagnostics.

A concrete operation should generate one root-cause diagnostic rather than additional downstream noise caused by the unknown result.

For research authority:

- any scan failure that could make the authority set incomplete sets global authority failure;
- downstream scanning is skipped.

For a downstream namespace:

- a namespace scan failure suppresses claims from that namespace because completeness is unknown;
- other downstream namespaces may still be checked;
- an entry-classification failure suppresses only that entry's missing/relationship diagnostics.

## Callable compatibility

Preserve F-021/F-023 compatibility:

- `check_artifacts(artifacts)` remains unchanged and research-only;
- public-to-tool `scan_repository(root)` retains `(research_artifacts, diagnostics)`;
- `check_repository(root)` gains stable scan diagnostics but keeps `list[str]`;
- CLI remains silent on success, diagnostics on stderr, exit 0/1;
- existing exact diagnostics for successfully enumerated malformed/missing/conflicting/read-error cases remain unchanged.

Private helper return shapes may change as needed.

## RED strategy

Do not rely on real chmod/ACL behavior. CI runners, Windows, container ownership, and elevated privileges make permission tests unreliable.

Use deterministic injection with `unittest.mock` around the filesystem seam selected by the plan.

RED should independently demonstrate current failures for at least:

1. research namespace classification raises `OSError` -> current raw exception; desired global `scan_error`;
2. research enumeration raises `OSError` -> desired global `scan_error`, no downstream relationship avalanche;
3. matching research entry `is_file()` raises -> desired global `scan_error` at the entry path;
4. optional plans namespace enumeration raises -> desired local `scan_error`, workflows/tests still evaluated;
5. workflows enumeration raises -> desired local `scan_error`;
6. matching workflow entry `is_file()` raises -> desired entry `scan_error`;
7. tests enumeration raises -> desired local `scan_error`;
8. matching `tests/fNNN` `is_dir()` raises -> desired entry `scan_error`;
9. expected test sidecar `is_file()` raises -> desired sidecar `scan_error`, not `missing_owner`;
10. existing `read_error`, malformed/duplicate/missing/conflict/unknown behavior remains green.

The tests should assert exact stable diagnostics and explicitly prove unrelated downstream namespaces remain observable when another optional namespace fails.

Run focused tests on Python 3.10 and 3.12. These are semantic/pathlib compatibility tests; an OS matrix is unnecessary when failures are injected above the OS syscall layer.

## Rejected alternatives

### Keep `glob()` and catch only outer exceptions

Rejected because Python documents suppression of later scan errors inside `Path.glob()`. A caller cannot reliably catch an exception that `glob()` intentionally hides.

### Treat scan failures as empty namespaces

Rejected because that converts inability to inspect the repository into successful absence, defeating ownership enforcement.

### Use chmod-based permission fixtures

Rejected because behavior depends on runner OS, ACLs, ownership, and privilege level.

### Use `Path.walk()`

Rejected because recursive traversal is unnecessary and `Path.walk()` is not available on Python 3.10.

### Add symlink rejection here

Rejected as scope expansion. Current F-024 evidence concerns error containment, not a settled security policy for repository symlinks.

## Recommendation

Proceed with a narrow implementation plan that:

1. introduces deterministic one-level namespace enumeration using Python-3.10-compatible primitives;
2. reports `scan_error: <relative-path>: <ExceptionType>` for caught namespace/entry classification failures;
3. treats research discovery scan failure as global authority failure;
4. treats downstream namespace/entry scan failure as local while continuing independent namespaces;
5. preserves existing F-021/F-023 public callable shapes and successful-path diagnostics;
6. proves behavior with injected tests-only RED before editing the checker;
7. runs F-021, F-023, D-006, direct checker, and full-suite regressions before final review.

## Acceptance trace

- mixed `glob`/`iterdir` behavior audited: yes;
- upstream Python behavior verified: yes;
- required/global versus optional/local semantics decided: yes;
- diagnostic family decided: yes;
- deterministic portable RED strategy decided: yes;
- callable compatibility frozen: yes;
- symlink policy explicitly excluded: yes.
