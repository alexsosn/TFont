# I-004 research: cross-artifact semantic validation after P-003

**Issue:** #36  
**Status:** research complete; implementation not started  
**Baseline:** P-003 merged `fac75d5a251945653a7be585fa30eae34afd4693`

## Decision

I-004 should add one deterministic, fail-closed **cross-artifact semantic validator** between I-001 structural validation and later compatibility/IR compilation.

It validates relationships among already-loaded, structurally valid source artifacts. It does not inspect a live TF corpus, execute a Context-Fabric query, fetch ontologies/references, evaluate parent compatibility state, or compile semantic indexes.

The public conceptual boundary is:

```text
I-001 load + structural validation
        ↓
I-004 semantic bundle validation
        ↓
validated semantic source bundle
        ↓
compatibility / semantic IR / resolver (later tickets)
```

## 1. Surviving production contracts

### I-001

Keep `load_source`, `loads_source`, `validate_source`, `load_and_validate` and `SourceValidationError` as structural/file boundaries.

I-004 must not duplicate JSON/YAML parsing or JSON Schema validation. Its input is already plain JSON-compatible Python data.

### I-002

Keep:

- RFC 8785/JCS canonicalization;
- exact SHA-256 representation;
- mapping/evidence/profile semantic projection principles;
- set-like UTF-16 ordering and duplicate rejection;
- fail-closed JSON/domain/depth behavior.

P-003 requires a new mapping semantic algorithm/version for mapping-v2 because target-bearing projections, typed ambiguity, routing, capability membership and approximation content alter semantic identity.

I-004 must compare the authored mapping-v2 digest to a freshly computed mapping-v2 semantic digest. A stale digest is invalid even when the object is structurally valid.

### I-003

Keep parent-component manifest projection/digest as identity only.

I-004 may compare the expected parent manifest's component IDs with profile `required_components` and dependency `component_id`s. It does not inspect component bytes or decide current compatibility.

### P-002

Keep the exact v1 dependency kinds and their closed assertions. I-004 resolves dependency IDs, component authority and evidence bindings; it does not reinterpret the assertion shapes.

### P-003

The semantic source model is now:

- native semantic record;
- zero or more approved target-bearing projections;
- zero or more typed ambiguous candidates only when record state is `ambiguous`;
- zero or more non-projection external references;
- controlled profiles/capabilities;
- R-015 ontology bundle/bridge inputs;
- R-016 approximation contract;
- R-017 routing/reference contract.

## 2. Input artifact bundle

The minimum I-004 API should accept an in-memory bundle, conceptually:

```python
SemanticSourceBundle(
    profile=...,
    expected_parent_manifest=...,
    mappings=...,
    ontology_locks=[...],
    evidences=[...],
    reviews=[...],            # only if standalone review records remain in the source model
    ontology_bundle=...,      # source identity/configuration, not runtime state
    bridges=[...],
    profile_catalog=...,
    reference_catalog=...,
)
```

P-003 implementation may choose dataclasses or plain dictionaries internally, but the public validator must not take filesystem paths as semantic inputs.

Every source object should carry a logical `source_name` in the wrapper/index so deterministic diagnostics can identify both artifact kind and local path.

### Why one bundle

Cross-artifact checks require simultaneous indexes over:

- components;
- dependencies;
- mappings/projections/candidates/references;
- ontology locks and `terms_used`;
- evidence records;
- profile/capability vocabulary;
- bridge/bundle records.

Passing separate resolver callbacks would make duplicate/reference precedence order-dependent and harder to reproduce.

## 3. Artifact indexes

Build indexes before semantic rules execute.

Required unique indexes:

```text
component_id -> parent component record
dependency_id -> P-002 dependency
mapping_id -> native semantic record
projection_id -> approved target-bearing projection
candidate_id -> ambiguous candidate
lock_id -> ontology lock
bridge_id -> bridge
bundle_id -> ontology bundle/config identity
evidence_id -> evidence
profile_id -> profile contract/catalog entry
capability_id -> capability catalog entry
```

Reference records that need stable IDs should also receive one and be duplicate-checked.

Duplicate IDs fail closed before missing-reference checks for the duplicated namespace.

No silent "last record wins" behavior.

## 4. Deterministic validation phases

