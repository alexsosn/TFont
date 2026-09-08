# P-003 plan: common ontology semantic adapter architecture

**Issue:** #44  
**Type:** design-only architecture amendment  
**Baseline:** `main` after P-002 (`a238522c3048ee077a09e090a4b067b72cec901c`)  
**Inputs:** R-001..R-017, R-017 post-review amendment, A-001, merged I-001/I-002/I-003, merged P-002

## 1. Decision

TFont's primary runtime contract is a **reviewed semantic compatibility layer over already-materialized Text-Fabric / Context-Fabric corpora**.

```text
source representations
        ↓ corpus-specific materializer/converter
materialized TF / Context-Fabric corpus
        ↓
TFont native semantic records
        ↓
0..N reviewed typed target-bearing projections
 + 0..N non-projection external-reference records
        ↓
content-addressed active ontology bundle + reviewed bridge closure
        ↓
semantic / authority / identity / identifier resolution
        ↓
native Context-Fabric query plan
        ↓
results + provenance + semantic-loss explanation
```

TFont does not own generic JSON/XML/CSV/TEI/PDF/database/API ingestion, arbitrary source-record addressing, network dereferencing, adapter authentication/caching, or a generic sidecar/native-adapter runtime.

The central modeling change is:

> A mapping is a reviewed **native semantic record** with one native binding and **zero or more complementary typed target-bearing projections**. A projection is the smallest reviewed unit that can participate in either the common semantic-pivot reverse index or the authority-value reverse index.

Entity-identity, catalogue-identifier, provenance-source and locator references are kept in a separate external-reference collection with their own index/query rules.

This replaces the current one-record/one-`external_target` model.

`native-only` and `unsupported` remain legitimate first-class reviewed native records with no target-bearing projection. Ambiguity is represented explicitly and never converted into simultaneous complementary projections.

## 2. Normative semantic basis

### 2.1 Seven-model common pivot

The first common semantic pivot remains:

- SKOS;
- OLiA;
- OntoLex-Lemon;
- CIDOC CRM;
- CRMtex;
- LRMoo;
- CRMinf.

Their roles are profile-specific and composable; no ontology namespace is itself a semantic capability.

### 2.2 Supporting standards/tooling

Preserve accepted R-002 governance:

- PROV-O: provenance infrastructure where used;
- SHACL 1.0: RDF validation/publication tooling, not runtime query execution;
- Web Annotation: optional publication/targeting profile;
- CRMarchaeo, CRMsci, LexInfo, Lexicog, VarTrans, Getty AAT, PeriodO and similar resources: optional/domain or authority profiles activated only by reviewed evidence.

No live RDF reasoner, SPARQL endpoint, or HTTP ontology lookup is required at runtime.

## 3. Native semantic record contract

A native semantic record represents one reviewed native meaning in one corpus/profile context.

Conceptually:

```yaml
native_record:
  mapping_id: stable-id
  corpus_id: stable-corpus-id
  native_binding:
    selector: materialized-TF selector/value/entity/path description
    applicability: reviewed source/entity/value domain
    execution_shape: membership | value-predicate | edge-path | identity-key | inspection-only
  native_dependencies: [P-002 dependency ids]
  profiles: [controlled profile ids]
  capabilities: [controlled capability ids]
  native_state: positive | native-only | unsupported | ambiguous
  projections: [0..N target-bearing projections]
  ambiguous_candidates: [0..N non-approved target candidates]
  external_references: [0..N identity/catalogue/provenance/locator records]
  evidence: [...]
  review: content-bound review
  mapping_semantic_digest: versioned semantic digest
```

Field spellings may differ in implementation, but the distinctions are normative.

### 3.1 Native binding remains TF-native

The binding may refer only to already-materialized TF/Context-Fabric facts represented through the accepted P-002 dependency vocabulary:

- `component-present`;
- `node-type-present`;
- `feature-present`;
- `edge-present`;
- `path-present`;
- `native-value-present`;
- `value-domain`;
- `extent-interpretation`.

