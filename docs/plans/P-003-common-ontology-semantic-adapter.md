# P-003 plan: common ontology semantic adapter architecture

**Issue:** #44  
**Type:** design-only architecture amendment  
**Baseline:** `main` after P-002 (`a238522c3048ee077a09e090a4b067b72cec901c`)  
**Inputs:** R-001..R-017, A-001, merged I-001/I-002/I-003, merged P-002

## 1. Decision

TFont's primary runtime contract is a **reviewed semantic compatibility layer over already-materialized Text-Fabric / Context-Fabric corpora**.

The architecture is:

```text
source representations
        ↓ corpus-specific materializer/converter
materialized TF / Context-Fabric corpus
        ↓
TFont native semantic records
        ↓
0..N reviewed typed semantic projections
        ↓
content-addressed active ontology bundle + reviewed bridge closure
        ↓
common-semantic / authority / identity resolution
        ↓
native Context-Fabric query plan
        ↓
results + provenance + semantic-loss explanation
```

TFont does not own generic JSON/XML/CSV/TEI/PDF/database/API ingestion, arbitrary source-record addressing, network dereferencing, adapter authentication/caching, or a generic sidecar/native-adapter runtime.

The central modeling change is:

> A mapping is a reviewed **native semantic record** with one native binding and **zero or more complementary typed projections**. A projection is the smallest reviewed unit that can participate in common-semantic reverse resolution.

This replaces the current one-record/one-`external_target` model.

`native-only` and `unsupported` remain legitimate first-class reviewed native records with zero semantic projections. Ambiguity is represented explicitly and never converted into simultaneous complementary projections.

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
  projections: [0..N semantic projections]
  references: [0..N R-017 external-reference records]
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

### 3.2 Native record state

The eight accepted R-002 assessment meanings remain semantically observable, but P-003 separates record state from projection strength:

- positive target-bearing relations are expressed on projections as `exact | close | broader | narrower | related`;
- `ambiguous` means target choice is unresolved and no common-semantic execution is authorized;
- `native-only` means reviewed native semantics exist but there is no accepted common target;
- `unsupported` is reviewed negative knowledge.

A record must not simultaneously claim `native-only`/`unsupported` and carry a common semantic projection.

Ambiguous alternatives are kept in a distinct candidate set. They are not ordinary approved projections and never enter reverse execution indexes.

## 4. Semantic projection contract

Each approved projection is independently typed and reviewed.

Conceptually:

```yaml
projection:
  projection_id: stable record-local or global id
  target: locked IRI/resource id
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

`authority-reference` is retained for projections whose target is genuinely semantic/authority-valued, but R-017 reference kind and query role determine whether it enters the common semantic index, authority index, or neither.

Formal kind does not determine semantic role. Role does not determine publication relation. URI syntax does not determine either.

### 4.3 Kind/role validation

At minimum the production validator must enforce:

- `class` → entity/category/value roles, never relation/attribute/particular identity;
- `property` → relation/attribute/annotation-category, never entity-type or particular identity;
- `skos-concept` → annotation value, lexical concept, authority reference; never relation/attribute;
- `named-resource` → particular lexical identities, authority reference, proposition/inference identity; never ontology class/property semantics.

Exceptional RDF multi-typing is represented by separate reviewed projections when execution/publication semantics differ.

### 4.4 Complementarity versus ambiguity

Multiple projections are **complementary** when all are simultaneously true of the same native semantics and serve different compatible roles or ontology dimensions.

Examples:

- physical-object class projection + reviewed material authority-value reference;
- lexical entry entity-type projection + a separate particular external lexical identity;
- written-text segment class + a relation projection connecting it to a carrier.

Mutually exclusive candidate targets remain `ambiguous` candidates and are not approved projections.

The validator must reject both failure modes:

- collapsing compatible complementary projections into ambiguity;
- representing unresolved alternatives as simultaneous approved projections.

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

Initial capability IDs are the accepted R-014 controlled identifiers, including:

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

Optional profile capabilities require their own versioned catalog entries and evidence; they are not inferred from free-form labels.

Profile/capability state is discovery information only. Common-semantic execution is authorized only by an exact requested concept/projection tuple.

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
- scoped terms belong to the endpoint lock `terms_used` sets;
- bridge content digest matches reviewed content;
- review state is accepted;
- compatibility is explicit;
- runtime strength is exact for the v1 active bundle gate.

A CRMtex F28 bridge does not imply ontology-wide equivalence. Optional profiles that are inactive do not inject bridge requirements into the active bundle.

### 6.3 Version-skew consequences

The production architecture must preserve accepted bridge cases, including:

- CRMtex 2.0's historical FRBRoo/LRMoo continuity needs;
- CRMarchaeo 2.1.1's CRM 7.1.2 / CRMsci 2.0 dependencies versus the current CRM 7.1.3 / CRMsci 3.2 stack.

An inactive optional archaeology profile is not a bridge failure. Activating archaeology with unresolved required bridges makes that capability unavailable/non-executable.

## 7. External references are not one target space

R-017 introduces a separate typed reference layer. It must not be flattened into the semantic projection array.

### 7.1 Reference kinds

Closed first vocabulary equivalent to:

- `semantic-pivot`;
- `authority-value`;
- `entity-identity`;
- `catalogue-identifier`;
- `provenance-source`;
- `locator`.

### 7.2 Query roles

Closed first query-role vocabulary equivalent to:

- `semantic-constraint`;
- `authority-value-filter`;
- `identity-filter`;
- `identifier-filter`;
- `metadata-filter`;
- `explanation-only`.

Only `semantic-pivot` + `semantic-constraint` participates in the ordinary common semantic reverse index.

Authority values have their own reverse index; entity identities have another; identifiers are issuer/namespace scoped. Provenance and locator references do not become semantic constraints merely because they are URIs.

### 7.3 Entity identity strength

Do not reuse set-theoretic `broader/narrower` for entity identity.

The first identity assertion vocabulary should be equivalent to:

- `same-entity`;
- `probable-same-entity`;
- `related-record`;
- `ambiguous-identity`.

Only an explicitly reviewed executable identity state may authorize `identity-filter`.

### 7.4 Publication predicates

Publication predicates are projection/reference-specific and never mechanically derived from TFont assessment.

In particular:

- SKOS mapping predicates require concept-to-concept publication legality;
- `owl:equivalentClass` requires class-to-class semantics;
- `owl:equivalentProperty` requires property-to-property semantics;
- canonical OWL `owl:sameAs` is the HTTP namespace IRI and is permitted only for genuine resource identity;
- RDFS subclass/subproperty relations require actual hierarchy semantics;
- OntoLex predicates retain their domain/range meaning.

Noncanonical lookalike predicates fail closed or require explicit external-policy delegation; they are never normalized by spelling.

## 8. Approximate execution

R-016 is authoritative.

### 8.1 Modes

Requests expose at least:

```text
semantic_mode = exact | approximate
accept_losses = subset of {undercoverage, overcoverage}
```

Unknown modes/loss tokens fail closed.

### 8.2 Projection policy

- `exact`: executable in exact or approximate mode only after upstream prerequisites pass;
- `broader`: approximate mode only, reviewed approximation eligibility, caller accepts `undercoverage`;
- `narrower`: approximate mode only, reviewed approximation eligibility, caller accepts `overcoverage`;
- `close`: informative-only by default; execution requires separate reviewed loss contract plus caller acceptance;
- `related`: never a substitute constraint;
- `ambiguous`: never auto-selected;
- `native-only`: no common-target reverse execution;
- `unsupported`: refuse.

The direction is fixed as native/source → target, therefore reverse execution through `broader` under-covers and through `narrower` over-covers.

### 8.3 Approximation authorization is content-bound

A mutable boolean is insufficient. Approximation eligibility, loss shape, rationale/evidence and review identity must participate in projection semantic identity/review binding.

Approximation cannot repair:

- parent incompatibility;
- unavailable profile/capability;
- invalid active bundle;
- missing/stale/unreviewed bridge;
- unresolved ontology lock;
- non-executable TF-native dependency.

### 8.4 Conjunctions and comparison

Every required atom must resolve; no atom is silently dropped.

Losses compose by union. Multi-corpus comparison state is at least:

- `exactly-comparable`;
- `approximately-comparable`;
- `heterogeneous-loss`;
- `partial/non-executable`.

Cross-corpus aggregate statistics remain exact-only by default. Approximate aggregation requires explicit boolean opt-in and uniform non-empty loss shape; heterogeneous loss remains non-aggregatable in v1.

## 9. Common semantic IR

The normalized IR is concept-centered rather than artifact-centered.

### 9.1 Required identity layers

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

### 9.2 Required indexes

Authoritative indexes:

```text
native_index[
  corpus,
  native-binding-identity
] -> reviewed native record + approved projections + references