Use a fixed phase order so multiple-fault bundles produce stable first errors.

Recommended v1 precedence:

1. **bundle shape/version precondition** — exact supported semantic contract/catalog versions;
2. **duplicate identity indexing** — all artifact ID namespaces;
3. **profile/parent component authority** — `required_components`, expected parent component IDs;
4. **dependency closure** — dependency IDs, dependency component authority, evidence refs;
5. **controlled vocabulary membership** — profile/capability, formal kind, semantic role, routing/query role, assessment, identity strength, loss tokens;
6. **native record state shape** — positive vs ambiguous/native-only/unsupported consistency;
7. **projection/candidate/reference cross-field legality** — routing pairs, kind/role matrix, candidate restrictions, reference-family restrictions;
8. **ontology lock/target membership** — lock exists, target belongs to the exact locked `terms_used` set when target membership is required;
9. **bundle/bridge source closure** — referenced locks/bridges/endpoints/scope identities exist and are content-bound; do not evaluate runtime compatibility state here;
10. **evidence binding** — every evidence binding resolves and digest matches current evidence identity;
11. **semantic digest/review binding** — mapping/projection/review content digest equality;
12. **P-002 semantic-source guardrails** — dense-empty/value-domain assertions require explicit native semantic dependencies, not mere source-field presence;
13. **approximation contract legality** — R-016 structural/semantic authorization shape only;
14. **publication relation legality** — R-013 formal-kind matrix plus locally provable R-017 same-entity rule;
15. **validated result assembly**.

This order intentionally validates identity/reference closure before expensive semantic consistency and keeps diagnostics independent of input list ordering.

## 5. Diagnostic model

I-004 should use a dedicated error type rather than overloading I-001 `SourceValidationError`.

Conceptually:

```python
@dataclass(frozen=True)
class SemanticValidationProblem:
    category: str
    message: str
    artifact_kind: str
    source_name: str
    path: tuple[str | int, ...]
    related_id: str | None = None

class SemanticValidationError(ValueError): ...
```

Categories should be stable machine tokens, not exception-class names.

Minimum category families:

```text
unsupported_contract_version
duplicate_id
missing_reference
component_authority
invalid_record_state
invalid_projection
invalid_candidate
invalid_reference_routing
unknown_vocabulary
kind_role_conflict
unknown_ontology_target
bundle_closure
bridge_closure
evidence_digest_mismatch
stale_semantic_digest
stale_review_binding
native_semantics_unproven
invalid_approximation
invalid_publication_relation
```

The exact category strings should be frozen in the implementation plan/RED before production code.

## 6. Parent/component authority

I-004 can validate from canonical sources:

1. every profile `required_components` ID exists in expected parent manifest;
2. no required-component ID is duplicated;
3. every P-002 dependency `component_id` is in `required_components` and exists in expected parent manifest;
4. every mapping/native binding names only components authorized by its resolved dependencies/source contract;
5. P-002 `component-present` cannot authorize a component outside profile authority.

I-004 cannot prove the currently loaded TF bytes match expected parent identity. That remains compatibility/runtime inspection.

## 7. P-002 dependency and dense-value semantics

Structural P-002 validity is necessary but not sufficient.

### Native value

A mapping that treats `""` or `null` as semantic must resolve to a `native-value-present` dependency whose assertion contains the same node type/feature/value and `value_semantics=semantic`.

Dense TF storage or feature existence alone is insufficient.

### Value domain

A mapping/profile claim that depends on a closed domain must resolve to a `value-domain` dependency with `domain_semantics=closed-reviewed`, non-empty evidence and the exact relevant values.

`domain_semantics=observed` never authorizes closed-domain reasoning.

I-004 validates source-contract consistency only. It does not scan the corpus to verify actual value occurrence.

## 8. Native record state and projections

### Positive record

A positive record may carry one or more approved projections and/or non-projection external references.

Each approved projection independently carries its R-002 assessment among:

`exact | close | broader | narrower | related`.

### `native-only`

Must have zero approved target-bearing projections and zero ambiguous candidates.

It may retain provenance/locator/catalogue/native identity references when those are not fabricated semantic/authority targets.

### `unsupported`

Must have zero approved target-bearing projections and zero ambiguous candidates. It is negative concept knowledge and cannot activate profile/capability support by itself.

