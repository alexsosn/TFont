# I-004 research: cross-artifact semantic validation

**Issue:** #36  
**Recorded:** 2026-09-06  
**Baseline:** `d2e393c79c6c2521b68a5c0ee71be46161ce46dd` (I-001, I-002, I-003 merged)  
**Status:** research complete; implementation plan is blocked on an explicit source-contract design amendment.

## 1. Question

P-001 assigns I-004 the cross-artifact semantic-validation stage between structural validation and compatibility/IR compilation. Before planning production code, this research checks whether the merged source schemas and deterministic helpers actually contain enough machine-readable information to enforce the accepted I-004 invariants without inventing new public semantics.

The answer is **partly, but not fully**. Several important invariants are implementable directly from the merged contracts. Others require fields/representation choices that are absent or contradictory in the accepted source model. Per P-001 §28 and `AGENTS.md`, I-004 must not guess those choices in production code.

## 2. Accepted normative requirements

P-001 requires cross-artifact semantic validation after JSON Schema validation and before exact-parent compatibility/IR work. Relevant accepted rules include:

- profile `required_components` is authoritative and the expected parent manifest contains exactly those components;
- mapping `native_dependencies` names stable dependency IDs and every dependency belongs to an authoritative required component;
- the complete dependency closure is profile-level dependencies plus all active mapping dependencies;
- `exact | close | broader | narrower | related` require one external target and one top-level ontology lock;
- `ambiguous` has no top-level target/lock/publication relation and owns candidate-specific locks/evidence;
- `native-only | unsupported` have no target/lock/publication relation;
- ontology targets must be known to the pinned lock;
- mapping evidence bindings are content-addressed;
- reviewed mappings must bind to the recomputed mapping semantic digest;
- dense TF empty storage is non-semantic unless explicit source semantics proves otherwise;
- contradictory selector/applicability metadata and illegal publication relations must fail closed;
- I-004 does **not** evaluate compatibility state, probe changed parents, compile IR, execute native queries, or infer semantics from feature-name/storage coincidence.

P-001 §26 explicitly describes I-004 as validating required-component authority, all eight assessment shapes, candidate-specific ontology locks, ontology targets, native dependencies, evidence digests, dense-empty assertions and review-digest binding.

## 3. Merged structural source model

### 3.1 Profile schema

`src/tfont/schemas/profile.schema.json` contains:

- `profile_id`, `profile_version`, semantic domains;
- one `parent_component_manifest` locator;
- `required_components` as unique string IDs;
- `ontology_locks` as unique string IDs;
- `mapping_sources` as unique string paths;
- dependency-contract version and runtime/license metadata.

It contains **no dependency-definition collection**, no evidence-source list, and no review-source list.

### 3.2 Parent component schema

The parent manifest contains `algorithm` and component records with `component_id`, `kind`, `identity_algorithm`, and `content_digest` plus optional locator/license metadata. I-003 adds deterministic parent projection/digest helpers and stable filesystem identity errors.

This is sufficient for source-only equality between `required_components` and expected component IDs. It is deliberately insufficient for proving changed-parent compatibility; that belongs to I-005.

### 3.3 Mapping schema

`mapping.schema.json` structurally pins all eight assessment labels and already enforces the broad target/lock/candidate nullability shapes. It also contains:

- `native_dependencies`: unique strings only;
- `native_selector`: merely `type: object`, `minProperties: 1`;
- `applicability`: unconstrained object;
- external target / top-level lock / candidate projections;
- evidence bindings `(evidence_id, content_digest)`;
- a **fully embedded `review` object**;
- `mapping_semantic_digest`.

The embedded review object has the same shape as the standalone `review.schema.json`. `tests/i001/test_review_schema_consistency.py` explicitly proves a standalone review record is accepted unchanged when embedded in a mapping. There is no `review_ref` field and no mapping field whose semantics is “look up this separate review artifact”.

### 3.4 Ontology-lock schema

An ontology lock contains `lock_id`, ontology metadata, `term_namespace`, source/release/content metadata and `terms_used` as a unique list of non-empty strings.

It contains no CURIE prefix map, no canonical-term expansion rule, no target-formalism identifier and no allowlist/rules for `publication_relation`.

