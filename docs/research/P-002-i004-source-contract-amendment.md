# P-002 research: source-contract amendment required by I-004

**Issue:** #37  
**Recorded:** 2026-09-06  
**Baseline:** `d2e393c79c6c2521b68a5c0ee71be46161ce46dd`  
**Trigger:** I-004 research `1524f81b9e9e5e01af4413ea9ea37c1d0f5a5bdf`

## 1. Decision problem

P-001 makes I-004 responsible for cross-artifact semantic validation, but the merged source schemas do not represent several facts that P-001 requires I-004 to validate. This research chooses the smallest amendment that makes I-004 mechanically decidable without redesigning compatibility, IR, runtime, or corpus mappings.

The amendment should preserve I-002 digest algorithms wherever possible. In particular, it should exploit the fact that `profile_semantic_digest()` already expects a normalized `dependencies` record set keyed by `dependency_id` even though `profile.schema.json` currently has no source `dependencies` field.

## 2. Dependency definitions

### Current contradiction

- P-001 §7 defines stable native dependency IDs, dependency kinds, component ownership and complete dependency closure.
- Mapping sources contain only `native_dependencies: [<id>...]`.
- The profile schema contains no dependency-definition records.
- I-002's `profile_semantic_digest()` nevertheless already includes `dependencies`, normalized as a set-like record collection keyed by `dependency_id`.

### Alternatives

**A. New standalone dependency artifact/schema.** Clean separation, but adds another source-file class, discovery/reference rules and schema to a POC that currently has no such artifact. It also requires profile locator fields and more loader plumbing.

**B. Put dependency definitions in each mapping source.** Avoids a new file type but makes shared/profile-level dependencies awkward across multiple mapping files and creates duplicate-definition ownership questions.

**C. Put dependency definitions in the profile manifest.** One authoritative set, naturally aligned with `required_components`, easy stable-ID indexing, and already aligned with the I-002 profile semantic projection.

### Recommendation

Choose **C**. Profile source schema v2 gains required `dependencies`, a non-empty unique-by-semantic-validation array of dependency records. Every record contains:

- `dependency_id` — stable non-empty ID;
- `component_id` — required component owning the assertion;
- `kind` — one accepted dependency kind;
- `assertion` — JSON object whose exact semantic fields depend on `kind` and `dependency_contract_version`;
- optional `evidence` — content-addressed evidence bindings when a claim requires documentary support.

Accepted POC dependency kinds remain the P-001 concepts, with edge/path separated mechanically:

- `component-present`;
- `node-type-present`;
- `feature-present`;
- `edge-present`;
- `path-present`;
- `native-value-present`;
- `value-domain`;
- `extent-interpretation`;
- `adapter-capability`;
- `sidecar-field`.

All profile dependency records are active profile-level requirements. A mapping's `native_dependencies` selects the subset directly needed by that mapping. Complete source dependency closure is therefore the entire profile `dependencies` set; there are no dormant/optional definitions inside one released profile. This matches P-001's no-hidden-partial-activation rule.

The schema should structurally require common fields and known kind, but I-004 should enforce the versioned kind-specific `assertion` contract. This keeps semantic rules in the semantic validator instead of duplicating a large conditional schema.

## 3. Profile schema versioning

Adding mandatory behavior-affecting dependency definitions is not a harmless optional extension. The current profile source contract declares `schema_version: 1` and `additionalProperties: false`.

Recommendation: profile source moves to **`schema_version: 2`**. Do not silently reinterpret existing v1 profiles. The same `profile.schema.json` file becomes the current v2 contract; TFont 0.0.0 has no published profile release that requires dual-version loading yet.

This is compatible with I-002 semantics:

- `profile_semantic_digest()` already includes `schema_version` and `dependencies`;
- no profile-digest algorithm version change is needed;
- the new source representation supplies information that the existing semantic projection already anticipated.

## 4. Kind-specific dependency assertion contract

`dependency_contract_version: 1` defines these semantic assertion fields. I-004, not JSON Schema, validates exact keys/types and rejects unknown fields.

