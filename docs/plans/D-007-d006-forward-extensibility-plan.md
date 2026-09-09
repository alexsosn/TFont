# D-007 implementation plan — D-006 forward extensibility

**Issue:** #117  
**Research:** `docs/research/D-007-d006-forward-extensibility.md`  
**Baseline:** `main` `c18f86651174a500ba1c8ecf3fd7879bba180239`

## Goal

Make the merged D-006 regression suite accept future valid research-only F-series feature allocations without weakening any ownership or migration guarantee.

This is a test-regression correction. It does not change the F-021 checker, downstream carrier grammar, F-023, runtime code, schemas, packaging, or public APIs.

## Stable invariant

`RepositoryMigrationREDTests.test_research_authority_is_valid` must require:

- no research-authority parsing/conflict errors;
- at least one valid research authority entry.

It must not require the historical D-006 cardinality of 22 features.

All other D-006 repository controls remain unchanged:

- explicit downstream claims have no errors;
- every present F-series plan is accounted for as matching or missing;
- only the frozen 35 D-006 carriers may ever appear as missing during historical phase replay;
- every frozen carrier remains observed as missing or matching with the reviewed owner;
- merged/current repository has zero missing carriers.

## Tests-only RED

Create only:

- `tests/d007/__init__.py`;
- `tests/d007/test_d006_forward_extensibility.py`.

Do not edit D-006 yet.

The test must import the real `tests.d006.test_downstream_ownership_migration` module and execute its actual `RepositoryMigrationREDTests` class against a temporary repository root.

### Temporary tree

Construct a minimal faithful copy of the current ownership namespaces:

- copy `docs/research/`;
- copy `docs/plans/`;
- copy `.github/workflows/`;
- create `tests/` and, for each current direct `tests/fNNN` package, copy only `issue-owner.txt` when present.

Then add exactly one new valid research-only artifact:

`docs/research/F-999-future-research-only.md`

with canonical content including exactly one header owner `**Issue:** #999` before the first `## ` section.

Do not create any F-999 plan, workflow, or test package. Research-only features are valid under F-021/F-023 semantics.

### Running the real D-006 class

Use `unittest.defaultTestLoader.loadTestsFromTestCase(d006.RepositoryMigrationREDTests)` and `unittest.TextTestRunner` against the temporary root while patching only `d006.ROOT`.

The patch must be context-managed so `ROOT` is restored even if the nested suite fails.

The permanent D-007 test asserts that the nested D-006 suite is successful. Include the nested runner output in the outer assertion message.

### Valid RED evidence

On the tests-only RED head, authoritative full-suite Python 3.10 and 3.12 must fail only because the new D-007 regression observes the nested D-006 failure:

- failing nested method: `test_research_authority_is_valid`;
- attribution contains `23 != 22`;
- the other four D-006 repository tests in the nested suite pass;
- no malformed/conflicting/missing downstream ownership failure occurs.

Do not encode the RED failure shape as a permanent test expectation. Inspect CI logs before GREEN.

## Minimal GREEN

Edit only `tests/d006/test_downstream_ownership_migration.py`.

Replace:

```python
self.assertEqual(len(self.authority), 22)
```

with:

```python
self.assertTrue(self.authority)
```

No helper/parser, frozen mapping, carrier grammar, scan behavior, or other assertion changes.

## Regression gates

After GREEN require:

1. `tests/d007` regression green;
2. D-006 focused workflow green on Python 3.10 and 3.12;
3. D-006 parser and repository controls green;
4. F-021 regressions run by D-006 green;
5. full repository suite green on Python 3.10 and 3.12;
6. current post-D-006 inventory remains complete;
7. compare against current `main` contains only D-007 research/plan/tests and the one D-006 assertion edit.

A separate D-007 workflow is unnecessary: the full suite owns RED coverage on both supported Python versions, while the GREEN edit to `tests/d006/**` triggers the permanent D-006 focused workflow.

## Adversarial review

Fresh final-head review must attack at least:

- whether the new regression accidentally constructs an incomplete temporary tree that passes for the wrong reason;
- whether `d006.ROOT` leaks after nested execution;
- whether GREEN changes anything beyond the cardinality assertion;
- whether replacing `==22` with truthiness permits malformed/conflicting authority (it must not; `authority_errors == []` remains);
- whether any frozen 35-carrier protection was removed or weakened;
- whether F-023/checker/runtime code leaked into scope;
- current-main drift.

## Exit condition

The real D-006 suite passes against current repository state and against the same state plus one additional valid research-only F-series feature, while every original D-006 migration invariant remains unchanged.
