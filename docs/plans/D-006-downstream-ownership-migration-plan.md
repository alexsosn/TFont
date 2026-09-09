# D-006 implementation plan — migrate F-series downstream ownership metadata

**Issue:** #114  
**Research:** `docs/research/D-006-downstream-ownership-migration.md`  
**Parent decision:** `docs/research/D-005-f-series-downstream-ownership.md`  
**Baseline:** `main` `bba3bd9dffbce797a2213cc26b78111ce539c345`

## 1. Goal

Complete machine-readable issue ownership for every currently present F-series downstream plan, focused workflow, and test package so F-023 can later enforce downstream claims against F-021 research authority without carrying legacy exceptions.

D-006 is a repository-metadata migration. It does not implement the reusable downstream ownership checker.

## 2. Frozen migration set

The reviewed D-006 research freezes exactly **35** missing carriers:

- 3 plan owner lines;
- 19 workflow owner comments;
- 13 test-package sidecars.

No other downstream artifact may be edited opportunistically. If current-main integration changes this set before final review, return to research/plan and rerun RED before altering GREEN.

### Plans

- `docs/plans/F-012-file-hash-object-binding-plan.md` -> #80
- `docs/plans/F-014-windows-exact-file-paths-plan.md` -> #84
- `docs/plans/F-015-error-precedence-amendment.md` -> #87

Insert exactly one canonical line immediately below the H1 title, followed by normal Markdown spacing:

```markdown
**Issue:** #N
```

No existing line of plan prose may change.

### Workflows

- `.github/workflows/f002-wheel-schema-resources.yml` -> #21
- `.github/workflows/f003-digest-projection-key-errors.yml` -> #26
- `.github/workflows/f004-source-bundle-diagnostic-paths.yml` -> #28
- `.github/workflows/f005-utf16-diagnostic-paths.yml` -> #30
- `.github/workflows/f006-deep-source-nesting.yml` -> #32
- `.github/workflows/f007-ci-full-suite-dedup.yml` -> #34
- `.github/workflows/f008-p001-design-scope.yml` -> #66
- `.github/workflows/f009-deep-digest-nesting.yml` -> #69
- `.github/workflows/f010-deep-directory-identity.yml` -> #71
- `.github/workflows/f011-node24-actions.yml` -> #78
- `.github/workflows/f012-file-hash-object-binding.yml` -> #80
- `.github/workflows/f014-windows-exact-file-paths.yml` -> #84
- `.github/workflows/f015-direct-validation-boundary.yml` -> #87
- `.github/workflows/f016-custom-schema-recursion.yml` -> #88
- `.github/workflows/f018-handle-bound-file-reads.yml` -> #90
- `.github/workflows/f019-invalid-source-filesystem-paths.yml` -> #94
- `.github/workflows/f020-invalid-schema-root-filesystem-paths.yml` -> #95
- `.github/workflows/f021-feature-id-ownership.yml` -> #99
- `.github/workflows/f022-semantic-digest-json-boundary.yml` -> #103

Insert exactly one comment as physical line 1:

```yaml
# Issue: #N
```

The existing file content begins on line 2 unchanged byte-for-byte apart from line-ending normalization already inherent in repository text writes. No YAML key/value, command, trigger, permission, matrix, concurrency expression, or action version may change.

### Test packages

Create exactly one `issue-owner.txt` in each package:

- `tests/f006/issue-owner.txt` -> #32
- `tests/f008/issue-owner.txt` -> #66
- `tests/f009/issue-owner.txt` -> #69
- `tests/f010/issue-owner.txt` -> #71
- `tests/f012/issue-owner.txt` -> #80
- `tests/f014/issue-owner.txt` -> #84
- `tests/f015/issue-owner.txt` -> #87
- `tests/f016/issue-owner.txt` -> #88
- `tests/f018/issue-owner.txt` -> #90
- `tests/f019/issue-owner.txt` -> #94
- `tests/f020/issue-owner.txt` -> #95
- `tests/f021/issue-owner.txt` -> #99
- `tests/f022/issue-owner.txt` -> #103

Exact content:

```text
Issue: #N
```

plus one final newline. No Python file is changed or added for ownership.

## 3. Migration-test implementation

Create:

- `tests/d006/__init__.py`
- `tests/d006/test_downstream_ownership_migration.py`
- `.github/workflows/d006-downstream-ownership-migration.yml`

The test code is D-006-specific migration scaffolding. It is not the F-023 reusable checker/API.

The tests derive research authority independently from repository text using the accepted F-021 bounded owner grammar rather than importing expected issue values from the future GREEN files.

### Authority parser

Enumerate every regular `docs/research/F-[0-9][0-9][0-9]-*.md` artifact.

For each:
- derive `F-NNN` from basename;
- inspect physical lines 2–12 inclusive, stopping before the first exact `## ` section heading;
- canonical owner regex: `^\*\*Issue:\*\* #([1-9][0-9]*)\s*$`;
- owner-like malformed lines are invalid;
- require exactly one canonical owner;
- require all artifacts sharing an F ID to agree.

The current authority must resolve 22 feature IDs with no errors.

### Plan parser

Enumerate every regular `docs/plans/F-[0-9][0-9][0-9]-*.md` artifact and use the same bounded Markdown grammar.

Every present plan/amendment after GREEN must carry exactly one owner equal to research authority.

### Workflow parser

Enumerate regular files matching both:

- `.github/workflows/f[0-9][0-9][0-9]-*.yml`
- `.github/workflows/f[0-9][0-9][0-9]-*.yaml`

Derive F ID from filename. Inspect physical lines 1–12 inclusive.

Canonical comment regex:

```regex
^# Issue: #([1-9][0-9]*)\s*$
```

Within the bounded region, any line whose left-stripped text begins `# Issue:` but does not match canonically is malformed. Require exactly one canonical comment after GREEN.

### Test-package parser

Enumerate direct `tests/f[0-9][0-9][0-9]` directories.

Ownership carrier is exactly `<package>/issue-owner.txt`. When present, its entire decoded UTF-8 content must match:

```regex
^Issue: #([1-9][0-9]*)\n?$
```

and contain only one logical owner declaration. GREEN writes exactly one final newline.

## 4. Deterministic migration diagnostics

The test module should expose internal helpers returning sorted path-based results for the test suite. It need not install or expose a CLI.

At minimum distinguish:

- missing carrier;
- malformed carrier;
- duplicate owner declarations where structurally possible;
- conflicting owner versus research authority;
- downstream unknown F ID.

All path lists/diagnostics are lexical-order deterministic.

## 5. Tests-only RED

Before any of the 35 target carriers changes, commit the D-006 tests and focused workflow.

RED classes should separate stable parser/authority controls from repository completeness.

### `DownstreamOwnershipParserControls`

Synthetic controls must be GREEN on RED and cover:

1. canonical plan owner accepted;
2. malformed/duplicate plan ownership rejected;
3. canonical workflow comment accepted;
4. indented/malformed/duplicate workflow ownership rejected;
5. `.yaml` workflow filename recognized as well as `.yml`;
6. valid sidecar accepted;
7. malformed/multiple-line sidecar rejected;
8. downstream owner disagreement with research authority classified as conflict;
9. downstream unknown F ID classified separately;
10. deterministic ordering independent of input/enumeration order.

### `RepositoryMigrationREDTests`

These inspect the checked-out tree and must demonstrate exactly the reviewed compatibility gap:

1. `test_research_authority_is_valid` -> GREEN, exactly 22 F IDs;
2. `test_existing_owned_plans_match_research` -> GREEN for the 19 current controls;
3. `test_missing_plan_owners` -> RED with exactly the 3 frozen plan paths;
4. `test_missing_workflow_owners` -> RED with exactly the 19 frozen workflow paths;
5. `test_missing_test_package_owners` -> RED with exactly the 13 frozen sidecar paths;
6. `test_no_explicit_downstream_conflicts` -> GREEN;
7. `test_no_unknown_downstream_feature_ids` -> GREEN;
8. `test_frozen_expected_owner_map` -> RED only because the 35 carriers are absent, while freezing their expected issue values from research authority;
9. `test_all_present_downstream_carriers_match_authority` -> RED until GREEN and then pass.

RED evidence is valid only if no target plan/workflow/test carrier is modified on the RED head and failures are attributable to the exact 35 missing carriers.

