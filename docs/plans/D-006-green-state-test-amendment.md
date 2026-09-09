# D-006 plan amendment — make migration controls phase-invariant

## Trigger

Exact-head GREEN CI at `a8b65fbd9be46a509258881b17614ffc745d4b28` exposed a test-design defect in the D-006 repository controls.

The metadata migration itself completed correctly: the independent downstream inventory reports 22/22 plans matching, 19/19 focused workflows matching, 13/13 F-series test packages matching, and no research-authority errors. F-021 and every triggered F-series feature workflow are green.

Two D-006 assertions nevertheless fail after successful migration because they encode the RED snapshot as a permanent invariant:

- `test_existing_owned_plans_are_matching_controls` requires exactly 19 matching plans, although GREEN correctly raises this to 22;
- `test_frozen_missing_carrier_map_matches_research` requires all 35 frozen targets to remain missing, although GREEN correctly makes the missing set empty.

The same two failures also make the authoritative full-suite workflow red. No production/runtime/schema/package behavior is implicated.

## Corrected invariant

The frozen 35-target map remains authoritative, but a target may be in either of two valid states while the migration test suite is used across RED and GREEN:

1. **RED state:** the target is absent from local ownership metadata and appears in `missing` with the frozen research owner;
2. **GREEN state:** the target is present and matching the same research owner.

No target may be malformed, conflicting, unknown, or disappear from both states. No missing carrier outside the frozen map is allowed.

For plans specifically, the stable invariant is that every current F-series plan is either already matching or is one of the frozen missing plan targets. Therefore `matching plan count + frozen-missing plan count == total current plan artifacts` rather than a permanently fixed matching count of 19.

`test_migration_is_complete` remains the sole phase-changing assertion: it is intentionally RED while any frozen target is missing and becomes GREEN only when `missing == {}`.

## Test-only correction

Amend `tests/d006/test_downstream_ownership_migration.py` only:

- replace the fixed 19-plan assertion with the phase-invariant coverage assertion above;
- replace the fixed `missing == FROZEN_MISSING` assertion with a target-state invariant that:
  - requires every current missing entry to be a frozen target with the frozen owner;
  - requires each frozen target not currently missing to appear in the scanner's matching set;
  - rejects unexpected missing carriers;
- retain `test_migration_is_complete` unchanged;
- retain all parser controls, research-authority controls, diagnostic grammar, and `maxDiff = None` unchanged.

No migration carrier, inventory parser, workflow, production source, schema, packaging metadata, or public API is changed by this correction.

## Gate consequence

The pre-correction RED evidence remains valid because exact head `d4679965c246982500a8f5710e259fd4624009be` independently proved the full frozen 35-carrier missing map and one intended completeness failure on Python 3.10 and 3.12 before any carrier edit.

After this amendment and test-only correction, exact-head GREEN must show:

- all D-006 parser controls green on Python 3.10 and 3.12;
- all D-006 repository controls green;
- corrected inventory: 22 matching plans, 19 matching workflows, 13 matching test packages, zero missing/conflicting/malformed/unknown owners;
- F-021 ownership regressions green;
- authoritative full suite green on Python 3.10 and 3.12;
- no change to the already-reviewed atomic 35-file GREEN commit itself.

A fresh independent adversarial review is required on the new exact final head before merge.