### `ambiguous`

Must have zero approved target-bearing projections and at least one fully typed candidate.

Candidates must include target, routing, formal kind, semantic role, profile/capability, ontology lock and evidence. They must not carry execution authorization, approximation authorization or positive publication authorization.

## 9. Complementary projection validation

I-004 cannot generally prove two projections are semantically complementary from ontology logic alone, but it can reject mechanical contradictions:

- duplicate projection IDs;
- same projection identity duplicated with conflicting content;
- projection routed as authority-value but query role `semantic-constraint`;
- candidate and approved projection sharing the same ID;
- no-target record carrying an approved projection;
- mutually exclusive state flags if the schema exposes them;
- incompatible kind/role pair.

Whether two distinct reviewed projections are philosophically compatible remains review content; I-004 verifies that each review is bound to the exact projection content.

## 10. Controlled vocabulary validation

Use the exact P-003 vocabulary freeze.

Unknown tokens fail closed; no aliases, case folding, fuzzy matching, namespace inference or local-name inference.

Profile/capability IDs are validated against the pinned catalog version. Optional profile ID existence does not imply activation.

Capability activation is not computed by I-004 beyond validating authored membership/source records. Operational `active|absent|unavailable` belongs to compiled runtime/compatibility state.

## 11. R-013 kind/role and publication rules

I-004 validates the closed formal-kind/semantic-role compatibility matrix.

At minimum reject:

- class + relation/attribute/particular identity;
- property + entity-type/particular identity;
- SKOS concept + relation/attribute;
- named resource used as ontology class/property semantics.

Artifact declaration metadata can strengthen rejection when a locked ontology property has a primitive/literal range but projection claims entity-valued relation execution.

Publication relation is independent of mapping assessment.

Never derive:

```text
exact -> skos:exactMatch
exact -> owl:sameAs
exact -> owl:equivalentClass
exact -> owl:equivalentProperty
broader/narrower -> rdfs hierarchy
```

`owl:sameAs` is locally legal only for entity-identity + `same-entity`; canonical OWL namespace spelling must be exact. Other positive publication predicates require formal-kind-aware validation and otherwise fail closed.

## 12. Ontology target/lock membership

For every target-bearing approved projection and ambiguous candidate:

1. `ontology_lock` resolves uniquely;
2. target identity is a stable non-empty target resource;
3. target is present in the exact lock's `terms_used` set;
4. any declaration evidence referenced by the projection belongs to the same lock identity/release;
5. target kind is not inferred from URI text.

`terms_used` membership is a cross-artifact declaration check, not proof that the ontology file itself really contains the term. If ontology snapshot truth validation is implemented separately, I-004 may consume its validated artifact; it must not do network resolution.

## 13. R-015 bundle/bridge boundary

I-004 validates source closure/content identity for bundle/bridge records:

- referenced lock IDs exist;
- bridge endpoint IDs/releases/digests match source records;
- scoped terms belong to endpoint `terms_used`;
- bridge reviewed-content digest matches bridge content;
- active edge references are syntactically/semantically resolvable.

I-004 does **not** decide current runtime compatibility or produce `satisfied-exact-lock` / `satisfied-reviewed-bridge` operational states. Later bundle/compatibility assembly consumes the validated source records.

This avoids duplicating R-015's runtime evaluator inside source validation.

## 14. R-016 approximation validation boundary

I-004 validates authored approximation content, not request-time execution.

Rules:

- approximation object allowed only on `close|broader|narrower` projections;
- `related` cannot be approximation-executable;
- eligible must be exact boolean if represented as boolean;
- reviewed `broader` eligible loss set must include only `undercoverage`;
- reviewed `narrower` eligible loss set must include only `overcoverage`;
- executable `close` authorization needs explicit reviewed loss shape (`undercoverage`, `overcoverage`, or both);
- unknown/future loss tokens fail closed;
- approximation evidence/review content participates in mapping/projection semantic identity.

Caller `semantic_mode` and `accept_losses` are runtime request inputs and are out of scope for I-004.

## 15. R-017 routing and identity rules

### Target-bearing projection routing

Valid exact pairs:

```text
semantic-pivot  + semantic-constraint
authority-value + authority-value-filter
```