No `native-adapter`, sidecar path, external record/file field, database/API locator, source-format selector, or URI dereference instruction is permitted.

### 3.2 Native record state and the eight accepted meanings

The eight accepted R-002 assessment meanings remain observable without forcing one record-level target field:

- approved target-bearing projections carry `exact | close | broader | narrower | related` individually;
- `ambiguous` is a native-record state with one or more explicit non-approved candidates and no executable common/authority target;
- `native-only` is a reviewed positive native state with no accepted target-bearing projection;
- `unsupported` is reviewed negative knowledge.

A record must not claim `native-only` or `unsupported` while carrying an approved target-bearing projection.

Ambiguous candidates never enter semantic or authority reverse indexes.

## 4. Target-bearing projection contract

Each approved projection is independently typed, routed and reviewed.

Conceptually:

```yaml
projection:
  projection_id: stable record-local or global id
  target: locked IRI/resource id
  reference_kind: semantic-pivot | authority-value
  query_role: semantic-constraint | authority-value-filter
  formal_kind: class | property | skos-concept | named-resource
  semantic_role: controlled R-013 role
  profile_id: controlled R-014 profile
  capability_id: controlled R-014 capability
  assessment: exact | close | broader | narrower | related
  ontology_lock: participating lock identity
  ontology_bundle_requirement: active bundle/profile requirement
  ontology_declaration_evidence: optional locked class/property/domain/range facts
  publication_relation: optional, independently validated
  native_execution_binding: role-compatible TF-native binding
  approximation: optional R-016 reviewed authorization/loss contract
  evidence: [...]
  review: projection-content-bound review
```

`reference_kind` is the R-017 routing dimension. `semantic-pivot` enters the ordinary common semantic target space; `authority-value` enters the authority-value target space. Neither routing choice bypasses R-003/R-015 prerequisites or R-016 for non-exact execution.

### 4.1 Closed formal kinds

P-003 freezes the first production vocabulary to:

- `class`;
- `property`;
- `skos-concept`;
- `named-resource`.

OWL `ObjectProperty` / `DatatypeProperty` remain locked ontology declaration metadata, not canonical TFont kinds.

### 4.2 Closed semantic roles

P-003 freezes the first production vocabulary equivalent to:

- `entity-type`;
- `annotation-category`;
- `annotation-value`;
- `relation`;
- `attribute`;
- `lexical-entry-identity`;
- `lexical-form-identity`;
- `lexical-sense-identity`;
- `lexical-concept-identity`;
- `authority-reference`;
- `claim-proposition`;
- `inference-activity`.

`authority-reference` is compatible with an `authority-value` routed projection where a reviewed external controlled value is the target. It does not make that target part of the ordinary semantic-pivot reverse index.

Formal kind does not determine semantic role. Role does not determine publication relation. URI syntax does not determine either.

### 4.3 Kind/role validation

At minimum the production validator must enforce:

- `class` → entity/category/value roles, never relation/attribute/particular identity;
- `property` → relation/attribute/annotation-category, never entity-type or particular identity;
- `skos-concept` → annotation value, lexical concept, authority reference; never relation/attribute;
- `named-resource` → particular lexical identities, authority reference, proposition/inference identity; never ontology class/property semantics.

Exceptional RDF multi-typing is represented by separate reviewed projections when execution/publication semantics differ.

### 4.4 Complementarity versus ambiguity

Multiple approved projections are **complementary** when all are simultaneously true of the same native semantics and serve different compatible roles or ontology dimensions.

Examples:

- physical-object semantic-pivot projection plus reviewed material authority-value projection;
- lexical-entry entity-type projection plus a separately reviewed particular lexical identity reference;
- written-text segment class plus a relation projection connecting it to a carrier.

Mutually exclusive candidate targets remain `ambiguous_candidates` and are not approved projections.

The validator must reject both failure modes:

- collapsing compatible complementary projections into ambiguity;
- representing unresolved alternatives as simultaneously approved projections.

## 5. Controlled profiles and capabilities

