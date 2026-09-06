# R-007: common structural semantics for Text-Fabric

**Status:** research complete; pending fresh logically-independent review  
**Issue:** #39  
**Recorded:** 2026-09-06  
**Depends on:** accepted R-002/R-003/R-005 and merged roadmap guardrail #45; compatible with R-006 pending its independent review

## Decision

TFont should **not** replace Text-Fabric's native graph with POWLA, Web Annotation, RDF-star, or another RDF runtime model. The faithful common structural layer is:

1. **native TF warp and feature semantics remain executable truth**;
2. domain-semantic edges/nodes are projected to the seven-model ontology profiles only where their native meaning warrants it;
3. POWLA is an alignment/publication vocabulary for selected linguistic graph structures, not the TF warp itself;
4. Web Annotation is useful for publication/targeting of externally addressable resources or segments, not as the canonical representation of `oslots` or arbitrary TF slot sets;
5. a **tiny TFont structural vocabulary is justified only for TF-specific mechanics that no external model names precisely**, chiefly the neutral slot abstraction, the native `oslots` slot-link relation, and the interpretation of a node type's slot links as textual extent, occurrence set, technical anchor, no-slot entity, or external/sidecar entity;
6. valued/unvalued edge mechanics, edge direction, node-feature applicability, and sidecar selectors belong primarily in the canonical mapping/IR contract rather than being inflated into a new domain ontology.

The key distinction is:

> **TF slot-set coverage/anchoring is structural evidence, not automatically linguistic constituency, physical containment, mereology, or semantic extent.**

TF itself computes structural embedding from `oslots` slot-set inclusion. TFont may expose that as **native TF structural embedding**, but must not silently publish or query it as a domain `partOf`, POWLA `hasParent`, CRM containment, syntactic constituency, or witness/textual-transmission relation unless a reviewed mapping establishes that stronger meaning for the relevant node types.

## 1. Primary evidence

### 1.1 Text-Fabric data model

The inspected Text-Fabric documentation is `annotation/text-fabric` at commit `1079c68e051947efd955b61ad499e3a9beb03b09`, especially `tf/docs/about/datamodel.md`.

The TF model states that:

- slots are textual positions and occupy the first `maxSlot` node numbers;
- all slots share one slot type, which may be `word`, `character`, `sign`, or another atomic choice;
- non-slot text objects are nodes;
- text objects may occupy **arbitrary compositions of slots**;
- nodes can be linked to one slot, a set of slots, or no slots;
- `otype` is the warp node feature assigning object types;
- `oslots` is the warp edge feature connecting non-slot nodes to slots;
- other node features map nodes to string/number values;
- other edge features map ordered pairs of nodes to optional string/number values;
- every edge feature name is already an implicit relation label; a valued edge adds another value;
- `otext` optionally declares text formats and sectioning rather than hard-wiring chapter/verse semantics into the TF core;
- structural embedding can be computed from `oslots`.

Primary source:
<https://github.com/annotation/text-fabric/blob/1079c68e051947efd955b61ad499e3a9beb03b09/tf/docs/about/datamodel.md>

### 1.2 POWLA

POWLA 1.0 is inspected from `acoli-repo/powla` at repository commit family `bd5e930ee1d3b1b57001c25895dbda887d9f286d` and the maintained project README/ontology.

The maintained README is explicit that POWLA models linguistic annotation structures and **does not aim to model textual data or anchoring of annotations in textual data**; it is intended to complement Web Annotation, NIF, CoNLL-RDF, RDFa, and similar mechanisms.

POWLA provides useful graph concepts including:

- `Node`, `Terminal`, `Nonterminal`, `Root`;
- reified `Relation` with `hasSource` / `hasTarget`;
- hierarchical `hasParent` / `hasChild`;
- ordering via `next`;
- annotation layers and annotations.