- `component-present`: `{}`.
- `node-type-present`: `{node_type}`.
- `feature-present`: `{node_type, feature}`.
- `edge-present`: `{edge, direction}`, where direction is `out | in`; optional `source_node_type`, `target_node_type`.
- `path-present`: `{steps}`, non-empty ordered list of `{edge, direction}`.
- `native-value-present`: `{node_type, feature, value}`, where value is one exact JSON scalar.
- `value-domain`: `{node_type, feature, domain_mode}` plus `values` where required. `domain_mode` is `observed | documented-bounded | closed | open | unknown`. `observed`, `documented-bounded` and `closed` require a non-empty unique scalar `values` list; `open` and `unknown` prohibit `values`.
- `extent-interpretation`: `{native_object, extent}`, with extent `semantic | anchor-only | source-span | sidecar-zero-span` and `native_object` a non-empty stable native object/path label interpreted by the adapter contract.
- `adapter-capability`: `{capability, minimum_version}`.
- `sidecar-field`: `{field_path}`, where `field_path` is a non-empty ordered list of non-empty path segments.

Evidence rules:

- `documented-bounded` and `closed` value-domain assertions require non-empty dependency evidence;
- a `native-value-present` assertion whose value is `""` or `null` requires non-empty dependency evidence; this is the explicit escape hatch from the dense-empty non-semantic default;
- `extent-interpretation` with `anchor-only` or `sidecar-zero-span` requires non-empty dependency evidence;
- other dependency kinds may carry evidence but are not required to.

I-004 will resolve these evidence bindings through the same evidence index as mapping evidence.

## 5. Native selector contract

The mapping schema currently leaves `native_selector` structurally opaque. A large schema rewrite is unnecessary for P-002; semantic validation can type it under `dependency_contract_version: 1`.

I-004 should accept exactly these selector kinds:

- `feature-value`: `kind`, `component_id`, `node_type`, `feature`, `operator: eq`, `value`, `extent`;
- `node-kind`: `kind`, `component_id`, `node_type`, `extent`;
- `edge`: `kind`, `component_id`, `edge`, `direction`, `extent`, optional source/target node types;
- `path`: `kind`, `component_id`, non-empty ordered `steps[{edge,direction}]`, `extent`;
- `sidecar-field`: `kind`, `component_id`, non-empty `field_path[]`, `extent`;
- `zero-span-entity`: `kind`, `component_id`, `entity_type`, `extent: sidecar-zero-span`;
- `source-span`: `kind`, `component_id`, non-empty `field_path[]`, `extent: source-span`.

`extent` is always one of `semantic | anchor-only | source-span | sidecar-zero-span`. I-004 rejects unknown selector keys rather than silently ignoring them.

For `feature-value` with value `""` or `null`, I-004 requires a referenced `native-value-present` dependency with the same component/node_type/feature/value and evidence; otherwise dense storage empty remains non-semantic.

For `anchor-only` / `sidecar-zero-span`, I-004 requires a corresponding evidence-backed `extent-interpretation` dependency. This prevents technical anchors from becoming semantic extent by spelling alone.

## 6. Applicability contract

The current mapping `applicability` object is also opaque. The first executable POC needs only a bounded contract sufficient for contradiction checks:

- optional `node_type`;
- optional `semantic_domain`;
- optional `preconditions`, a unique list of dependency IDs.

Unknown applicability fields fail I-004 under dependency contract v1. If both selector and applicability declare `node_type`, the values must agree. `semantic_domain`, when present, must be declared by the owning profile. Every applicability precondition must resolve to a profile dependency and therefore to a required component.

This leaves richer Boolean applicability languages for a future versioned contract rather than inventing expression semantics now.

## 7. Review authority

### Current state

The mapping schema embeds the complete review object. A standalone `review.schema.json` duplicates that exact shape, and `tests/i001/test_review_schema_consistency.py` deliberately proves that the standalone record can be embedded unchanged. There is no review-reference field.

### Recommendation

Make the **embedded mapping review authoritative for the first POC**. `review_id` remains a stable audit identifier, but I-004 does not require a separate review artifact and therefore has no “missing review reference” failure. The standalone review schema remains a reusable validation contract for tools that manipulate review records, not a second source of authority that must be joined at compile time.

