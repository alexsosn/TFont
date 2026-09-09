# I-006 plan amendment: preserve prerequisite trust provenance

**Issue:** #124  
**Amends:** `docs/plans/I-006-exact-semantic-resolver-plan.md`  
**Reason:** logically-independent adversarial plan review

Where this amendment is more specific than the parent plan, this amendment is authoritative.

## Finding

The parent plan makes `RuntimePrerequisiteState.source_contract` part of the prerequisite fingerprint, but the proposed `ExactNativePlan` exposes only the opaque `prerequisite_fingerprint`. That is insufficient for the later Context-Fabric execution trust boundary.

I-006 deliberately accepts separately established prerequisite attestations, including test/manual attestations before #130/I-007 exists. A later executor that receives only a resolver-produced plan must be able to distinguish which prerequisite contract established the runtime state. Merely verifying that a plan was produced by `semantic_resolve()` does not prove that the prerequisite was produced by the production I-007 evaluator.

## Normative correction

Add this field to `ExactNativePlan`:

```python
prerequisite_source_contract: str
```

It is copied exactly from the selected `RuntimePrerequisiteState.source_contract` after prerequisite validation.

The field is provenance, not resolver-side authenticity. I-006 does not decide which source contracts are trusted for production execution; #130/I-007 and the later execution handoff own that policy. I-006 must preserve enough provenance for them to enforce it without reopening or guessing the prerequisite source.

The exact-plan fingerprint projection must include `prerequisite_source_contract` explicitly in addition to `prerequisite_fingerprint`.

The whole-resolution fingerprint continues to bind the ordered plan fingerprints, so the prerequisite source contract is transitively bound there as well.

Do not infer this field from the fingerprint, evaluator-rule strings, corpus IDs, or variant metadata.

## RED additions

Before GREEN, permanent I-006 tests must prove:

1. an exact plan exposes the exact prerequisite `source_contract` value;
2. changing only `source_contract` changes prerequisite, plan, and whole-resolution fingerprints;
3. the resolver does not rewrite, normalize, or infer the source contract;
4. two otherwise identical prerequisite states from different source contracts produce distinct plan identities;
5. no test claims that an arbitrary source contract is production-trusted merely because I-006 accepted the attestation;
6. the later execution handoff can inspect plan provenance without receiving the original `RuntimePrerequisiteState` object.

## Scope

No new evaluator, signature/authentication scheme, filesystem inspection, Context-Fabric execution, or trust-store policy is introduced. This amendment only closes the provenance information loss at the I-006 -> execution-handoff boundary.