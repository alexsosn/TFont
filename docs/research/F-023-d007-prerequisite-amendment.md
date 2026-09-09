# F-023 research amendment — D-007 prerequisite

**Issue:** #115  
**Parent research:** `docs/research/F-023-downstream-ownership-enforcement.md`  
**Baseline:** `main` `c18f86651174a500ba1c8ecf3fd7879bba180239`

## Trigger

The fresh post-D-006 F-023 research re-audit exposed a permanent-regression defect in `tests/d006/test_downstream_ownership_migration.py`:

```python
self.assertEqual(len(self.authority), 22)
```

That assertion freezes the historical number of research-owned F-series feature IDs at D-006 merge time. It is not one of D-006's actual migration invariants.

Adding the required F-023 research authority artifact is itself a valid new research-only feature under F-021, but raises the authority count from 22 to 23. Therefore F-023's own research PR can fail D-006/full-suite CI even though its ownership metadata is valid and it adds no downstream claim.

This defect is tracked as D-007/#117. A separate branch/PR is handling it through research -> independently reviewed plan -> behavioral RED -> minimal test-only GREEN.

## Effect on the parent F-023 conclusion

The architectural conclusions in the parent research remain unchanged:

- F-021 research metadata is the sole allocation authority;
- the existing `scripts/check_f_series_ownership.py` should be extended in place;
- D-005/D-006 inventory remains an independent regression oracle;
- downstream plans/workflows/test packages remain claims only;
- no registry, Git/GitHub authority lookup, or installed runtime API is justified.

However, the parent's phrase that F-023 is "unblocked" is now superseded by this amendment.

**F-023 planning and RED are blocked until D-007/#117 merges.**

The F-023 research PR may remain open as research-only evidence. Its D-006/full-suite failure, if observed before D-007 lands, is an expected prerequisite failure and must not be worked around by:

- omitting the canonical `**Issue:** #115` research owner;
- weakening F-021's feature ownership contract;
- adding F-023-specific allowlists to D-006;
- changing the F-023 feature ID;
- proceeding to plan/RED on a failing baseline.

After D-007 merges, re-integrate current `main`, rerun F-021/D-006/full-suite controls, and require a fresh independent review of the integrated exact F-023 research head before planning.

## D-007 boundary relevant to F-023

The stable D-006 guarantees that must survive D-007 are behavioral, not cardinal:

- research authority is syntactically valid and conflict-free;
- every present downstream carrier is valid/matching (or, only in D-006 phase replay, one of the original reviewed frozen carriers);
- the original frozen 35 carrier-to-owner mappings remain protected;
- merged repository state has no missing downstream ownership carrier.

A future research-only F-series feature with no downstream artifacts must remain valid, as F-021 and F-023 both require.

D-007 must not implement any F-023 downstream checker behavior. Once D-007 lands, F-023 resumes from the plan gate defined by the parent research.

## Amended exit condition for research

F-023 research is ready for plan only when:

1. D-007/#117 has merged;
2. this branch is integrated onto that current `main` without dropping the F-023 research authority metadata;
3. F-021 and D-006 controls accept the new F-023 research-only feature;
4. the exact integrated research head receives fresh logically-independent skeptical review.