Critically, POWLA documents `hasParent` as a hierarchical relation with **coverage inheritance**: the string covered by children must also be covered by the parent; phrase structure is a typical example and dependency syntax is a typical counter-example. This is much stronger than generic TF `oslots` semantics.

Primary sources:
- <https://github.com/acoli-repo/powla/blob/main/Readme.md>
- <https://github.com/acoli-repo/powla/blob/main/owl/powla.owl>

### 1.3 Web Annotation

The W3C Web Annotation Data Model is a Recommendation and provides `Annotation`, Body/Target, SpecificResource and Selectors. It explicitly allows segments of external resources to be selected. Standard selectors include fragment, XPath/CSS, text quote, text-position, data-position, SVG, and range selectors.

The Text Position Selector is a **contiguous character interval** in a normalized character stream (`start`, `end`). This is not equivalent to TF's arbitrary set of word/sign/character slots and does not represent the semantic meaning of a technical one-slot anchor. Web Annotation is therefore useful when publishing an annotation against an externally addressable source/segment, but not as the universal TF warp model.

Primary source:
<https://www.w3.org/TR/annotation-model/>

### 1.4 OLiA System Ontology

OLiA's system/annotation-model vocabulary is useful for describing annotation tags and linking native annotation models to a linguistic reference model. It does not provide the missing TF warp semantics: arbitrary slot-set anchoring, technical anchors, zero-span nodes, valued TF edge features, or component-aware sidecars. R-006 therefore uses OLiA as the language-side semantic pivot, while R-007 keeps TF structure separate.

Primary project:
<https://github.com/acoli-repo/olia>

### 1.5 Existing TFont corpus census

R-005 remains the authoritative corpus evidence and prevents an over-literal reading of TF's word “containment”. It demonstrates that the **same `oslots` mechanism is used for materially different native purposes**:

- ordinary textual span/coverage;
- corpus-wide occurrence extent of an abstract lexical node;
- a technical one-slot anchor for a lexical node whose real attestations are explicit edges;
- zero-span or non-textual entities;
- converter/source structures that need external sidecars.

This means a semantic interoperability layer cannot infer domain containment merely from `oslots`.

## 2. TF structural concept inventory

### 2.1 Native node identity

A TF node is an integer identity in one specific warp. Node number has no portable semantic meaning without parent-corpus/component identity.

Required TFont consequences:

- every native node selector is scoped to the parent component manifest;
- mapping rules operate on node type/features/paths, not persistent global meaning of integer IDs;
- generated result provenance includes corpus/profile/component identity.

### 2.2 `otype`

`otype` is a mandatory warp node feature assigning a type label. TFont must distinguish:

- **native structural type label** (`word`, `line`, `lex`, `sentence`, ...);
- **semantic projection of that native type** to OLiA, OntoLex, CRMtex, LRMoo, CRM, etc.

Identical `otype` strings across corpora are not mappings.

### 2.3 Slot

A TF slot is an atomic ordered position in the warp, not a universal linguistic “word” or textual “character”. The slot type is corpus-defined.

Examples from R-005:

- BHSA / ExtraBiblical / Syriac / Pseudepigrapha-TF: `word` slot;
- CUC / TLHdig-TF / ORACC-TF target: `sign` slot.

A common `Slot` concept is therefore useful only at the **TF structural level**. Domain meaning of the thing represented at that position is a separate mapping.

### 2.4 `oslots`

`oslots` is the mandatory valueless warp edge from a non-slot node to the slots linked to it. TF uses these sets for ordering and derived embedding.

TFont needs a neutral name for the **native slot link**, because its semantic interpretation varies by node type. The relation must not be named `hasChild`, `partOf`, `containsWord`, `hasGlyph`, or another domain relation globally.

### 2.5 Node feature

A TF node feature maps node IDs to strings/numbers. Applicability is not a universal schema constraint encoded by TF itself. Dense files can also contain empty/`None` storage records that are not semantic values.

