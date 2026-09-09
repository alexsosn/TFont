# I-006 plan amendment: preserve prerequisite trust provenance and close resolver coherence gaps

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

For every requested corpus, prerequisite indexing must reject more than one `RuntimePrerequisiteState` for the same exact `BundleVariantKey`, whether the records are equality-identical or conflicting.

Use `invalid_prerequisite` for duplicate exact-variant prerequisite rows. `ambiguous_prerequisite_variant` remains reserved for two or more distinct fresh variants that could each represent the requested corpus.

No first-row, last-row, newest-row, equality-deduplication, or source-contract preference rule is allowed.

### RED additions

8. duplicate identical prerequisite rows for one exact variant fail `invalid_prerequisite`;
9. duplicate conflicting prerequisite rows for one exact variant fail `invalid_prerequisite` independent of authored input order;
10. two distinct fresh variants continue to fail `ambiguous_prerequisite_variant`.

## 3. Finding: public compiled IR can be hand-constructed with duplicate authoritative keys

`CompiledSemanticIR` and its child records are immutable public dataclasses, but immutability does not prove that an instance came from `compile_semantic_ir()`. A caller can hand-construct an object with duplicate entries in tuple-backed index families.

A resolver implementation that converts these tuples directly with `dict(...)` could silently apply last-one-wins semantics. This is particularly dangerous for duplicate `BundleVariantIR.key` values in `ir.variants`, duplicate `SemanticKey` rows in `ir.semantic_index`, and duplicate `CapabilityKey` rows in `ir.capability_facts`.

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

## 4. Finding: an injected target row could otherwise escape the selected release authority

The parent plan defensively checks a target row's local fields, review status, routing, bundle digest and native-binding identity. That is necessary but not sufficient for a public hand-constructed `CompiledSemanticIR`.

A malicious or malformed `TargetBindingIR` can claim the selected `BundleVariantKey` while carrying mapping/review/ontology authority that is absent from the selected `ProfileReleaseSignature`. A fresh runtime prerequisite for release A must never authorize a target row injected from release B merely because the row copies release A's variant key.

### Normative correction

Before an exact binding can become an `ExactNativePlan`, verify it is anchored in the selected `BundleVariantIR.release_signature` and that the variant record itself is internally coherent.

For the selected `BundleVariantIR` require:

- `release_key.corpus_id == key.corpus_id`;
- `release_key.authored_profile_id == key.authored_profile_id`;
- `release_key.profile_version == key.profile_version`;
- `release_signature.ontology_bundle_digest == key.ontology_bundle_digest`;
- the repeated `BundleVariantIR.mapping_digests` and `ontology_locks` equal the corresponding release-signature fields;
- the repeated schema/contract/algorithm version fields on `BundleVariantIR` equal their release-signature counterparts.

For the selected `TargetBindingIR` require:

- `(mapping_id, mapping_semantic_digest)` exists exactly in `release_signature.mapping_digests`;
- `(mapping_id, mapping_review)` equals the matching entry in `release_signature.mapping_reviews`;
- `(mapping_id, projection_id, projection_review)` equals the matching entry in `release_signature.projection_reviews`;
- `ontology_lock` equals one of the selected release signature's `ontology_locks`;
- every `native_dependencies` ID exists in the selected release signature's dependency-record ID set;
- the already frozen row/key/routing/corpus/variant/bundle/native-binding coherence checks also pass.

Any failure is `invalid_compiled_ir`. Do not repair, infer, or search a different release row.

The resolver need not reconstruct I-004 source evidence or recompute mapping/projection semantic digests. It verifies only the compiled cross-links it relies upon for execution authority.

### RED additions

16. a binding whose mapping digest is absent from the selected release signature fails `invalid_compiled_ir`;
17. a binding whose mapping review fingerprint differs from the release signature fails `invalid_compiled_ir`;
18. a binding whose projection review fingerprint differs from the release signature fails `invalid_compiled_ir`;
19. a binding whose ontology-lock fingerprint is absent/different in the release signature fails `invalid_compiled_ir`;
20. a binding naming a native dependency outside the selected release signature fails `invalid_compiled_ir`;
21. a variant whose release key disagrees with its variant key fails `invalid_compiled_ir`;
22. a variant whose ontology-bundle digest or repeated release fields disagree with its release signature fails `invalid_compiled_ir`;
23. valid compiler-produced noun rows satisfy all cross-link checks without source re-validation.

## Scope

No new evaluator, signature/authentication scheme, filesystem inspection, Context-Fabric execution, trust-store policy, semantic source validation, or multi-binding composition is introduced. These corrections preserve execution provenance, remove caller-order ambiguity, and ensure that runtime prerequisites authorize only bindings contained in the selected compiled release authority.