Replace free-form `semantic_domains` as execution/discovery authority with the R-014 catalog.

### 5.1 First profile catalog

Core profiles:

- `structural`;
- `linguistic`;
- `lexical`;
- `written-text`;
- `textology`;
- `heritage`;
- `scholarly-inference`.

Optional evidence-gated profiles:

- `archaeology`;
- `scientific-analysis`;
- `lexicography`.

Profile operational state is exactly:

`active | absent | unavailable`.

A profile is active only when at least one capability is active. A capability is active only when at least one reviewed positive native record actually instantiates it.

No profile inheritance auto-activates another profile.

### 5.2 Capability catalog

Initial capability IDs are the accepted R-014 controlled identifiers:

```text
structural.entity-kind
structural.slot-coverage
structural.edge-traversal
structural.section-navigation

linguistic.part-of-speech
linguistic.morphology
linguistic.syntax
linguistic.discourse

lexical.entry
lexical.form
lexical.sense
lexical.concept
lexical.relation

written-text.segment
written-text.sign
written-text.writing-system
written-text.transcription-recognition

textology.textual-version
textology.witness
textology.fragment-transmission
textology.apparatus-reading
textology.witness-attestation
textology.explicit-omission

heritage.physical-object
heritage.physical-part
heritage.identifier
heritage.material
heritage.place-provenance
heritage.custody-location

scholarly-inference.claim
scholarly-inference.inference
scholarly-inference.meaning-comprehension
scholarly-inference.provenance-assessment
```

Optional profile capabilities require versioned catalog additions backed by evidence; they are not inferred from free-form labels.

Profile/capability state is discovery information only. Target resolution is authorized only by an exact requested projection tuple in the appropriate index family.

## 6. Ontology bundle and bridge prerequisite

R-015 is authoritative for semantic composition.

### 6.1 Active bundle identity

The executable semantic environment is content-addressed from:

```text
active profile-contract IDs
+ full I-002 semantic ontology-lock identities
+ reviewed term-scoped bridge artifacts referenced by active edges
+ active dependency bindings
```

using accepted JCS/SHA-256 semantics.

No resolver path may weaken bundle failure into an approximation.

### 6.2 Bridge closure

A bridge is executable only if:

- endpoint lock IDs/releases/payload digests match participating locks;
- bridge term scope matches the active dependency edge;
- scoped terms belong to endpoint lock `terms_used`;
- bridge content digest matches reviewed content;
- review state is accepted;
- compatibility is explicit;
- runtime strength is exact for the v1 active bundle gate.

A CRMtex F28 bridge does not imply ontology-wide equivalence. Optional profiles that are inactive do not inject bridge requirements into the active bundle.

### 6.3 Version-skew consequences

Preserve accepted bridge cases, including:

- CRMtex 2.0 historical FRBRoo/LRMoo continuity;
- CRMarchaeo 2.1.1 CRM 7.1.2 / CRMsci 2.0 dependencies versus current CRM 7.1.3 / CRMsci 3.2.

An inactive optional archaeology profile is not a bridge failure. Activating archaeology with unresolved required bridges makes that capability unavailable/non-executable.

## 7. R-017 external-reference routing

R-017 classifies six roles, but only two are target-bearing projection families.

### 7.1 Target-bearing projection families

These live in `projections` because they use the R-002 assessment and R-013 formal-kind/role contract:

- `semantic-pivot` + `semantic-constraint` → `semantic_index`;
- `authority-value` + `authority-value-filter` → `authority_index`.

Both require a real external target. `native-only` and `unsupported` are therefore invalid as target-bearing external records.

Exact target-bearing mappings still require derived upstream execution prerequisites. Non-exact authority-value mappings additionally delegate to R-016 exactly like non-exact semantic-pivot mappings.

### 7.2 Non-projection reference kinds

These live in `external_references`:

- `entity-identity`;
- `catalogue-identifier`;
- `provenance-source`;
- `locator`.

Their query roles are respectively constrained to reviewed combinations equivalent to:

- `identity-filter`;
- `identifier-filter`;
- `metadata-filter` or explanation-only where native metadata is queryable;
- `explanation-only`.

They do not enter `semantic_index` or `authority_index`.

### 7.3 Entity identity strength

Do not reuse set-theoretic `broader/narrower` for entity identity.

The first identity vocabulary is equivalent to:

- `same-entity`;
- `probable-same-entity`;
- `related-record`;
- `ambiguous-identity`.

Only a separately reviewed executable identity state may authorize `identity-filter`, and it still consumes the same derived upstream prerequisite.

### 7.4 Identifier scope

Catalogue/inventory identifiers are keyed by issuing authority/namespace plus literal/code. Equal strings from different issuers are not equal identifiers.

### 7.5 Provenance and locators

A provenance/source or locator record requires a real external reference value, but URI presence never creates network access or semantic target status.

## 8. Publication predicates

Publication predicates are projection/reference-specific and never mechanically derived from TFont assessment.

- SKOS mapping predicates require concept-to-concept publication legality;
- `owl:equivalentClass` requires class-to-class semantics;
- `owl:equivalentProperty` requires property-to-property semantics;
- canonical `owl:sameAs` uses the HTTP OWL namespace IRI and is locally valid only for reviewed `entity-identity` + `same-entity`;
- RDFS subclass/subproperty relations require actual hierarchy semantics;
- OntoLex predicates retain their domain/range meaning.

R-017 may locally prove only the same-entity `owl:sameAs` case. Other positive publication relations delegate fail-closed to the R-013 formal-kind-aware validator. Noncanonical lookalike IRIs are never normalized by spelling.

## 9. Approximate execution

R-016 is authoritative.

### 9.1 Modes

Requests expose at least:

```text
semantic_mode = exact | approximate
accept_losses = subset of {undercoverage, overcoverage}
```

Unknown modes/loss tokens fail closed.

### 9.2 Projection policy

- `exact`: executable only after upstream prerequisites pass;
- `broader`: approximate mode only, reviewed eligibility, caller accepts `undercoverage`;
- `narrower`: approximate mode only, reviewed eligibility, caller accepts `overcoverage`;
- `close`: informative-only by default; execution requires separate reviewed loss contract and caller acceptance;
- `related`: never a substitute constraint;
- `ambiguous`: never auto-selected;
- `native-only`: no target reverse execution;
- `unsupported`: refuse.

Direction is native/source → target. Reverse execution through `broader` under-covers; through `narrower` over-covers.

### 9.3 Approximation authorization is content-bound

Approximation eligibility, loss shape, rationale/evidence and review identity participate in projection semantic identity/review binding.

Approximation cannot repair parent incompatibility, unavailable capability, invalid bundle, missing/stale bridge, unresolved lock, or non-executable TF-native dependency.

### 9.4 Conjunctions and comparison

Every required atom must resolve; no atom is silently dropped. Losses compose by union.

Multi-corpus comparison state is at least:

- `exactly-comparable`;
- `approximately-comparable`;
- `heterogeneous-loss`;
- `partial/non-executable`.

Cross-corpus aggregate statistics remain exact-only by default. Approximate aggregation requires explicit boolean opt-in and uniform non-empty loss shape; heterogeneous loss remains non-aggregatable in v1.

## 10. Common semantic IR

The normalized IR is concept-centered rather than artifact-centered.

### 10.1 Required identity layers

Every compiled IR carries fingerprints for:

- parent materialized corpus identity / expected-parent manifest;
- profile catalog and profile contract versions;
- native dependency contract version;
- mapping semantic contract/digest version;
- active ontology bundle identity;
- participating ontology-lock semantic identities;
- bridge review/content identities;
- reference policy/catalog version;
- approximation policy version where relevant.

### 10.2 Required indexes