TFont therefore needs explicit reviewed mapping metadata for:

- applicable native node type(s);
- value/domain semantics;
- whether absence is storage absence or an explicit native assertion;
- semantic target projection per feature/value where applicable.

### 2.6 Edge feature

A TF edge feature maps an **ordered source-target pair** to either:

- no additional value: unvalued edge; or
- a string/number: valued edge.

The edge feature name is already an implicit relation label. Direction is part of the native assertion.

TFont must preserve at least:

```text
source selector/type
edge feature name
target selector/type
native direction
value semantics (none | categorical | scalar/open)
```

A semantic mapping may:

- preserve direction;
- map to the inverse direction of an ontology property;
- map an edge **value** to a relation subtype/concept;
- preserve the edge value as a literal attribute rather than pretending it is another relation.

Those choices are reviewed mapping semantics, not generic RDF conversion rules.

### 2.7 Sectioning and `otext`

TF's optional `otext` config tells the runtime which node types/features function as section levels and text formats. The section names are corpus-native.

The structural layer can expose “configured section level/order”, but `book`, `chapter`, `verse`, `tablet`, `column`, and `line` remain domain concepts requiring separate mappings. A three-level `otext` path is not proof that corresponding units are semantically identical across corpora.

### 2.8 Discontinuous node

Because TF nodes occupy arbitrary compositions of slots, a node may be discontinuous. The structural contract must preserve the exact slot set, not normalize it to its minimal contiguous interval.

Consequences:

- the native query planner may use TF's exact slot set/embedding behavior;
- a Web Annotation character interval is not a lossless canonical serialization of a discontinuous TF node;
- POWLA can express discontinuous annotation ordering for appropriate linguistic structures, but that does not make POWLA the warp representation.

### 2.9 Zero-slot node

TF documentation explicitly permits nodes linked to no slots. Such nodes can still have type/features and participate in semantic edges.

A zero-slot node is not “missing data”. It can be a genuine non-textual entity.

### 2.10 Sidecar-backed entity

R-001/P-001 already allow semantically addressable native components outside the TF warp. A catalogue entity, provenance record, or zero-span object may therefore be addressed by a native adapter/sidecar rather than a TF node number.

The common structural contract must not force sidecar entities to acquire fake TF slots merely to participate in semantic resolution.

## 3. Slot-link interpretation: the required missing distinction

The same native `oslots` mechanism can encode different relationships between a node and its slot set. TFont should require an **extent/anchor interpretation per relevant node type or selector family**.

R-007 recommends the following minimal controlled meanings as a P-003 design input:

| mode | meaning | use in domain reasoning |
|---|---|---|
| **textual-extent** | the slot set is the actual represented textual/inscriptional extent of the native object | may support reviewed containment/segment mappings; discontinuity is allowed |
| **occurrence-set** | the slot set enumerates occurrences/attestations of an abstract entity | must not be treated as one contiguous textual object or ordinary containment hierarchy |
| **technical-anchor** | one or more slots exist only to anchor/address the node in the TF warp | never infer semantic extent/containment from the slot link |
| **no-slot** | a TF node is intentionally linked to no slots | semantic identity/relations remain valid; no textual extent is implied |
| **external-entity** | the entity is addressable in a sidecar/native component outside the TF warp | no `oslots` semantics at all; use component-native identity/path |

These modes describe the interpretation of the native addressing structure; they are **not ontology mapping assessments** such as `exact`/`close`.

A future validator should require the mode wherever semantic query planning could otherwise confuse slot coverage with semantic extent. Defaulting all non-slot nodes to `textual-extent` is unsafe.

## 4. Corpus stress cases

### 4.1 BHSA

R-005 establishes:

- slot type: `word`;
- textual/linguistic layers: `subphrase`, phrase/phrase_atom, clause/clause_atom, sentence/sentence_atom, half-verse, verse, chapter, book;
- lexical `lex` nodes;
- semantic edges including `mother`, `functional_parent`, and `distributional_parent`.

