# R-013: common semantic target kinds and semantic roles

**Status:** research complete; pending fresh logically-independent adversarial review  
**Issue:** #47  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-002/R-003/R-005, merged R-006/R-007/R-008/R-009/R-010/R-012, roadmap guardrail #45

## Decision

TFont needs **two independent controlled dimensions** for every common semantic projection:

1. **formal target kind** — what kind of ontology/RDF resource the target actually is;
2. **semantic role** — what the target means in the TFont mapping contract and therefore how it may participate in query planning.

One opaque `external_target` URI cannot encode either dimension reliably. The same formal kind can serve different semantic roles, and the same semantic role can be represented by different formal kinds in different standards.

The minimum first-profile formal-kind vocabulary is:

- `class`
- `object-property`
- `datatype-property`
- `skos-concept`
- `named-resource`

The minimum first-profile semantic-role vocabulary is:

- `entity-type`
- `annotation-category`
- `annotation-value`
- `relation`
- `attribute`
- `lexical-entry-identity`
- `lexical-form-identity`
- `lexical-sense-identity`
- `lexical-concept-identity`
- `authority-reference`
- `claim-proposition`
- `inference-activity`

These are **research contract names**, not frozen production enum spellings. P-003 may rename them, but it must preserve the distinctions. R-014 owns final semantic-profile/capability identifiers; R-017 owns the final authority-reference contract.

The governing invariant is:

> **Formal RDF shape does not determine semantic role, and semantic role does not determine publication relation. Query execution is authorized by an explicit reviewed `(profile, target, formal-kind, semantic-role, native binding)` tuple, not by URI syntax, local name, or ontology inference.**

## 1. Why one URI field is insufficient

Examples from the accepted corpus family show at least four different things currently representable only as an undifferentiated URI:

```text
olia:Noun
  formal kind: OWL class
  semantic role: annotation-value / entity-type-like category

crmtex:TXP4_has_segment
  formal kind: object property
  semantic role: relation

an external ORACC dictionary sense URI
  formal kind: named resource
  semantic role: lexical-sense-identity

a PeriodO period URI
  formal kind: SKOS concept
  semantic role: authority-reference
```

Treating all four as `external_target` creates concrete failures:

- a resolver cannot know whether to compile a node/value predicate or an edge traversal;
- publication code cannot know whether SKOS mapping properties are legal;
- an agent cannot distinguish an ontology class from a particular external entity identity;
- a lexical-sense URI may be mistaken for a class whose instances should be selected;
- an AAT/PeriodO authority URI may be mistaken for a common semantic-pivot target;
- complementary projections and ambiguity candidates cannot be validated by type/role compatibility.

## 2. Standards evidence

### 2.1 OLiA

OLiA is an OWL2/DL architecture with annotation models, a reference model, and linking models. The maintained documentation states that the OLiA Reference Model exposes grammatical feature values such as `olia:Noun` and `olia:Singular` as **classes**, while the System Model exposes annotation-structure properties.

Primary sources:

- <https://acoli-repo.github.io/olia/>
- <https://acoli-repo.github.io/olia/owl/>

Consequences for TFont:

- `olia:Noun`, `olia:Plural`, etc. are `class` targets;
- their semantic role in a corpus mapping is usually `annotation-value` (or `entity-type` where a native node type itself denotes the linguistic category);
- OLiA linking-model `subClassOf` architecture is prior art for semantic mediation, not permission for TFont to infer executable mappings at runtime.

### 2.2 SKOS