semantic_index[
  profile,
  capability,
  target,
  formal-kind,
  semantic-role
] -> per-corpus approved projection bindings

authority_index[
  authority-system,
  authority-resource,
  query-role
] -> per-corpus reviewed authority-value bindings

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

`semantic_index` must never contain `native-only`, `unsupported`, unresolved ambiguous candidates, locator URLs, provenance links, or catalogue IDs merely because they have URI-like values.

### 9.3 IR record shape

A resolved semantic atom must expose at least:

```yaml
resolved_atom:
  requested_target
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

Native binding details remain inspectable so an agent can explain the actual feature/value/edge/path used.

## 10. Resolver contract

Protocol-independent flow:

```text
semantic_capabilities
    ↓ discovery only
semantic_resolve(request)
    ↓ authoritative per-corpus resolution
native query plan(s)
    ↓
semantic_search / Context-Fabric execution
    ↓
results + exact semantic-resolution provenance
```

### 10.1 `semantic_capabilities`

Returns compact profile/capability summaries by default. It never implies whole-ontology support and never authorizes execution by profile/capability match alone.

### 10.2 `semantic_resolve`

Input includes requested corpus set and semantic atoms, each with exact target identity plus profile/capability/kind/role as required by the contract.

Resolution order is fail-closed:

1. validate request vocabulary/version;
2. establish parent/profile operational availability;
3. validate active ontology bundle/bridge closure;
4. locate exact requested semantic-index tuple;
5. validate projection review/content identity;
6. validate TF-native dependency closure/native binding executability;
7. apply R-016 semantic-mode/approximation gates;
8. compile one native plan per corpus;
9. compute comparison/loss state and provenance fingerprint.

No fuzzy labels, namespace inference, ontology hierarchy inference, stale cached fallback, or similar-feature fallback.

### 10.3 `semantic_search`

Search executes only a resolver-produced executable plan bound to its resolution fingerprint. If a requested required atom did not resolve, search fails rather than dropping it.

Execution reads materialized TF/Context-Fabric only.

## 11. Seven-corpus POC acceptance

The POC must contain reviewed mappings/negative controls for all seven pilots:

- BHSA;
- CUC;
- one ETCBC Syriac corpus;
- ETCBC ExtraBiblical;
- Pseudepigrapha-TF;
- ORACC-TF;
- TLHdig-TF.

Minimum cross-corpus scenarios:

1. exact OLiA noun across BHSA/Syriac/ExtraBiblical;
2. exact OLiA plural/person conjunction across at least two linguistic corpora;
3. OntoLex lexical-entry mixed-strength resolution across BHSA plus at least two close/native variants;
4. CRMtex TX7 written-text segment across CUC/ORACC/TLH with current reviewed strength preserved;
5. CRM E22 positive physical-object controls only where source identity really denotes a carrier;
6. Pseudepigrapha textual-version/textology positive case with manuscript physical-carrier overprojection rejected;
7. ORACC material/period/place authority-value examples kept outside the ordinary semantic-pivot index unless a separate semantic projection is reviewed;
8. TLH witness/fragment/editorial native-only/ambiguous controls;
9. explicit `native-only`, `unsupported`, `ambiguous`, `related`, unreviewed `close`, unavailable-bundle, stale-bridge and incompatible-parent failures;
10. ORACC synthetic/empty slots treated as `technicalAnchor`, never semantic sign content or justification for sidecar execution.

The POC must demonstrate at least one thin vertical slice:

```text
one exact ontology concept
 -> two or more corpora
 -> distinct native TF bindings
 -> executable native plans
 -> explained result provenance