Structural consequences:

- word and ordinary textual-object node extents can use `textual-extent` where the native definition warrants it;
- `lex` nodes use **occurrence-set** semantics: their `oslots` extent is the set of word occurrences, not one lexical text span;
- `mother`, `functional_parent`, and `distributional_parent` must not be derived from or replaced by `oslots` containment;
- functional objects can differ from continuous distributional `*_atom` objects, so a generic “phrase parent” collapse would destroy native analysis.

POWLA `hasParent` is only a candidate for a reviewed edge whose native semantics actually satisfy coverage-inheriting hierarchical annotation; it is not the generic mapping of any BHSA parent-like edge.

### 4.2 CUC

R-005 establishes:

```text
sign (slot) -> word -> line -> column -> tablet
```

and no corpus-specific semantic edge features in the pinned release.

CUC is a clean case where TF structural coverage and physical/written-text hierarchy can often be projected further into CRMtex/CRM after domain review. Still:

- TF `sign` = slot does not by itself establish CRMtex Grapheme or Glyph;
- `line`/`column` can be candidate CRMtex written-text segments, but the mapping is semantic, not a consequence of slot inclusion;
- editorial sign features (`emen`, `cert`, `alt`) remain separate annotation semantics.

### 4.3 TLHdig-TF

Pinned R-005 evidence includes:

```text
sign (slot) -> word -> line -> column -> surface -> document
```

plus `analysis`, `lex`, `cluster`, `fragment`, `note`, `edit`, and `docgroup` overlays.

Important stress cases:

- morphology is on separate `analysis` nodes and alternatives remain separate;
- `analysis -> lex` explicitly carries lexical attestation/reference semantics;
- TLH `lex` nodes use a **technical one-slot anchor**, unlike BHSA lexeme occurrence extents;
- `cluster` nodes represent editorial/damage ranges and include zero-width editorial statements in the conversion model;
- sign-level cuneiform is only populated when an alignment mechanism justifies it.

Thus two nodes named `lex` in BHSA and TLH can have completely different `oslots` interpretation while sharing a possible OntoLex semantic target. This is the strongest empirical argument for separating semantic entity mapping from native extent mode.

### 4.4 Pseudepigrapha-TF

Pinned converter/apparatus contracts use:

- `unit` textual apparatus loci;
- reading nodes;
- manuscript/witness entities;
- `reading_of`, `witness`, `is_primary`, manuscript relations;
- explicit empty readings for omissions;
- orphan readings that intentionally lack a `reading_of` locus;
- metadata-only/undefined witness cases.

The structure cannot be reconstructed from slot inclusion alone. `reading_of` and `witness` are semantic directed edges; omission is an explicit reading state, not an empty TF feature record or absent `oslots` link.

### 4.5 ORACC-TF target

R-005 treats ORACC-TF as an implementation/stress target. Relevant structures include document/surface/column/line/word/sign layers, lexical entities and explicit lexical links, plus catalogue/metadata entities and zero-span cases.

The important negative control is the source `c type=sentence` chunk: its label is not enough to make it the same semantic object as a BHSA linguistic sentence.

ORACC also motivates sidecar/external-entity support because catalogue/object metadata need not naturally be encoded as text spans.

### 4.6 Simple control: ETCBC Syriac 0.9

The pinned Syriac control has `word` slots and straightforward `book / chapter / verse` sections with morphological node features and no custom semantic edge features. This demonstrates that the structural contract does not require every corpus to instantiate all complexity classes: ordinary corpora can expose only slot, textual extents, configured sections, and node-feature mappings.

## 5. Mapping matrix to existing open models

Legend: **direct** = good semantic fit when native evidence warrants it; **conditional** = useful only after stronger domain review; **publication** = useful serialization/targeting mechanism; **gap** = does not express the TF structural meaning faithfully enough.

