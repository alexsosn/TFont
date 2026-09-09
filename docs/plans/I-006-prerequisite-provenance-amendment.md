# I-006 plan amendment: preserve prerequisite trust provenance and reject duplicate lookup state

**Issue:** #124  
**Amends:** `docs/plans/I-006-exact-semantic-resolver-plan.md`  
**Reason:** logically-independent adversarial plan review

Where this amendment is more specific than the parent plan, this amendment is authoritative.

## 1. Finding: prerequisite trust provenance would be lost at the plan boundary

The parent plan makes `RuntimePrerequisiteState.source_contract` part of the prerequisite fingerprint, but the proposed `ExactNativePlan` exposes only the opaque `prerequisite_fingerprint`. That is insufficient for the later Context-Fabric execution trust boundary.

I-006 deliberately accepts separately established prerequisite attestations, including test/manual attestations before #130/I-007 exists. A later executor that receives only a resolver-produced plan must be able to distinguish which prerequisite contract established the runtime state. Merely verifying that a plan was produced by `semantic_resolve()` does not prove that the prerequisite was produced by the production I-007 evaluator.

### Normative correction

Add this field to `ExactNativePlan`:

```python
prerequisite_source_contract: str
```

It is copied exactly from the selected `RuntimePrerequisiteState.source_contract` after prerequisite validation.

The field is provenance, not resolver-side authenticity. I-006 does not decide which source contracts are trusted for production execution; #130/I-007 and the later execution handoff own that policy. I-006 must preserve enough provenance for them to enforce it without reopening or guessing the prerequisite source.

The exact-plan fingerprint projection must include `prerequisite_source_contract` explicitly in addition to `prerequisite_fingerprint`.

The whole-resolution fingerprint continues to bind the ordered plan fingerprints, so the prerequisite source contract is transitively bound there as well.

Do not infer this field from the fingerprint, evaluator-rule strings, corpus IDs, or variant metadata.

`RuntimePrerequisiteState.source_contract` must be a non-empty exact string. An empty value fails `invalid_prerequisite` before hashing or selection.

### RED additions

Before GREEN, permanent I-006 tests must prove:

1. an exact plan exposes the exact prerequisite `source_contract` value;
2. changing only `source_contract` changes prerequisite, plan, and whole-resolution fingerprints;
3. the resolver does not rewrite, normalize, or infer the source contract;
4. two otherwise identical prerequisite states from different source contracts produce distinct plan identities;
5. empty `source_contract` fails `invalid_prerequisite`;
6. no test claims that an arbitrary source contract is production-trusted merely because I-006 accepted the attestation;
7. the later execution handoff can inspect plan provenance without receiving the original `RuntimePrerequisiteState` object.

## 2. Finding: duplicate prerequisite records for one exact variant are under-specified

The parent plan rejects multiple *different* fresh variants for one requested corpus, but it does not freeze behavior when the prerequisite iterable contains two records for the same exact `BundleVariantKey`.

Silently deduplicating or selecting one by input order would make caller input order semantically significant and could hide conflicting runtime observations.

### Normative correction

For every requested corpus, prerequisite indexing must reject more than one `RuntimePrerequisiteState` for the same exact `BundleVariantKey`, whether the records are byte/equality-identical or conflicting.

Use:

```text
invalid_prerequisite
```

for duplicate exact-variant prerequisite rows. `ambiguous_prerequisite_variant` remains reserved for two or more distinct fresh variants that could each represent the requested corpus.

No first-row, last-row, newest-row, equality-deduplication, or source-contract preference rule is allowed.

### RED additions

8. duplicate identical prerequisite rows for one exact variant fail `invalid_prerequisite`;
9. duplicate conflicting prerequisite rows for one exact variant fail `invalid_prerequisite` independent of authored input order;
10. two distinct fresh variants continue to fail `ambiguous_prerequisite_variant`.

## 3. Finding: public compiled IR can be hand-constructed with duplicate authoritative keys

`CompiledSemanticIR` and its child records are immutable public dataclasses, but immutability does not prove that an instance came from `compile_semantic_ir()`. A caller can hand-construct an object with duplicate entries in tuple-backed index families.

A resolver implementation that converts these tuples directly with `dict(...)` could silently apply last-one-wins semantics. This is particularly dangerous for:

- duplicate `BundleVariantIR.key` values in `ir.variants`;
- duplicate `SemanticKey` rows in `ir.semantic_index`;
- duplicate `CapabilityKey` rows in `ir.capability_facts`.

I-006 already promises defensive `invalid_compiled_ir` checks, so the uniqueness boundary must be explicit before RED.

### Normative correction

Before any prerequisite selection, capability lookup, or semantic target lookup, build the resolver's internal lookup views with duplicate detection.

Reject `invalid_compiled_ir` when:

1. two `BundleVariantIR` rows have the same exact `BundleVariantKey`;
2. two `semantic_index` entries have the same exact `SemanticKey`;
3. two `capability_facts` entries have the same exact `CapabilityKey`.

Do not silently merge their value tuples and do not let input order choose a winner.

This is a defensive coherence gate only. The resolver still does not re-run I-005 compilation or I-004 semantic validation.

### RED additions

11. duplicate variant keys in a hand-built `CompiledSemanticIR` fail `invalid_compiled_ir`;
12. duplicate semantic-index keys fail `invalid_compiled_ir`, including when the duplicate rows contain different bindings;
13. duplicate capability-fact keys fail `invalid_compiled_ir`;
14. reversing the order of malformed duplicate-key entries yields the same category rather than changing the selected data;
15. valid IR emitted by `compile_semantic_ir()` remains accepted unchanged.

## Scope

No new evaluator, signature/authentication scheme, filesystem inspection, Context-Fabric execution, trust-store policy, semantic source validation, or multi-binding composition is introduced. These corrections preserve execution provenance and remove caller-order ambiguity at the I-006 boundary.