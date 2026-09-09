# D-006 research — freeze downstream ownership metadata migration

**Issue:** #114  
**Baseline:** `main` `bba3bd9dffbce797a2213cc26b78111ce539c345`  
**Parent research:** `docs/research/D-005-f-series-downstream-ownership.md`  
**Type:** repository metadata migration prerequisite for F-023 (#115)

## Question

After D-005 merged, is its measured 35-carrier downstream ownership gap still the exact current-main migration set, with no newly introduced missing, malformed, duplicate, conflicting, or unknown-feature carrier that would invalidate direct planning?

## Re-audit method

D-006 does not infer issue owners from numbering or downstream filenames. The existing D-005 inventory script first derives `F-NNN -> issue` authority from the F-021-enforced `docs/research/F-NNN-*.md` tree, then classifies downstream plan, workflow, and test-package ownership against that authority.

The re-audit is pinned by `.github/workflows/d006-downstream-ownership-migration-research.yml` and asserts the reviewed post-D-005 shape rather than merely printing an inventory.

Exact audit head: `95d1cce0b82c0c8723904a623a210b21302efd78`  
Workflow run: `34348287797`  
Python: 3.12  
Result: success.

Assertions that passed:

- 22 authoritative F-series research owners;
- no research-authority errors;
- 22 F-series plan/amendment artifacts: 19 matching, 3 missing;
- 19 F-series focused workflows: 19 missing local owners;
- 13 `tests/fNNN` packages: 13 missing package owners.

No explicit downstream owner is malformed, duplicated, conflicting, or attached to an unknown F ID on this baseline.

## Frozen migration set

D-006 GREEN may modify/add ownership metadata only for the 35 carriers below. Expected issues come from the research authority tree.

### Plan metadata — 3 insertions

| Plan artifact | Expected owner |
| --- | ---: |
| `docs/plans/F-012-file-hash-object-binding-plan.md` | #80 |
| `docs/plans/F-014-windows-exact-file-paths-plan.md` | #84 |
| `docs/plans/F-015-error-precedence-amendment.md` | #87 |

Each receives exactly one canonical bounded-header line:

```markdown
**Issue:** #N
```

No existing plan prose, title, historical SHA, decision, or filename may otherwise change.

### Workflow metadata — 19 insertions

| Workflow artifact | Feature | Expected owner |
| --- | --- | ---: |
| `.github/workflows/f002-wheel-schema-resources.yml` | F-002 | #21 |
| `.github/workflows/f003-digest-projection-key-errors.yml` | F-003 | #26 |
| `.github/workflows/f004-source-bundle-diagnostic-paths.yml` | F-004 | #28 |
| `.github/workflows/f005-utf16-diagnostic-paths.yml` | F-005 | #30 |
| `.github/workflows/f006-deep-source-nesting.yml` | F-006 | #32 |
| `.github/workflows/f007-ci-full-suite-dedup.yml` | F-007 | #34 |
| `.github/workflows/f008-p001-design-scope.yml` | F-008 | #66 |
| `.github/workflows/f009-deep-digest-nesting.yml` | F-009 | #69 |
| `.github/workflows/f010-deep-directory-identity.yml` | F-010 | #71 |
| `.github/workflows/f011-node24-actions.yml` | F-011 | #78 |
| `.github/workflows/f012-file-hash-object-binding.yml` | F-012 | #80 |
| `.github/workflows/f014-windows-exact-file-paths.yml` | F-014 | #84 |
| `.github/workflows/f015-direct-validation-boundary.yml` | F-015 | #87 |
| `.github/workflows/f016-custom-schema-recursion.yml` | F-016 | #88 |
| `.github/workflows/f018-handle-bound-file-reads.yml` | F-018 | #90 |
| `.github/workflows/f019-invalid-source-filesystem-paths.yml` | F-019 | #94 |
| `.github/workflows/f020-invalid-schema-root-filesystem-paths.yml` | F-020 | #95 |
| `.github/workflows/f021-feature-id-ownership.yml` | F-021 | #99 |
| `.github/workflows/f022-semantic-digest-json-boundary.yml` | F-022 | #103 |

Each receives exactly one top-of-file ownership comment in the bounded header region:

```yaml
# Issue: #N
```

The migration must not alter triggers, permissions, matrices, checkout refs, commands, concurrency, action versions, job environments, or any other executable YAML semantics.

### Test-package metadata — 13 sidecars

| Test package | Feature | Expected owner |
| --- | --- | ---: |
| `tests/f006` | F-006 | #32 |
| `tests/f008` | F-008 | #66 |
| `tests/f009` | F-009 | #69 |
| `tests/f010` | F-010 | #71 |
| `tests/f012` | F-012 | #80 |
| `tests/f014` | F-014 | #84 |
| `tests/f015` | F-015 | #87 |
| `tests/f016` | F-016 | #88 |
| `tests/f018` | F-018 | #90 |
| `tests/f019` | F-019 | #94 |
| `tests/f020` | F-020 | #95 |
| `tests/f021` | F-021 | #99 |
| `tests/f022` | F-022 | #103 |

Each package receives one new non-Python file named `issue-owner.txt` with exact normalized content:

```text
Issue: #N
```

followed by one final newline.

No `__init__.py` should be added to `tests/f008`; no Python test module should be edited merely to carry ownership.

## Metadata grammar to freeze for migration tests

D-006 migration tests are allowed to be ticket-specific rather than the future reusable F-023 checker, but they must use the accepted D-005 forms precisely enough that GREEN cannot hide malformed metadata.

### Plans

- same bounded Markdown header region as F-021: physical lines 2–12 inclusive, stopping earlier at the first exact `## ` section heading;
- canonical line: `^\*\*Issue:\*\* #([1-9][0-9]*)\s*$`;
- owner-like malformed `**Issue:**` lines remain visible as failures;
- exactly one canonical owner per present F-series plan/amendment.

### Workflows

- inspect only a bounded raw-text header region, physical lines 1–12 inclusive;
- canonical owner comment: `^# Issue: #([1-9][0-9]*)\s*$`;
- leading indentation, missing issue marker, zero/non-decimal IDs, or extra text are malformed owner-like comments rather than valid ownership;
- exactly one owner comment per present F-series focused workflow;
- both `.yml` and `.yaml` filenames belong to the namespace even though the current migration set contains only `.yml` files.

### Test sidecars

- exact file path `tests/fNNN/issue-owner.txt`;
- exact textual grammar `^Issue: #([1-9][0-9]*)\n?$` when read as text, with GREEN writing one final newline;
- no additional prose or multiple owner lines;
- the sidecar issue must equal research authority for the package F ID.

## RED strategy

Before editing any of the 35 target carriers, add D-006 migration tests plus a focused workflow.

The tests-only RED must independently establish:

1. research authority is valid and contains the expected 22 current feature IDs;
2. all 19 already-owned plans are matching controls;
3. exactly the three frozen plans lack owner metadata;
4. exactly the nineteen frozen workflows lack owner comments;
5. exactly the thirteen frozen test packages lack sidecars;
6. no explicit current downstream owner conflicts with research authority;
7. there are no unknown-feature downstream namespaces;
8. parser fixtures reject malformed/duplicate plan and workflow metadata and malformed sidecar content;
9. `.yaml` workflow enumeration is covered synthetically even though none exists in current main;
10. diagnostics/target lists are deterministic;
11. no target metadata file is edited on the RED head.

RED should fail only on repository-state completeness/exact-owner assertions caused by the frozen 35 missing carriers. Parser/control tests and F-021 research-ownership regressions must remain green.

If RED discovers any target beyond this frozen set, stop and return to research rather than expanding GREEN opportunistically.

## GREEN boundary

After valid RED evidence, GREEN may only:

- insert `**Issue:**` lines in the three frozen plan files;
- insert `# Issue: #N` comments in the nineteen frozen workflow files;
- create the thirteen frozen `issue-owner.txt` sidecars.

No reusable downstream ownership checker is part of D-006. No `src/**`, schemas, package metadata, runtime, digest, semantic-validator, or ontology code is in scope.

## Current-main integration rule

The 35-carrier set is frozen only for the audited baseline. Before final review:

- if `main` moves, integrate current main;
- rerun the complete downstream inventory;
- if a new downstream artifact introduces a missing/conflicting owner, return to research/plan rather than silently adding it to migration GREEN;
- if current main independently fixes one frozen gap, reconcile the migration target set and rerun RED/plan review rather than applying duplicate metadata.

## Decision

D-005's 35-carrier compatibility gap survives unchanged on post-D-005 `main`, so D-006 may proceed to a metadata-only implementation plan after fresh independent review of this research head.

The migration remains a prerequisite for F-023 (#115). F-023 stays blocked until D-006 merges a complete downstream ownership baseline.

## Non-goals

- no reusable downstream checker in D-006;
- no central ownership registry;
- no Git/GitHub lookup in normal CI;
- no automatic renumbering;
- no immutable-history guarantee;
- no requirement to create downstream artifacts for research-only features;
- no runtime/schema/digest/ontology behavior changes.