| TF structural concept | POWLA | OLiA System | Web Annotation | seven-model domain profiles | conclusion |
|---|---|---|---|---|---|
| atomic TF slot independent of linguistic type | `Terminal` is linguistically oriented and anchoring is external | gap | selector positions/segments are source-specific, not TF slot identity | CRMtex may type a represented sign/glyph, not the TF slot mechanic | **small local structural term justified** |
| exact native `oslots` link | `hasParent` is too strong; POWLA itself delegates anchoring | gap | can select source segment, but not generic arbitrary TF slot sets/technical anchors | domain containment only conditionally | **small local neutral relation justified** |
| textual-extent interpretation | POWLA hierarchical coverage can align for suitable linguistic structures | gap | useful for publication against source segments | CRMtex written-text segment may align where appropriate | local mode + domain mapping |
| occurrence-set extent | no direct generic TF equivalent | gap | multiple targets are not the same semantics as one TF occurrence-set node | OntoLex can model lexical entity/attestation in domain layer | local extent mode required |
| technical anchor | no suitable semantic relation | gap | selector would falsely imply targeted segment meaning | no domain relation should be inferred | local extent mode required |
| zero-slot TF node | POWLA graph node possible but textual anchoring outside scope | gap | annotation/resource can exist without matching TF semantics | domain ontology can type entity | native/local structural state |
| sidecar entity | outside POWLA corpus graph assumption | gap | web resource can identify entity if published | CRM/LRMoo/OntoLex etc. can type entity | mapping IR/native adapter, not forced TF node |
| arbitrary directed edge | reified `Relation` is a good publication structure | gap | Annotation body-target relation is not generic graph edge semantics | map edge semantics to OLiA/CRM/etc. when justified | keep native edge; optional POWLA/RDF publication |
| valued directed edge | POWLA relation + annotation can publish | gap | can annotate a relation resource but not canonical TF mechanic | target ontology may model value differently | native IR tuple; publication may reify/RDF-star |
| discontinuous slot set | POWLA supports discontinuous linguistic structures/order | gap | standard text-position selector is contiguous; custom/multiple targeting needed | CRMtex may model segment semantics but not TF warp set | preserve exact native set; optional publication adapter |
| configured section hierarchy | document/layer concepts only partially fit | gap | can target resources/segments | CRMtex/LRMoo/CRM can map actual units | keep `otext` config + semantic mappings |
| explicit omission vs storage empty | annotation graph can represent explicit relation/state if modeled | linguistic tags only | can annotate explicit state, not infer it | textology profile handles explicit omission | never infer from missing/empty TF data |

## 6. POWLA decision

### 6.1 What POWLA is good for

POWLA remains valuable for publication/alignment of **actual linguistic annotation graph semantics**, especially:

- nodes and annotation layers;
- explicit hierarchy when coverage inheritance is part of the native semantics;
- reified directed relations with source/target;
- explicit sibling/annotation ordering;
- interoperability with linked linguistic data tooling.

### 6.2 Why `oslots -> powla:hasChild` is rejected

`powla:hasParent` / `hasChild` carries coverage-inheriting hierarchical annotation semantics. TF `oslots` is the warp relation used for all non-slot node extents/anchors. R-005 shows occurrence-set and technical-anchor uses where “child/parent” would be false.

Therefore the mapping:

```text
TF oslots  ==  POWLA hasChild
```

is rejected globally.

For a particular corpus relation such as a reviewed constituent-parent edge, POWLA `hasParent` may still be a valid **domain projection of that explicit edge**, independent of `oslots`.

### 6.3 POWLA should not be a runtime dependency

Even where POWLA is a useful publication target, Context-Fabric already executes the TF graph directly with exact node/edge/slot semantics. Re-serializing the graph to POWLA before every query would add conversion cost and create semantic pressure to force non-linguistic object/textology/heritage data into a linguistic graph model.

