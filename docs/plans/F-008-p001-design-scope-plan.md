# F-008 plan: scope P-001's design-only invariant to the design change

**Status:** implementation-ready  
**Issue:** #66  
**Recorded:** 2026-09-07  
**Depends on:** `docs/research/F-008-p001-design-scope.md`

## Goal

Repair the stale P-001 test without weakening the historical design-only boundary.

## Decision

Replace the current repository-state assertion with a deterministic changed-path scope contract.

A P-001 design-only change is invalid when its changed-path set contains any path under:

- `src/`
- `schemas/`
- `profiles/`

The helper is test-support code only. It does not inspect the live repository tree except for a control asserting that current legitimate implementation paths may exist.

## TDD sequence

### RED

Add focused F-008 tests before changing the stale P-001 contract. The RED tests require a not-yet-implemented helper and pin two behaviors:

1. current repository `src/` may exist while the historical PR #13 changed-path set remains design-only;
2. synthetic design changes touching `src/**`, `schemas/**`, or `profiles/**` are rejected.

The focused RED workflow must fail because the helper does not yet exist / the old contract remains repository-state based.

### GREEN

Implement the smallest test-support helper and replace `test_design_ticket_contains_no_production_artifacts` so it evaluates changed paths rather than `Path.exists()` on current production directories.

Use the actual historical P-001 PR #13 changed paths as a stable fixture:

- `.github/workflows/p001-plan-validation.yml`
- `docs/plans/P-001-foundation-poc-design.md`
- `tests/plans/test_p001_plan.py`

Do not add production/runtime code.

### Test gates

Run:

- focused F-008 tests;
- existing `tests/plans/test_p001_plan.py`;
- full repository suite on supported Python versions used by repository CI.

No skip/xfail is permitted.

## Implementation shape

Preferred shape:

- `tests/plans/p001_design_scope.py` — pure helper returning violating paths for a supplied iterable;
- `tests/f008/test_p001_design_scope.py` — focused RED/GREEN regression contract;
- update `tests/plans/test_p001_plan.py` to use the helper and historical changed-path fixture;
- `.github/workflows/f008-p001-design-scope.yml` — focused gate including the F-008 tests and P-001 plan tests.

The helper must:

- normalize path separators to `/` so Windows-style fixture paths behave deterministically;
- reject the production directory itself (`src`, `schemas`, `profiles`) and descendants;
- avoid false positives such as `docs/src-notes.md` or `schemas-notes.md`;
- return deterministic sorted unique violations.

## Non-goals

F-008 does not:

- change P-001 architecture;
- rewrite historical P-001 plan content;
- alter production source/schema/profile files;
- inspect Git history/network at test runtime;
- define a generic repository policy beyond the historical P-001 design-only scope.

## Review gate

Fresh logically-independent adversarial review must challenge whether the replacement still tests a meaningful historical invariant rather than merely deleting the failure. Review should also probe path-boundary normalization, directory-vs-prefix false positives, and whether any current repository-state dependency remains.