```text
native_index[
  corpus,
  native-binding-identity
] -> reviewed native record + approved projections + external references

semantic_index[
  profile,
  capability,
  target,
  formal-kind,
  semantic-role
] -> per-corpus approved semantic-pivot projection bindings

authority_index[
  authority-system,
  authority-resource,
  formal-kind,
  semantic-role
] -> per-corpus approved authority-value projection bindings

identity_index[
  authority-system,
  external-entity-id,
  identity-strength
] -> per-corpus reviewed native entity bindings

identifier_index[
  issuer-or-namespace,
  literal-id
] -> per-corpus native identifier bindings

capability_index[
  corpus,
  profile,
  capability
] -> operational state + summary counts + record ids
```

`semantic_index` and `authority_index` must exclude `native-only`, `unsupported`, unresolved ambiguous candidates, provenance/locator links and catalogue IDs.

### 10.3 Resolved atom shape

A target resolution exposes at least:

```yaml
resolved_atom:
  requested_target
  reference_kind
  query_role
  profile_id
  capability_id
  formal_kind
  semantic_role
  corpus_id
  mapping_id
  projection_id
  assessment
  native_execution_binding
  prerequisite_state
  ontology_bundle_id
  parent_identity
  review/evidence identity
  approximation/loss record if non-exact
```

Native binding details remain inspectable so an agent can explain the feature/value/edge/path actually used.

## 11. Resolver contract

Protocol-independent flow:

```text
semantic_capabilities
    ↓ discovery only
semantic_resolve / authority_resolve / identity_resolve
    ↓ authoritative per-corpus resolution
native query plan(s)
    ↓
semantic_search / Context-Fabric execution
    ↓
results + exact resolution provenance
```

### 11.1 Discovery

`semantic_capabilities` returns compact profile/capability summaries by default. It never implies whole-ontology support and never authorizes execution by profile/capability match alone.

### 11.2 Target resolution

Fail-closed order for semantic-pivot and authority-value targets:

1. validate request vocabulary/version and reference/query role;
2. establish parent/profile operational availability;
3. validate active ontology bundle/bridge closure;
4. locate exact requested tuple in the correct index family;
5. validate projection review/content identity;
6. validate TF-native dependency closure/native binding executability;
7. apply R-016 semantic-mode/approximation gates;
8. compile one native plan per corpus;
9. compute comparison/loss state and provenance fingerprint.

Identity and identifier resolution consume the same upstream prerequisite before producing a native plan, but use their own index/strength/scope contracts.

No fuzzy labels, namespace inference, ontology hierarchy inference, stale cached fallback, or similar-feature fallback.

### 11.3 Search execution

Search executes only a resolver-produced executable plan bound to its resolution fingerprint. If a required atom did not resolve, search fails rather than dropping it.

Execution reads materialized TF/Context-Fabric only.

## 12. Seven-corpus POC acceptance

The POC must contain reviewed mappings/negative controls for:

- BHSA;
- CUC;
- one ETCBC Syriac corpus;
- ETCBC ExtraBiblical;
- Pseudepigrapha-TF;
- ORACC-TF;
- TLHdig-TF.

Minimum scenarios:

1. exact OLiA noun across BHSA/Syriac/ExtraBiblical;
2. exact OLiA plural/person conjunction across at least two linguistic corpora;
3. OntoLex lexical-entry mixed-strength resolution across BHSA plus at least two close/native variants;
4. CRMtex TX7 written-text segment across CUC/ORACC/TLH with reviewed strengths preserved;
5. CRM E22 positive physical-object controls only where source identity really denotes a carrier;
6. Pseudepigrapha textual-version/textology positive case with manuscript physical-carrier overprojection rejected;
7. ORACC material/period/place as authority-value examples outside `semantic_index` unless separately reviewed as semantic-pivot targets;
8. TLH witness/fragment/editorial native-only/ambiguous controls;
9. explicit native-only, unsupported, ambiguous, related, unreviewed close, unavailable-bundle, stale-bridge and incompatible-parent failures;
10. ORACC synthetic/empty slots treated as `technicalAnchor`, never semantic sign content or justification for sidecar execution.

The POC must first prove one thin vertical slice:

```text
one exact ontology concept
 -> two or more corpora
 -> distinct native TF bindings
 -> executable native plans
 -> explained result provenance
```

before broader infrastructure generalization.

## 13. Migration from current production contracts

### 13.1 I-001 structural validation

Keep:

- JSON Schema draft 2020-12;
- strict closed shapes;
- duplicate-key/non-JSON/YAML fail-closed loading;
- stable diagnostics/source provenance;
- packaged canonical schema resources.

Versioned amendments required:

- `mapping.schema.json` v1 → v2 native-record/projection/reference contract;
- profile schema evolves from free-form `semantic_domains` to controlled catalog/profile-capability declarations while preserving P-002 dependency records;
- ontology-bundle/bridge/reference schemas or equivalent closed records.

No in-place reinterpretation of mapping v1 files.

### 13.2 I-002 canonicalization and digests

Keep:

- RFC 8785/JCS;
- SHA-256 representation;
- source/evidence digest boundaries;
- ontology-lock semantic identity normalization;
- UTF-16 set ordering/duplicate rejection;
- depth/recursion fail-closed behavior.

`MAPPING_SEMANTIC_ALGORITHM` requires a new version because projection arrays, routing/reference kinds, profile/capability membership, approximation authorization and projection-level review binding change semantic identity.

The old v1 mapping digest must never validate a migrated v2 semantic record.

Profile semantic identity must bind the controlled profile/catalog contract, P-002 dependency content, mapping v2 identities and semantic bundle requirement/identity fields that determine execution. It must **not** claim that a source profile file by itself proves the runtime active bundle is executable; that remains derived cross-artifact/runtime state.

Audit-only review timestamps/display metadata remain outside semantic identity where already established.

### 13.3 I-003 parent identity

Keep unchanged. Parent identity describes materialized corpus components and does not become ontology semantics.

### 13.4 P-002 dependencies

Keep the exact eight TF-native dependency kinds and profile-owned registry. Structural validity remains insufficient for execution; I-004 validates cross-artifact resolution, evidence/content binding and closure.

Never reintroduce pre-A-001 sidecar/native-adapter vocabulary.

### 13.5 Mapping v1 migration

| mapping v1 field | P-003 destination |
|---|---|
| `mapping_id` | native record identity |
| `profile_id` | controlled profile/capability membership |
| `native_selector` | TF-native binding |
| `native_dependencies` | P-002 dependency refs |
| `external_target` | one approved target-bearing projection, if any |
| `candidate_projections` | explicit ambiguous candidate set |
| positive `assessment` | projection-level assessment |
| `ambiguous/native-only/unsupported` | native-record state |
| `publication_relation` | projection/reference-specific publication field |
| `applicability` | native binding applicability |
| `ontology_lock` | projection ontology lock/bundle requirement |
| `evidence` | record/projection/reference evidence as appropriate |
| `review` | content-bound record/projection/reference review authority |
| `mapping_semantic_digest` | new v2 semantic digest |

Automatic migration is permitted only when a v1 row is semantically unambiguous under the new contract. New kind/role/profile/capability/reference classification must be re-reviewed rather than guessed.

## 14. I-004 boundary

I-004 #36 becomes the first production consumer after P-003 acceptance.

It owns deterministic validation of:

- controlled mapping/profile/capability/reference vocabularies;
- duplicate/missing cross-artifact IDs;
- P-002 dependency resolution/component authority;
- ontology lock and target membership against locked evidence;
- kind/role compatibility;
- projection versus ambiguity/no-target consistency;
- ontology bundle/bridge identity and active-closure inputs;
- evidence digest equality;
- review/content digest binding;
- approximation contract validity;
- R-017 routing/query-role/identity-strength legality;
- parent required-component consistency.

It does not execute corpus queries, fetch ontology/network resources, or infer meaning from labels/namespaces.

## 15. Implementation decomposition

Every production ticket follows:

`research → plan → RED contract tests → minimal implementation → focused/full exact-head CI → fresh logically-independent adversarial review`.

### Slice 1 — I-004 semantic validator (#36)