SKOS mapping properties (`exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, `relatedMatch`) have domain/range `skos:Concept` and are intended for concept-to-concept mapping across concept schemes.

Primary source:

- <https://www.w3.org/TR/skos-reference/>

Consequences:

- a SKOS target needs formal kind `skos-concept` when its concept semantics matter;
- TFont mapping assessments are **not automatically serialized** as SKOS mapping predicates;
- `skos:exactMatch` must not be emitted between arbitrary OWL classes, properties, lexical senses, or authority resources merely because TFont assessment is `exact`.

### 2.3 OntoLex-Lemon

OntoLex core distinguishes classes such as `LexicalEntry`, `Form`, `LexicalSense`, and `LexicalConcept`; it also distinguishes particular instances of those classes. `LexicalConcept` is modeled compatibly with SKOS concepts. `ontolex:reference` relates a particular lexical sense to a referenced ontology resource.

Primary source:

- <https://www.w3.org/community/ontolex/wiki/Final_Model_Specification>

This creates the strongest proof that formal kind alone is insufficient:

```text
ontolex:LexicalSense
    = class
    role when mapping a native node type = entity-type

external-dictionary:sense-123
    = named resource
    role when mapping a native source sense = lexical-sense-identity

external-concept:foo
    = SKOS concept / named resource
    role = lexical-concept-identity
```

A native gloss literal does not become any of these identities merely because it resembles a dictionary meaning.

### 2.4 CIDOC CRM family

CIDOC CRM 7.1.3 explicitly distinguishes ontology **classes**, **properties**, and instances of `E55 Type`. `P2 has type` links a CRM entity instance to an `E55 Type` instance; an external controlled term may therefore act as a classification resource without becoming an OWL class.

Primary source:

- <https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html>

CRMtex, LRMoo, CRMinf and optional CRM extensions likewise expose classes/properties plus domain instances.

Consequences:

- `crm:E22_Human-Made_Object` is `class` + `entity-type`;
- `crm:P46_is_composed_of` is `object-property` + `relation`;
- a particular `E55 Type` authority term is `named-resource` (or `skos-concept` if the authority is formally SKOS) + `annotation-value`/`authority-reference`, not `class` by default;
- a particular CRMinf proposition is a `named-resource` + `claim-proposition`, while `crminf:I4_Proposition_Set` is `class` + `entity-type`.

## 3. Formal target kinds

### 3.1 `class`

Use for ontology classes whose instances correspond to native entities/categories.

Examples:

- `olia:Noun`
- `ontolex:LexicalEntry`
- `crm:E22_Human-Made_Object`
- `crmtex:TX7_Written_Text_Segment`
- `lrmoo:F2_Expression`
- `crminf:I4_Proposition_Set`

Execution implication: normally compiles through an explicitly reviewed native **type/value membership predicate**, never through generic RDF class reasoning at runtime.

### 3.2 `object-property`

Use for semantic relations whose object is another entity/resource.

Examples include CIDOC/CRMtex/LRMoo relations and any reviewed OLiA/System relation used as a semantic edge.

Execution implication: normally requires a native edge/path relation, relation-valued feature, or explicitly defined derived path. The direction is part of the native binding and cannot be inferred from the English label.

### 3.3 `datatype-property`

Use for semantic attributes whose range is a literal/datatype value when an accepted ontology genuinely defines such a property and the mapping needs that property as the semantic pivot.

Execution implication: normally compiles to feature presence/value comparison rather than node traversal.

The current corpus pilots require fewer datatype-property targets than class/object-property targets, but omitting the kind would force literal-valued ontology properties into the same runtime shape as graph relations.

### 3.4 `skos-concept`

Use when the target is a concept in a SKOS concept scheme and concept-scheme/mapping semantics matter.

Examples:

- `ontolex:LexicalConcept` instances where published as SKOS concepts;
- PeriodO period definitions;
- reviewed semantic-domain/category schemes.

A SKOS concept is also an RDF resource, but `skos-concept` is retained as a separate formal kind because publication-relation legality and concept-scheme behavior differ materially from a generic individual/resource.

### 3.5 `named-resource`

Fallback for a particular identified RDF/resource individual that is neither being used as a class/property nor requiring SKOS-concept semantics.

Examples:

- a particular external lexical entry;
- a particular lexical form/sense resource;
- a museum/catalogue authority entity;
- a particular CRMinf proposition/belief/inference instance;
- a CRM `E55 Type` instance from a non-SKOS authority.

`named-resource` must not become a generic escape hatch for unknown target type. If the formal type cannot be determined from the locked source artifact, the mapping is invalid/unresolved rather than silently typed as `named-resource`.

## 4. Kinds deliberately excluded from the first closed vocabulary

### 4.1 Literals

A literal is a native/source value or query operand, not a semantic target identity. TFont must not store `"stone"`, `"noun"`, or an English gloss as an ontology target in lieu of a reviewed concept/resource.

### 4.2 Annotation properties

No accepted R-006–R-011 execution case requires an OWL annotation property as the common semantic query pivot. Labels, comments, provenance notes and documentation metadata belong to publication/evidence metadata. Add this formal kind only if a future profile demonstrates an executable semantic need.

### 4.3 Blank nodes

Released mappings require stable reviewable target identity. Anonymous blank-node targets are incompatible with deterministic locking, review provenance, documentation and reverse indexing unless canonicalized as part of an independently governed ontology artifact. They are not first-profile targets.

### 4.4 RDF-star/property-of-property constructs

These may be useful publication mechanisms, and CIDOC CRM has conceptual `.1` properties-of-properties, but no current pilot requires a distinct canonical target formal kind for them. If R-011 later demonstrates such a need, P-003 can version the vocabulary rather than pre-generalizing now.

## 5. Semantic roles

Formal kind answers “what RDF thing is this?” Semantic role answers “what does this projection mean to TFont?”

### 5.1 `entity-type`

The target classifies the kind of entity represented by the native selector/node type.

Examples:

- CUC `otype=tablet` -> CRM physical-object class;
- CUC/TLH/ORACC line node type -> CRMtex written-text-segment class, where physical writing semantics are reviewed;
- Pseudepigrapha textual version -> LRMoo Expression, where source semantics warrant it.

### 5.2 `annotation-category`

The target denotes an annotation dimension/property family, not one value.

Example conceptual use:

```text
native feature `gn`
  -> shared category “grammatical gender”
```

This role is separate from the particular value `Masculine`.

### 5.3 `annotation-value`

The target denotes one categorical annotation value.

Examples:

- BHSA `sp=subs` -> OLiA Noun;
- BHSA `nu=pl` -> OLiA Plural;
- Syriac `ps=first` -> OLiA FirstPerson.

### 5.4 `relation`

The target denotes a binary/entity relation.

Examples:

- written text -> segment;
- expression -> derivative expression;
- native structural/semantic edge when a reviewed standard relation exists.

A relation binding needs direction, source applicability, target applicability, and any path semantics explicitly recorded.

### 5.5 `attribute`

The target denotes a literal-valued semantic attribute/property.

This is distinct from `annotation-category`: some attributes are open-valued strings/numbers/dates rather than closed linguistic/controlled categories.

### 5.6 `lexical-entry-identity`

The target denotes one particular lexical entry identity. A class such as `ontolex:LexicalEntry` is **not** this role; it is normally `entity-type`.

### 5.7 `lexical-form-identity`

The target denotes one particular OntoLex/external lexical-form identity.

### 5.8 `lexical-sense-identity`

The target denotes one particular source/external lexical sense identity.

A gloss/guide-word/definition literal cannot satisfy this role.

### 5.9 `lexical-concept-identity`

The target denotes a shared lexical-semantic concept intended as a cross-resource semantic pivot. This will often pair with formal kind `skos-concept`.

### 5.10 `authority-reference`

The target is an external authority/identity/value resource usable for filtering, identity, documentation or linked-data navigation, but is not automatically part of the common semantic pivot.

Examples:

- PeriodO period definition;
- Getty AAT material/object term;
- museum/catalogue authority URI;
- external place authority.

R-017 owns the exact execution/publication policy for this role.

### 5.11 `claim-proposition`

The target represents a particular proposition/claim identity or the native assertion is mapped to a proposition-bearing semantic object.

This role is needed to keep an assertion about an object separate from the object/classification itself.

### 5.12 `inference-activity`

The target represents an argumentation/inference/assessment activity, not the proposition that resulted from it.

This preserves the R-009/R-010 distinction:

```text
source fact / proposition
    != scholar's belief about it
    != inference/assessment activity producing/adopting that belief
```

## 6. Kind/role compatibility matrix

`allowed` means structurally possible, not semantically approved for every mapping.

| formal kind | roles normally allowed | roles normally invalid |
|---|---|---|
| `class` | entity-type, annotation-category, annotation-value | relation, attribute, particular lexical identity, authority-reference |
| `object-property` | relation | entity-type, annotation-value, lexical identity, claim identity |
| `datatype-property` | attribute, sometimes annotation-category | entity-type, relation-to-entity, lexical identity |
| `skos-concept` | annotation-value, lexical-concept-identity, authority-reference | relation, attribute property |
| `named-resource` | lexical-entry/form/sense/concept identity, authority-reference, claim-proposition, inference-activity, controlled value | ontology relation/property, ontology class-as-type |

Exceptional combinations require explicit evidence, not free-form override strings. For example, an authority may type a resource simultaneously as `skos:Concept` and CRM `E55 Type`; the mapping still records the TFont formal kind/role chosen for this projection and may add a separate complementary projection if another role is independently needed.

## 7. Publication-relation legality

Publication relation is a third concern and must remain projection-specific.

### 7.1 SKOS mapping predicates

Allowed only for concept-to-concept mapping where the source publication entity and target are actually SKOS concepts and the chosen predicate is semantically justified.

Never derive automatically:

```text
TFont assessment exact    -> skos:exactMatch
TFont assessment close    -> skos:closeMatch
TFont assessment broader  -> skos:broadMatch
...
```

because TFont assessment applies across heterogeneous formal kinds and native mapping semantics.

### 7.2 OWL class/property equivalence

`owl:equivalentClass` is legal only class-to-class and is exceptionally strong. `owl:equivalentProperty` is legal only property-to-property. Neither follows from TFont `exact` by default.

### 7.3 `owl:sameAs`

Only for genuine identity of resources/individuals. Same label, same gloss, same catalogue number, same period name, or same translation does not establish `owl:sameAs`.

### 7.4 RDFS subclass/subproperty

Use only when the ontology/publication semantics genuinely assert class/property hierarchy. TFont broader/narrower mapping assessment is not automatically a subclass/subproperty statement.

### 7.5 OntoLex relations

`ontolex:sense`, `reference`, `canonicalForm`, etc. have specific domains/ranges and are not generic TFont publication relations. They can appear in an OntoLex publication profile only when the native/external resource structure satisfies that model.

## 8. Execution implications

The tuple `(formal-kind, semantic-role)` determines the **required native binding shape**, but never creates the binding itself.

| target | role | minimum native execution shape |
|---|---|---|
| class | entity-type | node/entity type or reviewed membership selector |
| class | annotation-value | feature/value/category selector |
| class | annotation-category | feature/category applicability binding |
| object-property | relation | directed native edge/path plus source/target applicability |
| datatype-property | attribute | feature/literal value or presence predicate |
| skos-concept | lexical-concept-identity | reviewed native sense/entry/concept -> shared concept binding |
| skos-concept | authority-reference | reviewed authority-valued native field/key; common-pivot execution depends on R-017 |
| named-resource | lexical-entry/form/sense identity | stable native identity construction/key plus occurrence/path binding |
| named-resource | claim-proposition | explicit native claim/assertion identity; no fabrication from ordinary fact |
| named-resource | inference-activity | explicit attributed process/activity identity |

The resolver must reject a mapping if target kind/role requires an execution shape that the native selector does not provide.

## 9. Corpus tests

These are contract examples for R-011/P-003, not released production mappings.

### 9.1 BHSA

```text
native: word.sp = subs
target: olia:Noun
formal kind: class
semantic role: annotation-value
execution: F.sp.v(n) == "subs"
```

This is structurally valid. Publishing it via `skos:exactMatch` would be invalid merely from the TFont mapping assessment because `olia:Noun` is an OWL class, not a SKOS concept mapping target.

A BHSA `lex` node projected to `ontolex:LexicalEntry` uses:

```text
formal kind: class
role: entity-type
```

A particular BHSA lexeme mapped to a particular external dictionary entry would instead be:

```text
formal kind: named-resource
role: lexical-entry-identity
```

### 9.2 ETCBC Syriac

A repeated `lex` feature used as a reviewed corpus-scoped lexical key may bind a particular lexical identity, but the key string itself is not a named RDF resource. TFont must represent the **native identity construction** separately from the external resource target.

Unsafe case:

```text
native literal lex="..."
external target ontolex:LexicalEntry
role lexical-entry-identity
```

This is invalid because the target is the class, not a particular entry identity.

### 9.3 CUC

A reviewed CUC line node mapping to `crmtex:TX7_Written_Text_Segment` is:

```text
formal kind: class
role: entity-type
```

A CUC sign node cannot be promoted to `crmtex:TX8_Grapheme` or `TX9_Glyph` simply from `otype=sign`; R-007/R-009 require native evidence resolving abstract-vs-physical written-sign semantics.

### 9.4 Pseudepigrapha-TF

The current variation locus/reading/witness-attestation graph has no accepted common apparatus target. Therefore:

```text
native: reading_of edge
assessment: native-only
target: none
formal kind: none
semantic role: profile-local apparatus relation
```

The schema must support a reviewed no-target record; it must not manufacture an object-property target merely because `reading_of` is an edge.

If a textual version is reviewed as an LRMoo Expression:

```text
target: lrmoo:F2_Expression
formal kind: class
role: entity-type
```

A specific witness identity must not be forced to physical CRM object identity without source evidence.

### 9.5 ORACC-TF

ORACC exposes several formally different target patterns:

- glossary entry/sense identities -> named resources + lexical identity roles;
- physical object/document type -> CRM class + entity-type;
- line/segment -> CRMtex class + entity-type;
- catalogue material/period authority -> authority-reference, potentially `skos-concept` or `named-resource` depending on the chosen authority;
- `cf`, `gw`, `mng` literals -> native literals, not target identities.

A PeriodO URI must not be treated as a CRM class. An AAT record must not be treated as `crm:E57_Material` merely because it labels material semantics; the object can have a CRM material relation and an external authority reference as complementary projections.

### 9.6 TLHdig-TF

Examples:

- document/fragment physical identity -> CRM class/resource projection only where native semantics warrant physical carrier identity;
- line -> CRMtex segment class where physical written-text semantics are active;
- `analysis -> lex` native relation -> no OntoLex object property unless an accepted OntoLex relation with correct domain/range is actually reviewed;
- lex node class -> OntoLex LexicalEntry class + entity-type if converter-defined grouping satisfies the accepted R-008 entry contract;
- editor/history nodes -> CRMinf classes/resources only when the source exposes attributed scholarly claims/processes; a flat edit code alone is insufficient.

## 10. RED-style contract cases for P-003/TDD

These cases should fail before P-003 production implementation accepts the new target contract.

1. **Opaque URI** — target URI present with no formal kind/role -> reject.
2. **Unknown kind** — arbitrary free-string formal kind -> reject.
3. **Unknown role** — arbitrary free-string semantic role -> reject after final P-003 enum/version is selected.
4. **Class as relation** — `formal_kind=class`, `role=relation` -> reject.
5. **Property as entity type** — object/datatype property + `entity-type` -> reject.
6. **Datatype property as graph relation** — datatype property + entity-valued edge plan -> reject.
7. **SKOS mapping misuse** — OWL class target with publication relation `skos:exactMatch` -> reject.
8. **SKOS concept relation misuse** — SKOS concept + `relation` role -> reject.
9. **Class/identity conflation** — `ontolex:LexicalSense` class + `lexical-sense-identity` -> reject unless target is a particular sense resource instead.
10. **Gloss promotion** — native gloss literal + external lexical-concept identity without reviewed sense/concept mapping -> reject.
11. **Authority/class conflation** — PeriodO/AAT authority target marked `entity-type` solely from label semantics -> reject.
12. **Assessment/publication conflation** — TFont `exact` automatically generating `owl:sameAs`, `owl:equivalentClass`, or `skos:exactMatch` -> reject.
13. **Native-only fake target** — `native-only` record forced to carry target kind/role -> reject unless the role is explicitly a profile-local native role outside semantic projections.
14. **Unsupported fake target** — `unsupported` capability record inserted into semantic->native target index -> reject.
15. **Relation direction omitted** — object-property relation with executable native edge but no direction/source-target binding -> reject.
16. **Particular resource without identity rule** — external lexical/authority named resource target but no stable native identity construction -> reject for executable identity lookup.
17. **Unknown ontology artifact type** — target formal kind inferred only from URI suffix/local name -> reject; must resolve from locked ontology metadata/review evidence.
18. **Complementary target collapsed into ambiguity** — two compatible targets with different roles represented as competing candidates -> reject the shape or diagnostic as contract mismatch.
19. **Ambiguity collapsed into complementarity** — mutually exclusive candidate targets represented as simultaneously approved projections -> reject.
20. **Claim fact conflation** — ordinary source fact mapped as CRMinf proposition/inference activity without attributed claim/process evidence -> reject.

## 11. P-003 schema/IR inputs

P-003 must support, conceptually, a projection record containing at least:

```yaml
projection:
  target: <locked IRI>
  formal_kind: <controlled formal-kind>
  semantic_role: <controlled role>
  ontology_lock: <exact artifact/version identity>
  assessment: exact|close|broader|narrower|related|ambiguous
  publication_relation: <optional, kind/role-validated>
  native_binding:
    selector_or_path: <reviewed native binding>
    applicability: <source/target/node/value domain>
    execution_shape: <value predicate | entity type | edge/path | identity key | non-executable>
  evidence: <review/research provenance>
```

`native-only` and `unsupported` remain first-class reviewed mapping/capability records with **no semantic target projection**.

The normalized IR must index:

```text
(native selector/path/value identity)
    -> approved projection(s)

(profile + target + formal kind + semantic role)
    -> per-corpus executable native binding(s)
```

The reverse index key must include kind/role; target IRI alone is insufficient because the same resource may legally participate in more than one role.

## 12. Extensibility/versioning

The vocabulary should be closed and versioned, not unrestricted strings.

Policy:

1. adding a formal kind requires evidence that an accepted ontology/profile contains a materially distinct formal target shape needed for execution/publication validation;
2. adding a semantic role requires at least one demonstrated native mapping whose execution/provenance semantics cannot be represented safely by existing roles;
3. aliases are not silently accepted; canonical role/kind identifiers participate in digest identity;
4. a vocabulary change that changes validation or reverse-index semantics requires a mapping-schema/IR version change;
5. old released mappings retain their original vocabulary version and do not silently acquire new role interpretations.

## 13. Rejected alternatives

### 13.1 One `target_type` enum mixing class/property/lexical-sense/authority

Rejected because it mixes RDF formal shape with domain semantic role and creates a combinatorial enum (`class-linguistic-value`, `resource-lexical-sense`, etc.).

### 13.2 Infer kind from ontology namespace or local name

Rejected. `ontolex:LexicalSense` is a class while a dictionary sense URI is an individual/resource; CIDOC CRM external vocabulary values can be E55 Type instances rather than classes; namespace/local-name heuristics cannot safely distinguish them.

### 13.3 Use RDF `rdf:type` only and omit TFont semantic role

Rejected. RDF type can say a target resource is `skos:Concept` or `ontolex:LexicalSense`, but it does not tell the resolver whether the mapping represents an annotation value, lexical concept identity, external authority, or another role.

### 13.4 Make every authority concept a semantic-pivot concept

Rejected. R-010/R-017 explicitly require authority/value identity to remain distinct from common semantic schema semantics.

### 13.5 Let publication predicate determine mapping strength/type

Rejected. Publication relation is an ontology-specific serialization decision; TFont mapping assessment is the canonical cross-formalism review result.

## 14. Acceptance-criteria closure

- **Minimal controlled formal-kind vocabulary:** `class`, `object-property`, `datatype-property`, `skos-concept`, `named-resource`.
- **Separate semantic-role vocabulary:** entity type, annotation category/value, relation/attribute, lexical identities, authority reference, claim/inference.
- **Single external URI shown insufficient:** demonstrated across OLiA, OntoLex, CRM/CRMtex/LRMoo/CRMinf, AAT/PeriodO-style authorities and native-only apparatus.
- **Publication-relation legality:** explicitly constrained by formal kind/role; no assessment->predicate auto-conversion.
- **Execution implications:** binding shape defined per kind/role without RDF runtime inference.
- **Six heterogeneous corpus tests:** BHSA, Syriac, CUC, Pseudepigrapha-TF, ORACC-TF, TLHdig-TF; ExtraBiblical follows the same high-similarity control pattern and is exercised by R-011.
- **P-003 inputs:** projection shape, reverse-index key, no-target records, versioning/extensibility and RED cases are explicit.

## 15. Remaining boundaries

R-013 intentionally does not decide:

- final semantic profile/capability identifiers — R-014;
- ontology-bundle and bridge-lock schema — R-015;
- approximate execution authorization — R-016;
- final external-authority identity/query policy — R-017;
- production mapping/schema/IR field names — P-003;
- empirical frequency/coverage of each combination — R-011.

Those tickets may refine names or activation policy, but they should not collapse the formal-kind/semantic-role separation established here.