```

before broader infrastructure generalization.

## 12. Migration from current production contracts

### 12.1 I-001 structural validation

**Keep:**

- JSON Schema draft 2020-12 structural validation;
- strict closed object shapes;
- duplicate-key/non-JSON/YAML fail-closed loading;
- stable diagnostics/source provenance;
- packaged canonical schema resources.

**Versioned amendments required:**

- `mapping.schema.json` v1 → v2 typed native-record/projection/reference contract;
- profile schema evolves from free-form `semantic_domains` to controlled catalog/profile-capability declarations while preserving P-002 v2 dependency records;
- new ontology-bundle/bridge/reference schemas or equivalent closed records.

No in-place reinterpretation of mapping v1 files.

### 12.2 I-002 canonicalization and digests

**Keep:**

- RFC 8785/JCS canonical JSON;
- SHA-256 representation;
- source/evidence digest boundaries;
- ontology-lock semantic identity normalization;
- UTF-16 set ordering and duplicate rejection;
- recursion/depth fail-closed behavior.

**Versioned amendment required:**

`MAPPING_SEMANTIC_ALGORITHM` must receive a new algorithm/version because projection arrays, reference records, profile/capability membership, approximation authorization, and projection-level review binding change semantic identity.

The old v1 mapping digest must never validate a migrated v2 semantic record.

Profile semantic identity must include the controlled profile/catalog contract, P-002 dependency content, mapping v2 identities, active ontology-bundle identity and executable review readiness. Audit-only review timestamps/display metadata remain outside semantic identity where already established.

### 12.3 I-003 parent identity

Keep unchanged. Parent identity describes materialized corpus components and does not become ontology semantics.

### 12.4 P-002 source dependency contract

Keep its exact eight TF-native dependency kinds and profile-owned registry. Structural validity remains insufficient for execution; I-004 validates cross-artifact resolution, evidence/content binding and closure.

Do not reintroduce any pre-A-001 sidecar/native-adapter vocabulary.

### 12.5 Current mapping v1 field migration

| mapping v1 field | P-003 destination |
|---|---|
| `mapping_id` | native record identity |
| `profile_id` | controlled profile membership; may expand to multiple reviewed profiles/capabilities |
| `native_selector` | TF-native binding |
| `native_dependencies` | unchanged P-002 dependency refs |
| `external_target` | one approved projection target, if any |
| `candidate_projections` | explicit ambiguous candidate set, not approved projection array |
| `assessment` positive | projection-level assessment |
| `assessment` ambiguous/native-only/unsupported | native-record state |
| `publication_relation` | projection/reference-specific publication field |
| `applicability` | native binding applicability |
| `ontology_lock` | projection ontology lock/bundle requirement |
| `evidence` | record/projection/reference evidence as semantically appropriate |
| `review` | content-bound record/projection review authority |
| `mapping_semantic_digest` | new v2 semantic digest |

Automatic migration is permitted only when the v1 row is semantically unambiguous under the new contract. Anything requiring new kind/role/profile/capability/reference classification must be re-reviewed rather than guessed.

## 13. Cross-artifact semantic validation boundary

I-004 #36 becomes the first production consumer after P-003 acceptance.

It owns deterministic validation of:

- controlled mapping/profile/capability/reference vocabularies;
- duplicate/missing cross-artifact IDs;
- P-002 dependency resolution/component authority;
- ontology lock and target membership against locked evidence;
- kind/role compatibility;
- projection vs ambiguity/no-target state consistency;
- ontology bundle/bridge identity and active closure inputs;
- evidence digest equality;
- review/content digest binding;
- approximation contract validity;
- R-017 reference-kind/query-role/identity-strength legality;
- parent required-component consistency.

It does not execute corpus queries, fetch ontology/network resources, or infer meaning from labels/namespaces.

## 14. Implementation decomposition

Every production ticket follows:

`research → plan → RED contract tests → minimal implementation → focused/full exact-head CI → fresh logically-independent adversarial review`.

### Slice 1 — I-004 semantic validator (#36)

First unblock and amend existing #36 against this P-003 contract.

Deliver:

- mapping/profile/bundle/reference vNext schemas;
- cross-artifact semantic validator;
- versioned mapping semantic digest migration;
- representative exact/native-only/unsupported/ambiguous/reference fixtures.

No resolver yet.

### Slice 2 — semantic IR compiler

Create a focused implementation ticket after P-003 acceptance.

Deliver:

- normalized native/projection/reference IR;
- authoritative semantic/authority/identity/identifier indexes;
- capability summaries;
- no Context-Fabric execution.

RED must prove no-target/reference-only records are excluded from the common semantic reverse index.

### Slice 3 — exact resolver thin vertical slice

Deliver:

- `semantic_capabilities` compact discovery;
- `semantic_resolve` exact-mode planning;
- one exact concept resolving across at least two corpora;
- native plan explanation/provenance;
- no approximate execution yet.

### Slice 4 — Context-Fabric execution handoff

Deliver:

- execution of resolver-produced native TF/CF plans;
- plan fingerprint enforcement;
- result provenance;
- no arbitrary source-format backend.

### Slice 5 — approximate resolution policy

Implement R-016 only after exact vertical slice is green.

Deliver:

- reviewed approximation authorization;
- caller `accept_losses`;
- per-atom loss records;
- conjunction loss union;
- multi-corpus comparison states;
- exact-only aggregate default.

### Slice 6 — authority/identity resolution

Implement R-017 dedicated indexes and query roles.

Deliver:

- authority-value filters;
- entity identity filters with separate identity-strength vocabulary;
- scoped identifier filters;
- provenance/locator explanation-only behavior;
- strict separation from common semantic reverse resolution.

### Slice 7 — seven-pilot POC package

Promote reviewed R-011 evidence into versioned POC fixtures/mappings for all seven corpora and the full positive/negative query suite.

This ticket must not normalize every native concept. Unreviewed schema remains unreviewed.

## 15. Design acceptance tests

P-003 is design-only, but every later implementation must include RED cases covering at least:

1. opaque target without formal kind/role;
2. unknown kind/role/profile/capability/reference vocabulary;
3. class/property/SKOS kind-role incompatibility;
4. native-only or unsupported record carrying a common target;
5. ambiguous candidates entering approved semantic index;
6. complementary projections collapsed into ambiguity;
7. URI/local-name inference of kind or semantics;
8. exact assessment auto-generating SKOS/OWL publication predicate;
9. noncanonical OWL lookalike predicate accepted as canonical;
10. ORACC generic document overprojected to CRM E22;
11. Pseudepigrapha manuscript overprojected to physical carrier;
12. TLH surface overprojected to CRMtex TX7;
13. provenance/locator/catalogue URI entering semantic-pivot index;
14. same identifier literal under different issuers conflated;
15. `same-entity` replaced by set-theoretic broader/narrower identity;
16. profile/capability match alone authorizing execution;
17. active optional profile with unresolved bridge executing;
18. approximation repairing stale/missing bridge or parent incompatibility;
19. `broader` reverse execution without accepted undercoverage;
20. `narrower` reverse execution without accepted overcoverage;
21. `close` executing without reviewed loss contract;
22. `related` or `ambiguous` used as substitute constraint;
23. required conjunction atom silently dropped;
24. heterogeneous-loss approximate aggregate accepted;
25. structural `technicalAnchor` treated as source-sign semantics;
26. outside-TF sidecar/path/backend smuggled through source dependency or native binding.

## 16. Independent review gate

The final P-003 design head must receive a fresh logically-independent skeptical review against:

- R-001..R-017 and their post-review amendments;
- A-001 TF-native boundary;
- merged P-002 dependency contract;
- current I-001/I-002/I-003 production behavior;
- authoritative OLiA, SKOS, OntoLex, CIDOC CRM-family and OWL namespace semantics already evidenced by the research tickets;
- all seven pilot corpus boundaries.

Review must explicitly try to falsify:

1. whether any field recreates a generic outside-TF runtime carrier;
2. whether projection complementarity/ambiguity is mechanically distinguishable;
3. whether target kind, semantic role, assessment and publication relation remain independent;
4. whether authority/identity/provenance references can leak into the common semantic index;
5. whether approximation can bypass bundle/parent/review gates;
6. whether profile/capability discovery can be mistaken for concept execution authority;
7. whether migration silently reinterprets mapping v1 semantic identity;
8. whether every required POC negative control remains fail-closed.

Merge P-003 only when the exact design head has no blocker. Production implementation begins only afterward.