Amend existing #36 against this contract.

Deliver mapping/profile/bundle/reference vNext schemas, cross-artifact semantic validation, versioned mapping digest migration and representative exact/native-only/unsupported/ambiguous/reference fixtures.

### Slice 2 — semantic IR compiler

Create a focused ticket after P-003 acceptance.

Deliver normalized native/projection/reference IR, semantic/authority/identity/identifier indexes and capability summaries. No Context-Fabric execution.

RED must prove target-negative/reference-only records cannot enter the wrong reverse index.

### Slice 3 — exact resolver thin vertical slice

Deliver `semantic_capabilities`, exact `semantic_resolve`, one exact concept resolving across at least two corpora, native-plan explanation and provenance. No approximate execution yet.

### Slice 4 — Context-Fabric execution handoff

Execute only resolver-produced native TF/CF plans, enforce plan fingerprint and return result provenance. No arbitrary source-format backend.

### Slice 5 — approximate resolution

Implement R-016 after the exact vertical slice: reviewed eligibility, caller losses, per-atom loss records, conjunction union, comparison states and exact-only aggregate default.

### Slice 6 — authority/identity/identifier resolution

Implement R-017 dedicated index families/query roles, same-entity identity rules, scoped identifiers and explanation-only provenance/locators while preserving the same upstream gate.

### Slice 7 — seven-pilot POC package

Promote reviewed R-011 evidence into versioned POC fixtures/mappings for all seven corpora and the full positive/negative suite. Unreviewed schema remains unreviewed.

## 16. Required RED cases for later implementation

1. opaque target without formal kind/role;
2. unknown kind/role/profile/capability/reference vocabulary;
3. class/property/SKOS kind-role incompatibility;
4. native-only/unsupported record carrying a target-bearing projection;
5. ambiguous candidate entering approved target index;
6. complementary projections collapsed into ambiguity;
7. URI/local-name inference of kind/semantics;
8. assessment auto-generating SKOS/OWL publication predicate;
9. noncanonical OWL lookalike predicate accepted as canonical;
10. ORACC generic document → CRM E22 overprojection;
11. Pseudepigrapha manuscript → physical carrier overprojection;
12. TLH surface → CRMtex TX7 overprojection;
13. authority-value projection entering `semantic_index`;
14. provenance/locator/catalogue reference entering a target index;
15. same identifier literal across issuers conflated;
16. `same-entity` replaced by broader/narrower identity semantics;
17. profile/capability match alone authorizing execution;
18. active optional profile with unresolved bridge executing;
19. approximation repairing stale/missing bridge or parent incompatibility;
20. `broader` reverse execution without accepted undercoverage;
21. `narrower` reverse execution without accepted overcoverage;
22. `close` executing without reviewed loss contract;
23. `related`/`ambiguous` used as substitute constraint;
24. required conjunction atom silently dropped;
25. heterogeneous-loss approximate aggregate accepted;
26. `technicalAnchor` treated as source-sign semantics;
27. outside-TF sidecar/path/backend smuggled through source dependency/native binding;
28. exact authority/identity/identifier filter executing without derived upstream prerequisite.

## 17. Independent review gate

The final P-003 design head requires a fresh logically-independent skeptical review against R-001..R-017 plus the R-017 amendment, A-001, merged P-002, current I-001/I-002/I-003 behavior, authoritative ontology semantics already evidenced by the research tickets and all seven pilot boundaries.

Review must explicitly try to falsify:

1. any recreation of a generic outside-TF runtime carrier;
2. projection complementarity versus ambiguity;
3. independence of target kind, semantic role, routing/reference kind, assessment and publication relation;
4. leakage between semantic, authority, identity, identifier and provenance index families;
5. approximation bypassing bundle/parent/review gates;
6. discovery state becoming concept execution authority;
7. mapping-v1 migration silently preserving an invalid semantic digest;
8. any required POC negative control becoming executable.

Merge P-003 only when the exact design head has no blocker. Production implementation begins only afterward.