### 3.5 Evidence schema

Evidence records support:

- `external-payload`: `content_digest` names the exact reviewed payload digest but payload bytes are not embedded;
- `normalized-record`: `reviewed_content` is present and I-002 can recompute `evidence_record_digest()`.

I-002 separately exposes `evidence_payload_digest(payload)` when exact external bytes are supplied.

For I-004 cross-artifact validation, binding equality between a mapping and the referenced evidence record is source-checkable. Recomputing normalized-record evidence is also source-checkable. Recomputing external-payload evidence is only possible if the caller supplies the reviewed payload bytes; the canonical record alone intentionally does not contain them.

## 4. Merged deterministic helper boundary

I-002 exposes deterministic JCS/digest projections including:

- `evidence_record_digest()` / `evidence_payload_digest()`;
- `mapping_semantic_projection()` / `mapping_semantic_digest()`;
- normalized set ordering and evidence/candidate ordering;
- stable `DigestError` paths.

Therefore I-004 must reuse `mapping_semantic_digest()` rather than independently reimplement mapping identity. Audit-only review fields are already excluded from the mapping digest by construction.

I-003 exposes parent/component identity only. It deliberately does not infer native dependency semantics or compatibility.

## 5. Invariants implementable without a design change

A deterministic source-object validator can safely implement all of the following on the current model:

1. duplicate profile/mapping/lock/evidence IDs across supplied artifacts;
2. `required_components` equality to expected parent component IDs, including missing/extra components;
3. each mapping `profile_id` equals the owning profile ID;
4. each top-level mapping ontology-lock ID exists and is declared by the profile;
5. each ambiguous candidate lock exists and is declared by the profile;
6. external target membership by **exact authored string** in the selected lock's `terms_used` list (no namespace/CURIE rewriting exists to justify anything else);
7. mapping evidence IDs resolve to supplied evidence records;
8. each mapping evidence binding digest equals the referenced evidence record's declared `content_digest`;
9. normalized-record evidence `content_digest` equals recomputed `evidence_record_digest()`;
10. candidate evidence bindings obey the same resolution/digest rules;
11. recomputed `mapping_semantic_digest()` equals the mapping's declared digest;
12. embedded review readiness: for `status: reviewed`, `reviewed_mapping_digest` equals the recomputed mapping digest; audit-only review provenance edits therefore do not invalidate the digest;
13. the already structurally modeled eight assessment target/lock/candidate shapes can be rechecked semantically where cross-artifact lock/target resolution is involved;
14. stable deterministic indexing/error precedence over caller-supplied structurally valid objects.

These checks do not require live ontology access, concrete parent probing, or I-005 compatibility state.

## 6. Design-blocking gaps

### 6.1 No dependency-definition source representation

This is the hard blocker for the accepted I-004 scope.

P-001 §7 says mappings reference stable dependency IDs through `native_dependencies`, describes dependency kinds, requires every dependency to name a component from `required_components`, and defines complete dependency closure as profile-level dependencies plus mapping dependencies.

But the merged profile schema has **no dependency definitions at all**; the mapping schema stores only dependency ID strings; and there is no dependency schema/file type elsewhere in the merged source contracts.

Consequences:

- I-004 cannot distinguish a valid dependency ID from a missing reference;
- it cannot verify the dependency's `component_id` authority;
- it cannot validate dependency kind/direction/value/extent/adapter fields;
- it cannot compute the accepted complete source dependency closure.

Adding a `dependencies` field or a new dependency artifact inside I-004 would be a public source-contract change and therefore requires an explicit design amendment first.

### 6.2 Native selector/applicability contract is structurally opaque

P-001 enumerates selector kinds (`feature-value`, node-kind, directed edge, ordered path, sidecar-field, zero-span-entity, source-span) and requires explicit extent/direction semantics. It also requires contradictory selector/applicability metadata and dense-empty semantic claims to fail.

The current mapping schema accepts any non-empty object for `native_selector` and any object for `applicability`. There is no machine contract defining required/allowed fields per selector kind, no typed direction/path shape, and no structural representation of observed-vs-documented/closed value-domain claims.

I-004 therefore cannot enforce the accepted selector/extent/dense-empty rules without inventing those shapes. This also requires a design/schema amendment.

