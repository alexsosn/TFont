# I-006 plan adversarial-review amendment

**Issue:** #124  
**Amends:** `docs/plans/I-006-exact-semantic-resolver-plan.md`  
**Reviewed head before amendment:** `94259f44ea71f2803e060565eca3f5537c7da4ec`

This amendment is normative where it is more specific than the original plan.

## 1. Freeze NativeBindingIR -> source-binding identity projection

The resolver defensively verifies that a compiled `TargetBindingIR.native_execution_binding` still matches its stored `native_execution_binding_identity` before emitting a plan.

The public I-005 `native_binding_identity()` hashes the **source JSON binding dictionary**. `NativeBindingIR` is not itself that source projection: in particular, `value_present` records the difference between an absent `value` field and an authored JSON `null` value.

I-006 therefore freezes one internal inverse projection:

```python
def _native_binding_source_projection(binding: NativeBindingIR) -> dict[str, Any]:
    ...
```

Rules, in source field order only for readability (JCS canonicalization owns object-key ordering):

1. Start with an empty exact `dict`.
2. For each scalar optional source field below, include the key **iff the corresponding IR field is not `None`**:
   - `component_id`
   - `node_type`
   - `feature`
   - `edge`
   - `direction`
   - `interpretation`
   - `execution_shape`
3. `value` is special:
   - if `binding.value_present is False`, omit the `value` key entirely;
   - if `binding.value_present is True`, include `"value": binding.value`, including when that value is JSON `null`/Python `None`.
4. If `closed_values is not None`, include `"closed_values"` as a JSON list preserving the exact validated tuple order. Empty tuple therefore projects to an authored empty list, not absence.
5. If `steps is not None`, include `"steps"` as a JSON list preserving step order, with each step exactly:

   ```json
   {"edge": "...", "direction": "..."}
   ```

   Empty tuple projects to an authored empty list, not absence.
6. Do not emit `value_present`; it is IR presence metadata, not a source binding field.
7. Do not invent default/null keys that were absent in source.
8. Pass the resulting dict to the existing public `native_binding_identity()`; do not introduce another native-binding hash algorithm.

The resolver treats any inability to reconstruct a valid identity projection, or any recomputed/stored identity mismatch, as `invalid_compiled_ir`.

### Mandatory RED additions

Add before GREEN:

- a source binding with authored `"value": null` compiles and resolves without false identity mismatch;
- an otherwise valid binding with absent `value` compiles and resolves without false identity mismatch;
- the reconstructed source projections for those two cases differ exactly by key presence;
- changing the typed `NativeBindingIR` while retaining the old stored identity fails `invalid_compiled_ir`;
- steps and `closed_values` preserve authored list order/presence through identity verification.

No `dataclasses.asdict()` or generic removal-of-`None` implementation satisfies this contract.

## 2. Freeze ontology-bundle prerequisite diagnostics

Replace the ambiguous RED #31 and make §8 exact.

### Variant has no ontology bundle

When `selected_variant.ontology_bundle_digest is None`, the only valid attestation shape is:

```text
ontology_bundle_state == "not-required"
active_ontology_bundle_digest is None
```

Any other combination, including `verified + non-null digest`, `unavailable`, or `not-required + non-null digest`, is internally contradictory caller evidence and fails:

```text
invalid_prerequisite
```

It is **not** `stale_prerequisite`, because there is no compiled bundle identity against which a supplied digest could merely be stale.

### Variant requires an ontology bundle

When `selected_variant.ontology_bundle_digest is not None`:

- `ontology_bundle_state == "unavailable"` -> `ontology_bundle_unavailable`;
- any state other than `verified|unavailable` (including `not-required` or unknown) -> `invalid_prerequisite`;
- `verified` with `active_ontology_bundle_digest is None` -> `invalid_prerequisite`;
- `verified` with a non-null digest unequal to the variant digest -> `stale_prerequisite`;
- `verified` with exact digest equality -> continue.

Projection-level `ontology_bundle_requirement` coherence remains an `invalid_compiled_ir` check after prerequisite validation.

### Revised RED #31

`null-bundle variant with any fabricated bundle state/digest other than exactly not-required/None -> invalid_prerequisite`.

Add a separate RED for `non-null variant + state=not-required -> invalid_prerequisite`.

## 3. Freeze duplicate prerequisite-record behavior

Prerequisite materialization is deterministic and never first-row-wins.

After type/shape validation, index prerequisite records by exact `BundleVariantKey`.

### Same variant repeated

If more than one `RuntimePrerequisiteState` is supplied for the same exact `BundleVariantKey`, fail:

```text
invalid_prerequisite
```

This applies even when the records are dataclass-equal. The API contract is one attestation per variant; silent deduplication would make accidental duplication and conflicting evidence indistinguishable.

If repeated records differ in parent/dependency/bundle/source-contract fields, the same category applies; do not inspect iterable order to choose a winner.

### Different variants for the requested corpus

After rejecting duplicate exact variant keys and validating profile-release freshness:

- zero candidate variants -> `missing_prerequisite` or `stale_prerequisite` according to the original selection rules;
- exactly one fresh candidate variant -> select it;
- more than one fresh distinct variant for the same requested corpus -> `ambiguous_prerequisite_variant`.

The resolver never uses parent state, profile version recency, expected digest similarity, source contract, or lexical ordering to disambiguate multiple fresh variants.

### Mandatory RED additions

- identical prerequisite object supplied twice -> `invalid_prerequisite`;
- same variant supplied twice with different dependency evidence -> `invalid_prerequisite` independent of order;
- two distinct fresh variants -> `ambiguous_prerequisite_variant`;
- reversing prerequisite iterable order does not change category/corpus attribution.

## 4. Runtime-attestation trust boundary

`RuntimePrerequisiteState.source_contract` is provenance for the external prerequisite-establishment mechanism; I-006 does not authenticate or execute that mechanism.

For I-006:

- require a non-empty exact string;
- include it in the prerequisite fingerprint;
- do not infer authority from its spelling;
- do not maintain an allow-list in I-006.

This means callers can construct test/POC attestations, as explicitly required by #124 research. Such attestations are sufficient to exercise resolver semantics but are **not a production trust root for Context-Fabric execution**.

The later execution-handoff ticket must remain blocked on #130 and must accept only prerequisite evidence produced/validated under the versioned production evaluator/report-vNext contract. A plan fingerprint proves what I-006 resolved from its inputs; it does not cryptographically authenticate who established runtime compatibility.

No MCP/session/user identity belongs in prerequisite or plan semantic identity.

## 5. Additional fingerprint RED

Because source-contract provenance participates in runtime prerequisite identity:

- changing only `source_contract` changes prerequisite, plan and whole-resolution fingerprints;
- it does not change profile-release fingerprint;
- arbitrary `source_contract` spelling never changes semantic tuple selection or bypasses parent/dependency/bundle consistency checks.

## 6. Review closure criteria

The plan may enter RED only after fresh review confirms all of the following on one exact head:

- null versus absent native `value` survives defensive identity verification;
- bundle prerequisite categories have no implementation-choice branch;
- duplicate attestation records are deterministic and fail closed;
- I-006 POC attestation is clearly separated from #130 production runtime trust;
- no new source interpretation, live corpus evaluation, query execution or multi-binding composition entered scope.
