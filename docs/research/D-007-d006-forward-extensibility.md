# D-007 research — make D-006 ownership regressions forward-extensible

**Issue:** #117  
**Baseline:** `main` `c18f86651174a500ba1c8ecf3fd7879bba180239`  
**Blocked feature:** F-023 / #115

## Question

Which D-006 repository assertions are stable migration invariants, and which are historical observations that must not constrain future valid F-series research additions?

## Evidence inspected

- `tests/d006/test_downstream_ownership_migration.py` on post-D-006 `main`;
- `scripts/check_f_series_ownership.py` and `tests/f021/test_feature_id_ownership.py`;
- merged D-006 research/plan and the frozen 35-carrier migration map;
- F-023/#115 requirements, which require a fresh `F-023` research authority artifact before implementation.

## Finding 1 — the exact authority count is historical, not semantic

`RepositoryMigrationREDTests.test_research_authority_is_valid` currently requires:

```python
self.assertEqual(self.authority_errors, [])
self.assertEqual(len(self.authority), 22)
```

The first assertion is a permanent ownership invariant. The second records the repository size at the D-006 baseline.

F-021 intentionally permits a new `F-NNN` research feature when its research artifacts have one canonical owner and same-ID artifacts agree. A research-only feature is valid even when it has no downstream plan/workflow/test package yet.

Therefore a 23rd valid feature should not invalidate D-006.

## Finding 2 — the original migration remains protected without the total count

D-006 already has independent permanent controls that protect the migration:

1. `authority_errors == []` rejects malformed, duplicate, or conflicting research ownership.
2. `downstream_errors == []` rejects malformed, duplicate, conflicting, and unknown-feature downstream claims.
3. `test_plan_namespace_is_fully_accounted_for` proves every present F-series plan is either matching or explicitly missing.
4. `test_frozen_carriers_are_missing_or_matching` preserves the reviewed 35-path map and expected owners.
5. `test_migration_is_complete` requires no missing downstream carrier in the merged state.

A future research-only feature changes none of those properties. Removing the exact total-feature count does not weaken protection of any of the 35 migrated carriers.

## Finding 3 — new matching downstream artifacts are already supported

`scan_downstream()` enumerates current plan/workflow/test namespaces dynamically. New artifacts are accepted only if their local owner matches research authority. New missing carriers are rejected because `test_frozen_carriers_are_missing_or_matching` allows missing paths only from the D-006 frozen map.

So the forward-compatibility defect is narrowly limited to the exact research-authority cardinality assertion.

## Finding 4 — F-023 exposes the defect immediately

F-023/#115 must begin with fresh research after D-006. Its canonical research artifact will allocate `F-023 -> #115` under F-021 rules.

On current `main`, that otherwise-valid artifact would increase `len(authority)` from 22 to 23 and fail D-006 solely because of the historical count. This blocks the documented agentic research workflow before F-023 can reach planning or TDD.

## Alternatives

### A. Remove only the exact count assertion — recommended

Keep `authority_errors == []` and every downstream/frozen-carrier invariant unchanged.

Pros:
- smallest semantic correction;
- no future feature-count ceiling or floor;
- D-006 continues to protect exactly what it migrated;
- no production/checker behavior changes.

### B. Replace `== 22` with `>= 22` — reject

This would unblock F-023 but retains a meaningless historical lower bound. If legitimate repository evolution later reduces obsolete research features, D-006 would fail for another non-semantic reason.

### C. Freeze the 22 baseline feature IDs instead of the count — reject

D-006 did not own global research feature retention. F-021 owns research allocation integrity; D-006 owns the downstream migration.

### D. Avoid an `F-023` research artifact — reject

That would evade F-021 allocation semantics and undermine the issue-driven F-series workflow rather than fixing the regression.

## Behavioral TDD requirement

A new regression must exercise the actual D-006 repository test class against a temporary repository tree derived from the current valid tree plus one additional valid research-only F-series artifact.

Expected RED on current main:
- D-006 parser controls remain green;
- the temporary-tree D-006 suite has exactly one failure attributable to `len(authority) == 22`;
- no missing/conflicting/malformed downstream diagnostic appears.

Expected GREEN:
- the same temporary-tree D-006 suite passes with 23 valid research features;
- current real repository D-006 suite remains green;
- F-021 and full-suite regressions remain green.

The regression should monkeypatch the D-006 module's `ROOT` only within the test and restore it afterward. The temporary tree needs only the namespaces consumed by D-006: research docs, F-series plans, focused F-series workflows, and test-package owner sidecars.

## Licensing / redistribution

No external data, dependency, or license change is involved.

## Agent and human effects

After the correction, agents and contributors can allocate future F-series research features without editing D-006 merely to update a repository-size constant. D-006 continues to fail on actual ownership regressions rather than normal feature growth.

## Recommendation

Treat `len(authority) == 22` as historical RED/GREEN evidence that should remain visible in D-006 research/CI history, not as a permanent merged-tree invariant.

Implement a behavioral tests-only RED proving one extra valid research-only feature currently breaks the real D-006 suite, then GREEN by removing only the exact cardinality assertion. Do not modify F-021, downstream carrier grammar, the frozen 35 map, runtime code, schemas, package metadata, or F-023 itself in this ticket.

## Acceptance traceability

- identify unstable D-006 assumption: exact authority cardinality;
- prove original 35 migration remains protected: existing frozen/missing/conflict controls;
- specify behavioral RED: real D-006 suite under temporary tree with one extra research feature;
- minimal GREEN: remove only historical count assertion;
- preserve F-021/F-023 semantics: research authority remains dynamic and sole allocator.