### 6.3 Review representation is internally inconsistent

P-001's canonical-bundle description says review records are content-addressed/source artifacts referenced by stable IDs, and I-004's prose talks about missing review references. The merged mapping schema instead embeds the complete review record directly, while a separate standalone review schema duplicates that same shape. The consistency test explicitly treats the standalone shape as embeddable.

There is no reference edge for I-004 to resolve. A production validator cannot both require a separate review artifact and remain compatible with the merged mapping schema without a design decision.

The amendment must choose one authoritative POC representation:

- embedded review is canonical and separate review files are not required for mapping validity; or
- mapping source uses an explicit review reference and standalone review artifacts become authoritative.

### 6.4 Publication-relation legality lacks formalism metadata

P-001 requires non-null `publication_relation` to be independently justified and legal for the approved target formalism. Current ontology locks do not identify a publication formalism or allowed relation vocabulary. I-004 can preserve nullability rules but cannot determine whether a non-null relation is legal without another accepted machine contract.

### 6.5 CURIE/URI equivalence is unspecified

P-001 permits external URI/CURIE targets. Current locks expose only `term_namespace` plus exact string `terms_used`; no prefix mapping or expansion rule exists.

The only deterministic validation possible without new semantics is exact-string membership. If semantic CURIE expansion/equivalence is desired in I-004, the amendment must define it. Research recommendation for the first POC is to keep I-004 exact-string only and require `terms_used` to contain the exact target representation used by mappings.

## 7. Evidence boundary recommendation

Do not make external evidence retrieval a hidden I-004 behavior.

For `normalized-record`, I-004 should recompute the record digest from canonical source fields.

For `external-payload`, I-004 can always verify mapping-binding equality to the declared evidence record digest. Exact payload-byte verification should be an explicit optional/required caller input only if a later design says build-time source bundles include those bytes. Missing bytes must never trigger network retrieval or silent trust escalation.

This choice does not require a source-schema change, but the eventual I-004 plan should state the API boundary explicitly after the design amendment resolves the harder source-model gaps.

## 8. Deterministic diagnostic model recommendation

Once unblocked, use one I-004 error type with a machine category and a tuple path into a logical bundle object. Deterministic phase ordering should be:

1. exact input container/type/index construction;
2. duplicate IDs;
3. profile/parent authority;
4. cross-artifact reference existence;
5. lock/target and evidence binding integrity;
6. dependency/selector semantic rules;
7. recomputed mapping digest;
8. review readiness binding.

Within a phase, sort records by UTF-16 code-unit order of stable IDs before validation, matching existing I-002 set semantics. This avoids input enumeration order changing the first reported problem.

The exact category names belong in the implementation plan after the missing machine contracts are fixed.

## 9. Runtime/compatibility boundary

I-004 must not claim to validate facts that require inspecting an observed changed parent. Source-only validation can establish that declared dependencies are well formed and refer to authoritative components once dependency definitions exist. Whether those dependencies pass on a concrete observed parent belongs to I-005/adapters.

Likewise dense-empty handling in I-004 is a declaration/contract check: source semantics must explicitly encode any claim that storage empty has semantic meaning. I-004 must never inspect a finite observed release and infer closure/absence itself.

## 10. Conclusion and gate decision

I-004 is **unblocked at the dependency level** because I-001..I-003 are merged, but it is **blocked at the accepted source-contract level**.

A production plan that implemented the full P-001 I-004 scope today would have to invent at least dependency-definition representation and selector semantics, and would have to choose a review/publication-relation interpretation not fixed by the merged schemas. That would violate the project's explicit no-silent-semantic-change rule.

Therefore the next gate is an explicit design amendment. No I-004 plan, RED tests or production code should be committed until that amendment decides at minimum:

1. canonical dependency-definition representation and kinds;
2. minimum typed native-selector/applicability/extent/value-domain contract needed by I-004;
3. authoritative review representation (embedded vs referenced standalone artifact);
4. publication-relation/formalism validation boundary;
5. exact-string versus expanded CURIE target matching.

After the amendment is independently reviewed and merged, I-004 can resume with a plan grounded in the amended source contract.