Cross-pairing fails.

Authority-value projections remain outside the common semantic index later, but I-004 only validates their routing metadata.

### Non-projection references

Valid kind/query-role routing:

```text
entity-identity      -> identity-filter
catalogue-identifier -> identifier-filter
provenance-source    -> metadata-filter | explanation-only
locator              -> explanation-only
```

Entity identity strength is exactly:

```text
same-entity
probable-same-entity
related-record
ambiguous-identity
```

Catalogue identifiers require non-empty issuer/namespace and value.

Provenance/locator records require an actual external reference value but never authorize network access.

## 16. Evidence and review binding

Evidence bindings resolve by `evidence_id` and exact content digest.

A binding to an evidence ID with a different current digest fails even if the ID exists.

Review authority must be content-bound to the semantic object it authorizes.

P-003 requires projection-level semantic identity/review binding. The implementation must avoid one record-level review accidentally authorizing a newly added projection or changed approximation block.

Recommended migration direction:

- native record has its own semantic digest/review for native meaning and membership;
- each approved projection has a projection semantic digest/review;
- each ambiguous candidate carries evidence but not executable review authorization;
- entity-identity claims needing execution carry identity-content review binding;
- final mapping semantic digest binds normalized native content + child semantic identities.

Exact digest field names/algorithms are an I-004 implementation-plan decision, but the old mapping-v1 digest is insufficient and must be versioned.

Audit-only reviewer timestamp/display edits may remain outside semantic content identity when consistent with accepted I-002 boundaries; changing reviewed content or the digest it binds invalidates review readiness.

## 17. What I-004 cannot validate

Without concrete parent/runtime inspection, I-004 cannot prove:

- a TF node type/feature/edge actually exists in the installed parent;
- an observed value actually occurs;
- current corpus bytes match expected identity;
- a query plan is executable in Context-Fabric;
- active profile/bundle operational availability;
- runtime approximation caller acceptance;
- network URI dereferenceability;
- semantic truth from labels/ontology hierarchy;
- empirical completeness of an observed value domain.

These remain compatibility/runtime/IR/resolver responsibilities.

## 18. Minimal public result

Successful validation should return an immutable/explicit `ValidatedSemanticBundle` (or equivalent) containing the same source objects plus deterministic indexes/fingerprints needed by the next stage.

It must not mutate the source mapping objects or enrich them with inferred semantic targets.

The validated result may include:

- ID indexes;
- mapping-v2 semantic digest(s);
- expected parent manifest digest;
- profile/catalog version identities;
- ontology bundle source identity;
- deterministic source provenance.

It must not contain a compiled semantic reverse index; that belongs to the next P-003 slice.

## 19. RED matrix for the implementation plan

The first RED suite should cover:

1. minimal valid mapping-v2 bundle;
2. missing/extra/unauthorized parent component;
3. missing or duplicate dependency/lock/evidence/profile/capability IDs;
4. all eight assessment meanings in their P-003 locations;
5. native-only/unsupported with target projection rejected;
6. ambiguous with zero candidate rejected;
7. under-typed candidate rejected;
8. candidate execution/approximation/publication authorization rejected;
9. kind/role conflict;
10. semantic-pivot/authority-value routing mismatch;
11. external reference routing mismatch;
12. duplicate scoped identifier namespace/value handling;
13. unknown target outside lock `terms_used`;
14. bridge endpoint/scope/digest mismatch;
15. evidence binding digest mismatch;
16. stale mapping/projection semantic digest;
17. stale review binding;
18. audit-only review provenance control remains valid;
19. dense empty/null without matching `native-value-present` semantic dependency;
20. closed-domain claim backed only by `observed` dependency;
21. invalid approximation loss/assessment combination;
22. publication relation/kind mismatch;
23. noncanonical OWL sameAs spelling rejected/delegated fail-closed;
24. deterministic first-error precedence with two simultaneous faults.

## 20. Research conclusion

I-004 is now sufficiently specified to enter implementation planning.

The validator should be a pure, deterministic semantic-source checker over already-structurally-valid in-memory artifacts. It closes references, authority, target typing, evidence, review and semantic identity; it deliberately stops before parent inspection, operational compatibility, IR compilation and Context-Fabric execution.
