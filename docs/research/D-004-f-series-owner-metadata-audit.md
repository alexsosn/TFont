# D-004 research — F-series research ownership metadata audit

**Issue:** #104  
**Recorded:** 2026-09-09  
**Baseline:** `main` `6934649ae64c1df60032240d1a82a350c509e77a`  
**Type:** repository metadata / documentation prerequisite for F-021 (#99)

## Question

Can the committed `docs/research/F-NNN-*.md` tree support a simple current-tree ownership invariant in which each primary F-series research report carries exactly one machine-readable `**Issue:** #N` owner, without a permanent legacy allowlist or Git/GitHub lookup in normal CI?

This phase is audit only. It does not edit historical research conclusions, add the F-021 checker, or change runtime/source/schema/digest behavior.

## Audit method

The audit enumerated every committed `docs/research/F-NNN-*.md` file on the baseline tree and inspected the document header directly rather than relying on code-search indexing.

For each primary report, the current `**Issue:** #N` header was recorded when present. For the four headerless primary reports identified below, the intended owner was independently checked against the corresponding GitHub issue record and issue title.

A same-prefix supporting note is not treated as a second primary ticket merely because its filename starts with the same `F-NNN`: `F-019-cpython-path-conversion-evidence.md` explicitly identifies itself as an evidence note that closes a question in the main F-019 report. Its primary owner remains the main `F-019-invalid-source-filesystem-paths.md` report / issue #94.

## Current primary-report inventory

| Feature | Primary research report | Current owner metadata | Audit result |
|---|---|---:|---|
| F-001 | `F-001-source-diagnostic-provenance.md` | #18 | complete |
| F-002 | `F-002-wheel-schema-resources.md` | #21 | complete |
| F-003 | `F-003-digest-projection-key-errors.md` | #26 | complete |
| F-004 | `F-004-source-bundle-diagnostic-paths.md` | #28 | complete |
| F-005 | `F-005-utf16-diagnostic-paths.md` | #30 | complete |
| F-006 | `F-006-deep-source-nesting.md` | #32 | complete |
| F-007 | `F-007-ci-full-suite-deduplication.md` | #34 | complete |
| F-008 | `F-008-p001-design-scope.md` | #66 | complete |
| F-009 | `F-009-deep-digest-nesting.md` | #69 | complete |
| F-010 | `F-010-deep-directory-identity.md` | #71 | complete |
| F-011 | `F-011-node24-actions.md` | #78 | complete |
| F-012 | `F-012-file-hash-object-binding.md` | missing | migrate to #80 |
| F-013 | `F-013-directory-handle-binding.md` | #81 | complete |
| F-014 | `F-014-windows-exact-file-paths.md` | missing | migrate to #84 |
| F-015 | `F-015-direct-validation-source-boundary.md` | #87 | complete |
| F-016 | `F-016-custom-schema-recursion-boundary.md` | missing | migrate to #88 |
| F-017 | `F-017-inplace-file-mutation.md` | missing | migrate to #91 |
| F-018 | `F-018-handle-bound-file-reads.md` | #90 | complete |
| F-019 | `F-019-invalid-source-filesystem-paths.md` | #94 | complete |
| F-020 | `F-020-invalid-schema-root-filesystem-paths.md` | #95 | complete |
| F-021 | `F-021-feature-id-uniqueness.md` | #99 | complete |
| F-022 | `F-022-semantic-digest-json-boundary.md` | #103 | complete |

No fifth headerless primary F-series research report exists on the audited tree.

## Authoritative mapping checks for the four migrations

The four missing headers are historical metadata omissions, not unresolved ownership:

- **F-012 → #80**: issue #80 is titled `F-012: bind file hashing to the inspected filesystem object` and explicitly requires `docs/research/F-012-file-hash-object-binding.md` as its research deliverable.
- **F-014 → #84**: issue #84 is titled `F-014: reject ambiguous exact-file path spellings consistently on Windows`; the accepted report is `F-014-windows-exact-file-paths.md`.
- **F-016 → #88**: issue #88 is titled `F-016: contain recursion failures in custom schema validation` and names the accepted research as the implementation authority; its accepted report is `F-016-custom-schema-recursion-boundary.md`.
- **F-017 → #91**: issue #91 is titled `F-017: research in-place mutation during file identity hashing`; its accepted report is `F-017-inplace-file-mutation.md`.

These mappings also match the migration list already recorded in issue #104.

## Required migration

The minimal repository-state repair is exactly four metadata insertions, each near the top of its existing report:

```text
F-012-file-hash-object-binding.md          -> **Issue:** #80
F-014-windows-exact-file-paths.md          -> **Issue:** #84
F-016-custom-schema-recursion-boundary.md  -> **Issue:** #88
F-017-inplace-file-mutation.md             -> **Issue:** #91
```

No title, filename, research conclusion, historical SHA, issue number, or implementation claim should otherwise change.

## F-021 boundary after migration

Once the four headers are present, F-021 can enforce a pure current-tree rule for primary F-series research without a permanent legacy allowlist:

1. enumerate primary `docs/research/F-NNN-*.md` reports under the frozen classifier;
2. require exactly one machine-readable `**Issue:** #N` owner header per primary report;
3. require a single feature namespace to have one authoritative issue owner;
4. reject newly introduced headerless or conflicting primary research before merge.

F-021 should not infer ownership from Git history or call the GitHub API in normal CI.

The supporting F-019 evidence note demonstrates why the future checker needs a documented primary-vs-supporting classifier rather than the invalid rule “every filename beginning with `F-NNN-` is independently ticket-owning.” The main F-019 report remains the ownership-bearing artifact.

## Gate implications

D-004 should proceed only after fresh review of this audit:

1. design a metadata-only plan from this frozen four-file migration list;
2. commit RED repository-state tests before editing the four reports;
3. RED must fail on exactly the four missing primary ownership headers while existing owned reports remain controls;
4. GREEN should add only the four `**Issue:**` lines;
5. run focused metadata/research regressions and the authoritative full suite on the exact head;
6. perform a fresh logically-independent adversarial review checking accidental reassignment and scope drift.

## Non-goals

- no F-021 uniqueness-checker implementation in D-004;
- no automatic renumbering;
- no changes to supporting evidence-note semantics;
- no GitHub API/runtime dependency;
- no cleanup or renaming of historical research filenames;
- no claim that owner metadata becomes immutable without later CI enforcement.

## Conclusion

The current-tree blocker is finite and deterministic: **four** accepted primary F-series reports lack ownership metadata, and all four authoritative issue mappings are already established. After those four metadata-only backfills, F-021 can enforce ownership from the repository tree itself instead of carrying a permanent compatibility exception for legacy research.