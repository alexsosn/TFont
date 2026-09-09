# D-006 research amendment — align inventory with accepted downstream carriers

**Issue:** #114  
**Parent research:** `docs/research/D-006-downstream-ownership-migration.md`  
**Triggered by:** adversarial plan review

## Finding

The first D-006 implementation-plan review found that the merged D-005 reproducibility script did not yet recognize the final test-package carrier selected by D-005 research.

`detect_test_owner()` still probed earlier exploratory candidates (`OWNER`, `OWNERSHIP`, `ownership.txt`, and sometimes `__init__.py`) and did **not** inspect `tests/fNNN/issue-owner.txt`. Its workflow-owner parser was also broader than the accepted contract: it scanned twenty lines and accepted indentation/case variants rather than the exact bounded `# Issue: #N` form.

This did not invalidate the D-005 baseline counts because no current workflow or test package had any explicit ownership carrier. It would, however, make the planned post-GREEN audit incorrect: valid new `issue-owner.txt` sidecars would still be reported as missing, and non-canonical workflow comments could be reported as valid.

## Research-tool correction

Before D-006 RED, `scripts/research/d005_downstream_ownership_inventory.py` was aligned with the accepted D-005/D-006 carrier definitions:

- workflow owner: exact `# Issue: #<positive decimal>` within physical lines 1–12;
- malformed owner-like `# Issue:` comments are classified as malformed;
- test-package owner source: exactly `tests/fNNN/issue-owner.txt`;
- sidecar grammar: exactly `Issue: #<positive decimal>` with an optional final newline when read;
- invalid sidecar content is classified as malformed;
- `__init__.py` and exploratory OWNER/OWNERSHIP filenames are no longer treated as ownership sources.

Exact correction head: `8becb594ac54ea574ab35b2ede64368bde4b4a16`  
D-006 research workflow run: `34348719519`  
Result: success.

The corrected parser still reports the same reviewed current-tree state:

- 22 valid research owners;
- plans: 19 matching / 3 missing;
- workflows: 19 missing;
- test packages: 13 missing.

Therefore the frozen 35-carrier migration set and all expected issue owners remain unchanged.

## Consequence for the implementation plan

The D-006 plan must treat this research-script correction as allowed pre-RED research tooling and must require the corrected inventory to become fully matching after GREEN. The plan must not claim that the merged D-005 script is unchanged across D-006.

No downstream metadata carrier was edited by this correction. It is still valid to enter tests-only RED after this amended research state receives fresh independent review and the plan is updated/re-reviewed.