## 7. Web Annotation decision

Web Annotation is retained from R-002 as an optional publication/targeting profile.

Useful cases:

- publish a TFont mapping/evidence annotation whose target is a stable corpus resource;
- target a source XML/PDF/web fragment with a standard selector when that selector faithfully identifies the evidence;
- expose a human-auditable target separate from runtime native node identity.

Not suitable as canonical TF structure because:

- TextPositionSelector is character-offset based and contiguous;
- TF slots may be words or signs rather than characters;
- TF node extents may be discontinuous arbitrary slot sets;
- occurrence-set and technical-anchor semantics are not “select this segment of the source”;
- valued directed graph edges and native feature applicability are not naturally represented by selector semantics.

A future publication adapter may define a TFont-specific Web Annotation Selector for stable slot sets, but R-007 does **not** require one for runtime or for the canonical mapping source.

## 8. Valued edges and publication mechanisms

TFont needs an internal normalized representation equivalent to:

```text
edge assertion = (
    native edge feature,
    source native selector/node,
    target native selector/node,
    optional native edge value,
    direction,
    applicability/dependency evidence
)
```

This is enough for native Context-Fabric execution.

RDF publication can choose among:

- a direct ontology property when the edge is unvalued and the property meaning/direction is reviewed;
- an explicit relation resource (POWLA Relation or a domain event/assertion entity) when the relation itself needs metadata;
- RDF-star/reification where appropriate for publication tooling.

RDF-star/reification is therefore **not** a new semantic ontology dependency and is not required at runtime.

## 9. Explicit absence is not storage absence

R-003/R-005 already establish that dense empty-string/`None` TF records are storage facts, not semantic values.

R-007 extends this rule structurally:

- no node-feature value does not mean `Unknown`, `Absent`, `Omitted`, `Unattested`, `Damaged`, etc.;
- no edge does not mean an explicit negative relation;
- no `oslots` link does not by itself mean omitted text;
- a zero-slot entity can be semantically valid;
- an explicit omission must be represented by a native assertion whose semantics say “omission” (as in the Pseudepigrapha apparatus), then mapped through the textology profile.

This distinction must survive coverage metrics and agent explanations.

## 10. Minimal TFont structural vocabulary recommendation

An existing external ontology does **not** name TF's neutral slot mechanics precisely enough. A local vocabulary is therefore justified, but it should be deliberately tiny and non-domain-semantic.

R-007 recommends only the following public concepts as the initial ceiling; exact namespace/URI is a P-003/design decision:

1. **`Slot`** — an atomic ordered position in a particular TF warp. It does not imply Word, Sign, Grapheme, Glyph, Character, Token, or any domain class.
2. **`slotLink`** — the neutral native relation corresponding exactly to `oslots`: a non-slot TF node is linked to a slot in its warp. It does not imply immediate child, semantic part, physical containment, or constituency.
3. **`SlotLinkInterpretation`** — a controlled concept scheme whose initial values are:
   - `textualExtent`;
   - `occurrenceSet`;
   - `technicalAnchor`;
   - `noSlot`;
   - `externalEntity`.

That is the **maximum** local ontology surface justified by current evidence.

The following should **not** become ontology terms unless later evidence demonstrates a concrete interoperability need:

- `NodeFeature`;
- `EdgeFeature`;
- `ValuedEdgeFeature`;
- edge source/target/value;
- node integer identity;
- section level number;
- direction flags.

Those are native mapping/IR schema mechanics. Creating RDF classes for all of them would recreate the whole TF implementation as an ontology without improving semantic interoperability.

### 10.1 Alignment policy for the tiny vocabulary

The local terms are alignment hooks, not replacements for domain semantics:

```text
native TF node with textualExtent
   ├─ structural: has slotLink(s)
   └─ semantic: may map to CRMtex Written Text Segment / OLiA constituent / etc.

native TLH lex node with technicalAnchor
   ├─ structural: has slotLink(s), interpretation=technicalAnchor
   └─ semantic: may map to OntoLex lexical entity
```