This matches the already-shipped mapping schema and I-002 digest behavior: review audit provenance is excluded from `mapping_semantic_digest`, while I-004 checks `status` and `reviewed_mapping_digest` readiness.

P-001 prose saying that mappings reference separate review records is superseded by this amendment for the POC.

## 8. Publication relation boundary

The ontology lock has no formalism identifier or relation allowlist. Guessing legality from URI namespaces would violate fail-closed semantics.

Recommendation: in dependency/semantic contract v1, **`publication_relation` must be null for executable I-004-valid mappings**. Non-null publication assertions remain unsupported until a later reviewed contract supplies target-formalism metadata and relation rules (naturally before I-009 publication generation).

The structural mapping schema may continue accepting string-or-null for source/audit compatibility; I-004 returns a stable semantic error for non-null values. This avoids another schema-version churn while staying conservative.

## 9. Ontology target matching

No CURIE prefix map or expansion rule exists in ontology locks. I-004 therefore uses **exact authored-string membership**:

- a top-level target must exactly equal one string in the selected lock's `terms_used`;
- each ambiguous candidate target must exactly equal one string in its own selected lock's `terms_used`.

Both absolute URI and CURIE strings are permitted only when the lock records the same representation. There is no live lookup, prefix guessing, case folding or namespace concatenation.

## 10. Evidence byte boundary

I-004 validates source-addressable evidence integrity as follows:

- every mapping/dependency/candidate evidence ID resolves to exactly one supplied evidence record;
- the binding `content_digest` exactly equals that record's declared digest;
- `normalized-record` evidence digest is recomputed with I-002 and must equal the declaration;
- `external-payload` records are not network-fetched and the cross-artifact validator does not pretend the exact external bytes are embedded when they are not.

If a caller separately has external payload bytes, I-002's `evidence_payload_digest()` can verify them before/alongside I-004. Making payload acquisition mandatory is outside this source-contract amendment.

## 11. Digest compatibility

No I-002 algorithm change is required:

- mapping semantic digest already includes native selector, dependency IDs, applicability and publication relation exactly as authored;
- review remains excluded as designed;
- profile semantic digest already expects `dependencies` and sorts by `dependency_id`;
- profile `schema_version` participates in the semantic projection, so moving source schema to v2 changes identity explicitly rather than silently.

P-002 must include regression tests showing existing I-002 fixed vectors are unchanged and that arbitrary dependency record content still participates in profile semantic digest through the existing projection.

## 12. Required-component authority and dependency closure

I-004 can now define deterministic authority:

- expected parent component IDs == profile `required_components` as sets;
- dependency IDs are unique;
- every dependency `component_id` belongs to `required_components`;
- every mapping selector `component_id` belongs to `required_components`;
- every mapping/applicability dependency reference resolves to one profile dependency;
- all profile dependencies are active release requirements; there is no optional dormant definition;
- compatibility evaluation of whether those dependencies pass on observed bytes remains I-005.

## 13. Plan/implementation boundary

P-002 production changes should be intentionally small:

1. amend P-001 with a clearly marked P-002 override/addendum rather than rewriting historical research;
2. update `profile.schema.json` to profile source schema v2 with required dependency records/common structural shape;
3. update I-001 structural fixtures/tests for v2 and dependency common fields;
4. add no semantic validator production code here;
5. add no compatibility or IR behavior;
6. preserve I-002 algorithms and fixed vectors.

The kind-specific dependency/selector/applicability rules above are normative P-002 design inputs for the subsequent I-004 plan/tests/implementation, not extra behavior to hide in JSON Schema.

## 14. Conclusion

The smallest amendment is:

- profile-owned `dependencies` in source schema v2;
- version-1 semantic rules for dependency assertions, selectors and applicability;
- embedded review as sole mapping review authority;
- null-only executable publication relation for now;
- exact-string ontology-term membership;
- no hidden external evidence retrieval.

This supplies I-004 with all missing machine authority while preserving the already-reviewed I-002 hashing model and keeping I-005/I-006/I-009 boundaries intact.