Do not weaken repository assertions after RED merely to make GREEN easier.

## 6. Focused workflow

Create `.github/workflows/d006-downstream-ownership-migration.yml`.

Matrix:
- Ubuntu 24.04;
- Python 3.10;
- Python 3.12.

Steps:
1. exact-head checkout;
2. setup Python;
3. run parser controls;
4. run repository migration RED/GREEN tests;
5. under `if: always()`, run F-021 ownership checker tests and direct `python scripts/check_f_series_ownership.py`;
6. under `if: always()`, run D-005/D-006 inventory script for audit visibility;
7. repository-wide discovery remains owned by `full-suite.yml`.

Triggers cover:
- `docs/research/F-*.md`;
- `docs/plans/F-*.md`;
- `.github/workflows/f*.yml`;
- `.github/workflows/f*.yaml`;
- `tests/f*/**`;
- D-006 research/plan/tests;
- D-005 inventory script;
- the D-006 migration workflow itself.

The workflow must not create a second full-repository test owner; F-007 policy remains authoritative.

## 7. Minimal GREEN

Only after valid RED evidence, create one metadata-only GREEN commit containing the exact 35 carrier changes.

For the 22 existing plan/workflow files:
- compare against the RED parent must show additions only at the intended owner insertion location;
- no existing line deletion or replacement is acceptable.

For the 13 sidecars:
- each is a new one-line text file;
- no Python test file changes.

The unchanged D-006 tests must become GREEN.

## 8. Post-GREEN migration audit

After GREEN, require the merged D-005 inventory semantics to report:

- research: 22 valid feature owners, zero authority errors;
- plans: 22 matching, zero missing/malformed/duplicate/conflicting/unknown;
- workflows: 19 matching, zero missing/malformed/duplicate/conflicting/unknown;
- test packages: 13 matching, zero missing/malformed/duplicate/conflicting/unknown.

The D-006 test suite must independently confirm the same property.

## 9. Scope guard

Allowed paths across the complete PR:

- D-006 research/plan;
- D-006 tests/workflows;
- the 3 frozen F-plan targets;
- the 19 frozen F-workflow targets;
- the 13 frozen test sidecars.

The already-merged D-005 inventory script is consumed but should not need semantic modification during D-006 unless review finds a research defect, in which case return to research.

Forbidden:
- `src/**`;
- schemas;
- `pyproject.toml` or package metadata;
- runtime/digest/semantic-validator/ontology code;
- existing Python tests except D-006's own new tests;
- reusable F-023 checker implementation.

## 10. Exact-head integration and regression gate

Before final review require:

- D-006 focused Python 3.10/3.12 green;
- F-021 ownership checker/regressions green;
- D-005 inventory shows the complete matching downstream state;
- authoritative full repository suite green on Python 3.10 and 3.12;
- F-007 single-full-suite policy green;
- F-011 action-major policy green where triggered;
- compare against then-current `main` contains only the allowed scope;
- no orphan/superseded migration PR remains open.

If `main` moves:
1. integrate current main;
2. rerun the inventory before final review;
3. if the frozen carrier set is no longer exact, return to research/plan/RED;
4. do not add a hidden allowlist or silently absorb new metadata targets.

## 11. Fresh independent adversarial review

Review exact final head and attack at least:

- wrong issue number on any of the 35 carriers;
- a workflow comment that accidentally edits executable YAML;
- plan prose/history drift alongside owner insertion;
- sidecar content/filename drift;
- accidental `__init__.py` creation for F-008;
- parser accepting indented/malformed workflow comments;
- parser ignoring `.yaml` workflows;
- malformed/duplicate carrier passing because one valid owner is present;
- unknown F ID accepted as if downstream files could allocate features;
- migration tests hard-coding exemptions instead of comparing claims to research authority;
- hidden F-023 checker implementation;
- full-suite duplication or CI-policy regression;
- current-main drift.

Any blocker returns to the earliest affected gate.

## 12. Exit condition

D-006 completes when all 35 reviewed compatibility gaps have been filled with local metadata matching F-021 research authority, all current downstream carriers are complete and consistent, focused/full exact-head CI is green, and fresh independent review finds no blocker. F-023/#115 is then unblocked for its own research phase.
