# D-006 plan amendment — inventory alignment and attributable RED

**Issue:** #114  
**Parent plan:** `docs/plans/D-006-downstream-ownership-migration-plan.md`  
**Research amendment:** `docs/research/D-006-inventory-carrier-alignment-amendment.md`

This amendment is authoritative where it refines the parent plan.

## 1. Pre-RED research-tooling correction is allowed

The parent plan's scope statement that `scripts/research/d005_downstream_ownership_inventory.py` should not need semantic modification is superseded.

Adversarial plan review demonstrated that the merged script could not recognize the accepted `issue-owner.txt` carrier and used an over-broad workflow-owner grammar. The corrected research head already aligned the inventory with D-005/D-006 semantics and reran the baseline successfully.

The correction is pre-RED research tooling, not migration GREEN. It remains in PR scope and must be reviewed as part of the final diff.

After GREEN the corrected inventory is required to report:

- research: 22 valid owners / zero authority errors;
- plans: 22 matching;
- workflows: 19 matching;
- test packages: 13 matching;
- no missing/malformed/duplicate/conflicting/unknown status in any downstream namespace.

## 2. RED attribution is simplified

The parent plan's intent remains: RED must prove the exact frozen legacy gap before any metadata carrier changes. To avoid a noisy wall of expected failures, split repository-state evidence into two complementary tests.

### Frozen-gap control — GREEN on RED

A repository-state control must independently derive research authority, enumerate downstream carriers, and assert that the complete current missing-carrier mapping equals the reviewed 35-path `path -> expected issue` mapping exactly.

This control proves:

- no 36th target is hidden;
- no frozen target has already been repaired;
- all expected owner numbers still match research authority;
- no explicit downstream conflict or unknown feature is being masked by the missing set.

It must pass on the tests-only RED head.

### Migration-completeness assertion — single intended RED failure

A separate repository-state test must require the missing-carrier mapping to be empty and all present explicit claims to match research authority.

On the tests-only RED head this is the single intended repository-completeness failure, with the deterministic 35-path mapping visible in the assertion output.

After GREEN the unchanged assertion passes.

Parser/grammar controls, research-authority validation, existing-owned-plan controls, no-conflict checks, no-unknown-feature checks, F-021 regressions, and inventory execution remain GREEN on RED.

This one-failure structure is preferable to thirty-five repetitive subtest failures because it proves the same frozen state while keeping RED causality unambiguous.

## 3. No change to GREEN boundary

GREEN is still exactly:

- 3 plan `**Issue:** #N` insertions;
- 19 workflow line-1 `# Issue: #N` comments;
- 13 new `issue-owner.txt` sidecars.

The pre-RED inventory-script correction is not part of those 35 GREEN carrier changes and must already be present on the RED parent.

No reusable F-023 checker or production/runtime/package change is introduced.