The semantic target remains the open domain ontology. The local vocabulary explains how the native TF graph realizes/address that target.

## 11. Structural query-planning contract

The agent should never need to reason directly from `oslots` semantics. The resolver receives reviewed structural metadata and emits native plan fragments.

Conceptually:

```text
semantic request
   ↓
semantic target mapping
   + structural realization
       - carrier: tf-node | sidecar
       - native node type
       - slot-link interpretation
       - feature/value or edge path
       - edge direction/value semantics
   ↓
Context-Fabric native plan
```

### 11.1 Domain concept plus native extent

Example: “written-text lines” across CUC and TLHdig-TF.

- semantic layer identifies reviewed CRMtex line/segment mapping;
- structural layer says which native `otype` realizes it and that its slots are `textualExtent`;
- Context-Fabric uses native `otype`/`oslots` navigation.

### 11.2 Relation query

Example: “reading attested by witness”.

- textology profile maps the semantic relation;
- structural binding specifies Pseudepigrapha `reading` source, `witness` directed edge, manuscript target;
- resolver compiles that explicit edge path;
- another corpus with a `witness`-named feature does not participate unless its reviewed semantic mapping matches the same relation.

### 11.3 Discontinuous object

A semantic query that returns a discontinuous BHSA functional phrase should preserve the exact native node/slot set. Rendering/export may later convert that to multiple ranges, but the semantic result identity remains the native object rather than a fabricated contiguous span.

### 11.4 Sidecar object

A semantic request for an ORACC catalogue object may resolve to a sidecar/native-adapter selector rather than a TF `otype`. Context-Fabric/TFont must carry that component dependency in the plan and provenance. No fake slot anchor is required.

## 12. P-003 contract requirements

P-003 should preserve/add the following structural requirements.

### Preserve from P-001/R-003

- parent component manifest identity;
- semantically addressable sidecar/native-adapter components;
- explicit native selectors and dependency closure;
- fail-closed compatibility;
- native query execution;
- dense-empty non-semantic rule;
- inspectable native plan/provenance.

### Add/version

1. **native carrier kind**: at minimum TF node vs sidecar/native-adapter entity;
2. **slot-link interpretation** for TF node families where `oslots` could otherwise be misread;
3. exact preservation of discontinuous slot sets when object identity/extent is returned;
4. first-class directed edge selector/path semantics;
5. explicit distinction between valued and unvalued edge matching;
6. value-role metadata for valued edges where the value is categorical vs scalar/open;
7. reviewed node-feature applicability rather than inference from dense storage records;
8. structural capability for zero-slot nodes/entities;
9. a tiny public structural vocabulary limited to `Slot`, neutral `slotLink`, and slot-link interpretation concepts unless later research justifies more;
10. optional POWLA/Web Annotation/RDF publication adapters kept outside the runtime execution contract.

## 13. TDD implications for later implementation

After P-003, structural implementation tickets should begin with contract tests that demonstrate failure of tempting false assumptions.

Required RED cases should include:

1. BHSA `lex` occurrence-set is **not** treated as one text span or containment object.
2. TLH `lex` technical one-slot anchor is **not** treated as semantic lexical extent.
3. identical `witness` names across Pseudepigrapha/Peshitta/TLH do not create the same edge predicate.
4. an ORACC `sentence`-labelled source chunk does not satisfy a linguistic-sentence capability without a reviewed mapping.
5. a discontinuous node preserves its exact slot set.
6. a zero-slot node remains addressable.
7. a sidecar entity can resolve without fake `oslots`.
8. valued edge direction and value are preserved in native plan compilation.
9. empty/absent feature/edge data never become explicit omission/absence semantics.
10. a reviewed POWLA/CRMtex/domain relation may compile to a native edge/path, but `oslots` alone never fabricates it.

