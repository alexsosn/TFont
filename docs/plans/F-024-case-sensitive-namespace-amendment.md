# F-024 plan amendment — pin case-sensitive namespace controls

**Issue:** #121  
**Parent plan:** `docs/plans/F-024-ownership-namespace-scan-failures-plan.md`  
**Research amendment:** `docs/research/F-024-case-sensitive-namespace-amendment.md`

## Reason

Adversarial review of the first F-024 plan found that replacing `Path.glob()` with explicit enumeration changes a platform-specific implementation detail: Windows globbing can be case-insensitive even though the accepted F-series ownership namespace is case-sensitive.

Research now explicitly makes the F-021/F-023 lexical regex namespace authoritative across platforms.

## Plan change

All references in the parent plan to applying namespace regexes before entry classification are authoritative **case-sensitive lexical filtering**.

GREEN must not use filesystem/glob case matching to decide F-series namespace membership.

## Additional tests-only RED/GREEN controls

Add permanent controls to `tests/f024/test_ownership_namespace_scan_failures.py`.

### Research near-miss

With one valid authority artifact present, add a differently-cased unrelated research path such as:

`docs/research/f-999-near-miss.md`

Patch matching-entry `is_file()` classification so the test would fail if the checker tried to classify that near-miss as an F-series research entry.

Expected result: checker ignores the near-miss and the valid authority remains usable.

### Plan near-miss

Add `docs/plans/f-999-plan.md` beside a valid authority artifact. Patch file classification selectively so an attempt to classify the near-miss raises.

Expected result: no scan diagnostic and no ownership diagnostic for that path.

### Workflow near-miss

Add at least one of:

- `.github/workflows/F999-near-miss.yml`;
- `.github/workflows/f999-near-miss.YML`.

Selective classification injection must prove these are filtered lexically before `is_file()`.

### Test-package near-miss

Add `tests/F999` or `tests/f99` and inject classification failure if ownership code attempts `is_dir()` on it.

Expected result: ignored as unrelated.

## RED attribution

These near-miss controls may already pass on current POSIX RED because the current glob/regex combination is case-sensitive there. That is acceptable: they are compatibility controls, not intended RED failures.

The intended RED remains the scan-failure containment tests from the parent plan.

## GREEN scope

Unchanged: only `scripts/check_f_series_ownership.py` may change for implementation.

## Final review addition

The final reviewer must verify that:

- explicit enumeration does not accidentally broaden ownership namespace membership;
- near-miss case variants are filtered before classification;
- no Windows-specific glob semantics remain in authority/plan enumeration;
- exact accepted F-series naming continues to work unchanged.