## 14. Rejected alternatives

### A. POWLA as the canonical TF structural ontology

Rejected. POWLA is linguistically oriented, explicitly delegates textual anchoring, and gives `hasParent` coverage-inheritance semantics that are too strong for generic `oslots`. It remains valuable alignment/publication prior art.

### B. `oslots` = semantic containment

Rejected. R-005 provides concrete occurrence-set and technical-anchor counterexamples. TF structural embedding is useful native behavior but not a universal domain mereology.

### C. `oslots` = POWLA `hasChild`

Rejected globally for the same reason. May be valid only for a separately reviewed explicit hierarchical relation whose native semantics satisfy POWLA's coverage-inheritance contract.

### D. Web Annotation selectors as canonical TF extents

Rejected. Standard selectors are source/media specific; text positions are contiguous character ranges and cannot losslessly encode arbitrary TF slot sets and anchor semantics. Web Annotation remains optional publication/targeting infrastructure.

### E. Reify every node/feature/edge in a new TFont ontology

Rejected. This would rebuild Text-Fabric's implementation metamodel in RDF and make TFont a competing graph runtime. Only the small uncovered structural distinctions should get public vocabulary terms.

### F. Force zero-span/sidecar entities into the warp

Rejected. It changes native identity/extent semantics and conflicts with R-001/P-001's component-aware architecture.

### G. Infer domain relation from edge name or node type string

Rejected. Direction, applicability, corpus-native definitions, and mapping evidence are mandatory.

## 15. Remaining boundaries owned elsewhere

R-007 answers the structural-metagraph problem and deliberately does not decide domain mappings that belong to other research tickets:

- exact OLiA linguistic relation mappings: R-006/R-011 and future corpus mapping review;
- lexical entity/attestation semantics: R-008;
- witness/reading/apparatus semantics: R-009;
- physical object/archaeological relations: R-010;
- empirical mapping strengths across all pilots: R-011;
- final semantic target formal kinds/roles: R-013;
- final capability identifiers: R-014.

No additional research ticket is required by R-007 at this point. The exact namespace and serialization of the tiny structural vocabulary are P-003/design concerns once R-007 is independently accepted.

## 16. Acceptance-criteria trace

- [x] **Slot coverage vs constituency/containment distinguished.** Sections 2–3 and 6 explicitly separate `oslots` from stronger domain relations.
- [x] **Valued edges and direction covered.** Sections 2.6 and 8 define the required native assertion tuple and mapping choices.
- [x] **Discontinuous, zero-span and sidecar semantics covered.** Sections 2.8–2.10 and 11 provide explicit contracts.
- [x] **POWLA tested against actual TF structures.** Sections 4–6 use BHSA, TLH, Pseudepigrapha, ORACC and CUC counterexamples.
- [x] **No RDF/SPARQL runtime requirement.** Native Context-Fabric remains the executor; RDF mechanisms are publication adapters only.
- [x] **Local vocabulary justified and bounded.** Section 10 caps it at Slot, neutral slotLink, and a small slot-link interpretation scheme.
- [x] **Concrete P-003/TDD requirements produced.** Sections 12–13 provide design and RED-test inputs.

## Review gate

The exact final head requires a fresh logically-independent skeptical review against:

- Text-Fabric's authoritative data-model documentation;
- POWLA's maintained README and OWL semantics, especially `hasParent`/`hasChild` and relation reification;
- W3C Web Annotation selector semantics;
- R-005's pinned corpus evidence for BHSA, CUC, Syriac, TLHdig-TF, Pseudepigrapha-TF and ORACC-TF;
- R-001/P-001 component-aware sidecar semantics.

The reviewer should actively try to falsify the local-vocabulary recommendation: if `Slot`, neutral `slotLink`, or the interpretation scheme can be represented precisely by a maintained open standard without semantic overclaiming, they should be removed rather than duplicated.
