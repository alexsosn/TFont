# R-009: textology, codicology, and critical-apparatus semantic profile

**Status:** research complete; pending fresh logically-independent review  
**Issue:** #41  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-002/R-003/R-005, merged R-006/R-007/R-008, merged R-012 #54, and merged roadmap guardrail #45

## Decision

TFont should represent textological/codicological semantics as a **layered composition**, not one manuscript ontology and not one universal “witness” class.

The first profile has five distinct layers:

1. **physical carrier / codicology** — CIDOC CRM for physical objects, parts, identifiers, production, materials, places, custody/provenance; CRMtex for the physical writing and written-text segments actually present on those carriers;
2. **intellectual/textual realization** — LRMoo for works, expressions, manifestations/items where justified, expression derivation, and symbolic/textual fragments;
3. **witness / apparatus assertions** — preserve native variation-locus, reading, explicit omission, witness-attestation and unattested states as reviewed profile-local semantic roles unless a supported common ontology target is defensible;
4. **scholarly/editorial epistemic layer** — CRMinf for attributed propositions, beliefs, inference/provenance assessment and meaning-comprehension activity when the source actually records such scholarly claims or processes;
5. **publication / targeting** — Web Annotation remains optional output/targeting infrastructure, not the canonical runtime representation of TF slot sets or apparatus graphs.

The governing invariant is:

> **Physical carrier, physical writing, intellectual text, textual witness, apparatus reading, source assertion, and scholarly inference are separate semantic objects/roles. A source may connect them, but TFont must not collapse them merely because a corpus uses one node or label for several purposes.**

The current evidence does **not** justify minting a normative TFont critical-apparatus ontology. Pseudepigrapha-TF provides a robust full reading/witness graph, but the other inspected corpora expose only related witness, fragment, damage, or editorial assertions rather than a second independent full apparatus model. This preserves the R-002 rule that TFont-local ontology terms are created only for recurring cross-corpus gaps.

TFont does need canonical IR to preserve profile-local apparatus **roles and assertion shapes** so the native model can be executed and compared without inventing a common target. R-013 owns the final controlled role vocabulary; R-011 must test whether these gaps recur strongly enough to justify a later small common vocabulary or whether a reviewed external apparatus profile becomes acceptable.

## 1. Layer model

```text
PHYSICAL / CODICOLOGICAL
  CIDOC CRM physical object / part / material / identifier / place / event
             │
             ├── carries / bears reviewed physical writing
             ▼
WRITTEN TEXT ON THE CARRIER
  CRMtex TX1 Written Text
      └── TX7 Written Text Segment
            ├── line / column / fragment-like written segment where justified
            └── glyph / grapheme distinctions only where native semantics support them

INTELLECTUAL / TEXTUAL
  LRMoo F1 Work
      └── F2 Expression / derivation / symbolic fragment relations
             │
             └── represented/embodied by physical or publication carriers only when source semantics justify it

WITNESS / APPARATUS
  native/profile-local variation locus
      ├── reading A ── attested by ── textual witness X
      ├── reading B ── attested by ── textual witness Y
      └── explicit omission ── attested by ── witness Z

  unattested = reviewed query state derived from absence inside a closed native witness inventory,
               not a fabricated omission or ontology fact

EPISTEMIC / EDITORIAL
  CRMinf proposition / belief / inference / provenance assessment
      └── only when the source records an attributed scholarly assertion or reasoning process
```

The diagram is intentionally not an RDF import graph. Each projection is activated only when the native corpus semantics support that layer.

## 2. Standards and prior-art evidence

### 2.1 CIDOC CRM

CIDOC CRM remains the physical heritage backbone selected by R-002. It is the default layer for:

- a manuscript, tablet, codex, fragment or other physical human-made object when the source denotes a physical carrier;
- physical part-whole relations;
- identifiers and inventory/catalogue identity;
- production, modification and custody/provenance events;
- material/support facts;
- actors, places and times connected to those events.

TFont must not promote an object to a bibliographic/intellectual class merely because it contains text.

A physical fragment is ordinarily a CRM physical object/part. It is **not automatically** an LRMoo textual fragment.

### 2.2 CRMtex 2.0

Primary sources:

- <https://cidoc-crm.org/crmtex/ModelVersion/version-2.0>
- <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>

CRMtex is the selected layer for physical writing itself:

- `TX1 Written Text` — visible/tactile writing on a physical support;
- `TX7 Written Text Segment` — scholarly significant portions of written text, including segmentations such as columns, fragments, sections, paragraphs, words and signs where source semantics fit;
- `TXP4 has segment` — written-text segmentation;
- `TX8 Grapheme` / `TX9 Glyph` — abstract/concrete written-sign distinctions only where the native source supports the distinction;
- text recognition and reading activities only when the corpus records the relevant activity semantics.

R-007 still controls the structural boundary: a TF `line`, `column`, `sign`, slot set or `oslots` relation does not become a CRMtex segment/glyph relation merely from its storage shape.

R-012 controls the version boundary: CRMtex 2.0 keeps its declared old-family dependency closure. The current first pilots do not require `TX2 Writing` or `TX14 Reading` merely to model their textual structure. Pseudepigrapha's node called `reading` is not CRMtex `TX14 Reading`.

### 2.3 LRMoo 1.1.1

Primary sources:

- <https://cidoc-crm.org/lrmoo/ModelVersion/version-1.1.1>
- <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- <https://cidoc-crm.org/sites/default/files/LRMoo_V1.1.1.pdf>

LRMoo supplies the intellectual/textual layer:

- `F1 Work` for the identifiable intellectual creation at work level;
- `F2 Expression` for a particular realization of a work;
- derivation/revision/translation relations among works/expressions where the source states them;
- `F5 Item` where a physical object is genuinely a bibliographic item/holding, not merely any ancient object;
- `R15 has fragment` for **symbolic/expression fragments**, not automatically physical shards/manuscript pieces.

The last distinction is essential. LRMoo `R15 has fragment` relates an `F2 Expression` to an `E90 Symbolic Object` fragment of the expression. A TLHdig physical manuscript fragment may carry a textual fragment, but those are two separate entities unless the source/converter explicitly identifies both layers.

### 2.4 CRMinf 1.2.1

Primary sources:

- <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>
- <https://cidoc-crm.org/sites/default/files/CRMinf_v1.2.1%28stable%29.pdf>

Useful current classes include:

- `I1 Argumentation`;
- `I2 Belief`;
- `I4 Proposition Set`;
- `I5 Inference Making`;
- `I10 Provenance Statement`;
- `I14 Provenance Belief`;
- `I15 Provenance Assessment`;
- `I16 Meaning Comprehension`.

CRMinf is not a generic wrapper for every corpus fact. A source catalogue statement such as “provenience = Nineveh” remains a source assertion/provenance-bearing native fact unless the dataset separately models a scholar's assessed belief or inference. CRMinf becomes appropriate when the source records who asserted, inferred, assessed, reconstructed or adopted a proposition and with what evidence/provenance.

R-012's TX14/I16 result remains in force: current CRMinf treats CRMtex reading/deciphering and I16 meaning comprehension as distinct composable activities, not a direct broader/narrower class mapping.

### 2.5 SAWS

SAWS is valuable historical prior art for ancient-text transmission. It distinguishes manuscripts, manuscript parts/loci, linguistic objects, and transmission relationships.

However it is unsuitable as a new normative TFont dependency:

- its ontology architecture is tied to the older FRBRoo/Erlangen stack rather than current LRMoo;
- its project/content licensing includes non-commercial restrictions incompatible with R-002's normative-dependency openness rule;
- its maintenance/version context is historical rather than an actively current interoperability target.

Decision: **reference/prior art only**, consistent with R-002.

### 2.6 Critical Apparatus Ontology (CAO) 0.9

CAO 0.9 remains useful apparatus prior art, but not a supported TFont dependency:

- version 0.9 was published as a draft-era ontology;
- it depends on older FRBR and ontology-design-pattern components;
- the ontology's licensing/governance state is not sufficient to promote it beyond R-002's existing reference-only status.

Decision: **reference/prior art only**.

### 2.7 Critical Edition Ontology (CEO) 1.0

A newer apparatus model exists and is more relevant than CAO for current design work: **Critical Edition Ontology (CEO) 1.0**, published in 2023 and described in 2024 literature.

CEO provides explicit apparatus concepts including:

- apparatus / critical apparatus;
- apparatus entry / critical apparatus entry;
- reading / reading in apparatus;
- gap;
- witness;
- witness carrier;
- siglum / siglum reference;
- textual tradition;
- critical intervention and critical text/passage;
- Web Annotation-based targeting/selectors.

Its separation between a textual `Witness` and physical `WitnessCarrier` is particularly useful prior art for TFont. Its apparatus reading model is also much closer to Pseudepigrapha-TF than generic CRM/LRMoo alone.

CEO is nevertheless **not promoted to a supported profile in R-009**:

1. R-002 did not review/accept it as a normative dependency;
2. the ontology documentation reuses an older FRBR-family model, so its F-class relationships cannot be assumed compatible with current LRMoo 1.1.1;
3. the publication article has an open license, but R-009 did not establish a sufficiently explicit distributable ontology license for TFont's normative snapshot/redistribution requirements;
4. promoting it would therefore require explicit governance/version/licensing research rather than a convenience import.

Decision: **strongest current apparatus prior art / candidate future alignment profile**, but reference-only for P-003's first design.

### 2.8 Medieval Manuscript Ontology (MeMO) and manuscript-KG prior art

MeMO is useful codicological prior art and exposes manuscript structures such as codex, folio, recto/verso, binding, columns and material. Its CC BY 4.0 licensing is suitable in principle, but its semantic stack is built around older FRBR/FaBiO assumptions and the current TFont pilot corpora do not yet show recurring quire/folio/hand semantics sufficient to justify another normative dependency.

The Mapping Manuscript Migrations project likewise demonstrates that CIDOC CRM + FRBR-family models can support large manuscript provenance graphs, while project-specific terms fill source-specific gaps. Its principal value here is architectural prior art, not a new TFont target ontology.

Decision: **prior art; activate new codicology ontology research only when actual corpus recurrence requires it**.

## 3. Responsibility matrix

| semantic question | primary TFont layer | unsafe shortcut |
|---|---|---|
| What physical object is this? | CIDOC CRM | `manuscript` label ⇒ LRMoo Expression |
| What physical part is this fragment/folio/surface? | CIDOC CRM physical object/part | physical fragment ⇒ LRMoo R15 fragment |
| What writing exists on the carrier? | CRMtex TX1/TX7 where native semantics warrant | TF slot/line ⇒ CRMtex segment automatically |
| What intellectual work is represented? | LRMoo F1 | physical object identity ⇒ Work |
| What textual realization/version is represented? | LRMoo F2 where source identity warrants | every corpus `version` string ⇒ F2 |
| What is a textual/symbolic fragment of an expression? | LRMoo R15 where source defines symbolic fragment | physical sherd/manuscript piece ⇒ R15 |
| Which witness attests which reading at which locus? | native/profile-local apparatus assertion; future reviewed apparatus target | generic `witness` metadata ⇒ reading attestation |
| Is this an explicit omission? | explicit native reading/absence assertion | no edge/value ⇒ omission |
| Is this witness unattested at a locus? | derived closed-world query state with provenance | unattested ⇒ explicit omission |
| Is this a scholarly reconstruction/interpretation? | CRMinf when source records claim/inference | editorial display state ⇒ inference |
| Where/how is an annotation published? | optional Web Annotation | Web Annotation selector ⇒ canonical TF extent |

## 4. Witness identity contract

The word **witness** is too overloaded to be one automatic ontology mapping.

TFont must distinguish at least:

1. **physical witness carrier** — manuscript, tablet, fragment, printed item or other physical object;
2. **textual witness identity** — a textual realization/tradition/edition-level witness that may be preserved by one or more carriers;
3. **witness attestation assertion** — the claim/source fact that a witness supports a particular reading at a particular locus;
4. **witness metadata label** — a source feature saying an object/book belongs to witness A/B without asserting reading-at-locus semantics.

The final controlled role names belong to R-013. R-009 requires only that canonical mapping/IR not collapse these roles.

A corpus may represent more than one role with one native node. TFont should then preserve one native identity plus multiple reviewed projections/roles rather than duplicating or silently retyping the source object.

## 5. Apparatus gap analysis

### 5.1 What the seven-model core covers

The accepted stack already covers most surrounding semantics:

- physical carrier/item/material/provenance → CIDOC CRM / LRMoo where appropriate;
- physical writing and segments → CRMtex;
- work/expression/derivation → LRMoo;
- attributed inference/reconstruction → CRMinf;
- publication targets → Web Annotation optionally.

### 5.2 What it does not cover directly

The seven-model core does not provide a convenient first-class contract for the complete apparatus assertion:

```text
variation locus
  -> one or more readings
  -> each reading attested by zero or more identified textual witnesses
  -> explicit omission represented as positive source evidence
  -> non-attestation distinguished from explicit omission
  -> orphan/malformed readings preserved without fabricating a locus
```

CEO provides close prior art for several of these roles, but is not yet an accepted supported dependency.

### 5.3 Should TFont mint a local apparatus ontology now?

**No.** The empirical recurrence threshold from R-002 is still not met.

Pseudepigrapha-TF supplies a robust full apparatus graph. Peshitta A/B metadata, TLHdig line/fragment witness relations, qere information and ORACC edition structures concern related witness/text phenomena but do not independently instantiate the same full reading-at-locus assertion model.

Therefore R-009 recommends:

- preserve the Pseudepigrapha apparatus graph exactly in native/profile-local IR;
- expose controlled semantic roles/assertion shapes sufficient for agents and R-011 measurements;
- do not insert profile-local roles into the common semantic→native index as though they had a supported ontology target;
- use CEO/CAO/SAWS for mapping research and documentation alignment only;
- let R-011 determine whether another independent corpus demonstrates the same gap strongly enough to justify a tiny TFont vocabulary;
- alternatively, if CEO passes later licensing/governance/current-LRMoo review, prefer adopting/reusing it over creating overlapping local terms.

This is a deliberate `native-only`/profile-local outcome, not a failure of interoperability.

## 6. Pseudepigrapha-TF mapping pattern

Current Pseudepigrapha-TF exposes a substantially stronger apparatus contract than generic manuscript metadata.

### 6.1 Native model

Relevant native identities include:

- textual version / stable TF version ID;
- `unit` — apparatus locus;
- `reading` — ordinary reading at a unit;
- `orphan_reading` — preserved malformed/source-anomaly reading with no fabricated unit;
- `variant_word` — token inside a non-primary reading;
- `manuscript` — source witness identity;
- `resource` / metadata-only version identities.

Relevant edges include:

- `reading_of`: reading → unit;
- `witness`: reading/orphan reading → manuscript;
- `variant_word_of`: variant word → reading;
- `manuscript_of`: manuscript → exact textual version owner;
- `resource_of`: bibliographic resource → exact version owner.

### 6.2 Explicit omission vs unattested

The public apparatus API distinguishes:

- `reading` — witness explicitly assigned to a non-empty reading;
- `omission` — witness explicitly assigned to an empty source reading;
- `unattested` — no reading at the unit cites that witness.

This is a semantic boundary TFont must preserve.

An explicit empty reading is **positive source evidence for omission**. It is not the same as the absence of an edge.

`unattested` is a derived query state valid only relative to a known version/witness inventory and locus set. It must carry the closure/provenance context that justified the derivation and must never be serialized as though the source explicitly asserted omission or lacuna.

### 6.3 Manuscript node semantics

The native `manuscript` node is a textual witness identity in the converter contract. Some source records may correspond to physical manuscript carriers, but TFont must not project every such node directly to a CRM physical object or LRMoo Item without evidence that the source identity denotes that carrier.

A future mapping can legitimately represent:

```text
native witness identity
  -> textual witness role / LRMoo expression candidate where justified

separate physical carrier identity
  -> CIDOC CRM physical object / LRMoo F5 Item where justified

carrier preserves/embodies witness
  -> reviewed relation
```

CEO's `Witness` versus `WitnessCarrier` distinction is useful prior art for this separation.

### 6.4 Version/work semantics

Pseudepigrapha-TF preserves multiple textual versions under one work and explicitly reports `available`, `not_present`, and `metadata_only` states. A normalized chapter/verse address is applied independently per version and is **not** evidence that divisions are aligned across versions.

Therefore:

- a version identity is a candidate LRMoo expression/textual-realization identity after source-level review;
- metadata-only versions remain valid identities and are not fake empty text;
- source references remain authoritative for exact loci;
- common section labels do not manufacture cross-version alignment.

### 6.5 Apparatus projection

Until a supported apparatus ontology is accepted:

| native assertion | TFont treatment |
|---|---|
| `unit` | profile-local variation-locus role; native-only common-target state |
| `reading` | profile-local reading role; native-only common-target state |
| `reading_of` | profile-local reading-at-locus relation |
| `witness` edge | profile-local reading-attestation relation |
| empty reading + cited witnesses | explicit-omission source assertion |
| no reading cites witness at locus | derived unattested state, not source assertion |
| `orphan_reading` | reading identity preserved; locus unsupported/unknown rather than invented |
| manuscript metadata | textual-witness metadata; carrier projection only with independent evidence |

R-011 can still execute Pseudepigrapha-specific apparatus queries through native/profile-local roles. It simply must report that those roles do not yet have a common semantic pivot target.

## 7. TLHdig-TF mapping pattern

TLHdig-TF supplies physical/documentary and editorial structures that stress different layers from Pseudepigrapha.

### 7.1 Physical/document hierarchy

The current model includes the sign/word/line/document hierarchy and physical/documentary layers such as:

- `document`;
- `surface`;
- `column`;
- `line`;
- `fragment`;
- sign-level text;
- witness/join relationships where source evidence provides them.

Candidate mappings:

| native object | candidate layer | guardrail |
|---|---|---|
| document/tablet/manuscript physical object | CIDOC CRM physical object | only if native identity denotes physical carrier |
| physical fragment | CIDOC CRM physical object/part | **not** LRMoo R15 merely because named fragment |
| surface | physical object feature/part + CRMtex support context as reviewed | not generic TF containment |
| column/line written portion | CRMtex TX7 candidate | requires reviewed written-text semantics, not `otype` label alone |
| sign | CRMtex glyph/grapheme candidate | abstract/concrete distinction must be source-evidenced |

### 7.2 Damage/editorial clusters

TLHdig uses `cluster` nodes and induced sign flags for damage/editorial ranges, including range and point-width cases. These are source/editorial states with exact native semantics.

A damage or restoration marker does not automatically mean:

- an ancient physical event is known;
- a modern scholarly inference has been made;
- a specific CRMinf belief exists;
- a CRMtex recognition activity was recorded.

The profile should preserve native cluster type/range/evidence first. CIDOC CRM condition concepts may be candidates where the native state genuinely describes object condition; CRMinf is activated only where an explicit attributed interpretation/reconstruction is represented.

### 7.3 `edit` nodes

An `edit` node is an editorial activity/event in the corpus model. It is not CRMtex `TX2 Writing` simply because it creates or changes encoded text. It may project to a generic activity and, when it makes an attributed proposition or reconstruction with evidence, participate in CRMinf.

### 7.4 Witness/fragment relations

TLHdig witness relations concerning fragments/lines are useful for broad witness discovery but are not equivalent to Pseudepigrapha's reading→manuscript attestation at a variation locus. R-011 must preserve that distinction and refuse a common `witness has reading at locus` query for TLHdig unless an actual native assertion supports it.

## 8. ORACC-TF mapping pattern

ORACC-TF is still a stress/conversion target rather than a finalized released TFont corpus profile. Its source/target schema separates physical/catalogue data, textual structures, lexical layers and editorial/damage information.

Textological use should therefore be layered:

- tablet/document/object identity → CIDOC CRM physical object where source semantics warrant;
- surface/line/written sign structure → CRMtex candidates where reviewed;
- lexical semantics → R-008 OntoLex/OLiA profile, not the textology profile;
- damage/missing/editorial states → native facts, with CRM condition/CRMinf projection only when semantics fit;
- period/provenience/catalogue authority semantics → primarily R-010/R-017, not overloaded into textology;
- no apparatus reading-at-locus capability should be advertised merely because ORACC has editions, readings, normalizations, or source variants.

A source field named `reading` in cuneiform/lexical data is not Pseudepigrapha apparatus `Reading` and is not CRMtex TX14 Reading by label similarity.

## 9. Negative/control corpus

BHSA or ETCBC Syriac is a useful negative/control case. These corpora expose textual sections and linguistic annotation but no physical manuscript carrier graph or full critical apparatus in the inspected TF versions.

Expected capability behavior:

- linguistic/lexical profiles active as appropriate;
- generic textual section/navigation may remain native/structural;
- physical codicology profile absent;
- reading-at-locus apparatus capability absent;
- archaeology/material profile absent;
- a query for manuscript fragments or witness omissions reports unsupported/non-resolvable rather than an empty result that implies the corpus was searched for such assertions.

## 10. Codicological detail policy

Features such as support/material, folio, recto/verso, quire, binding, hand/script and ruling should not force one manuscript ontology into every profile.

Use the following policy:

1. map broadly supported physical facts to CIDOC CRM where the model fits;
2. map physical writing/script features through CRMtex where appropriate;
3. preserve source-local codicological values when no accepted target fits;
4. use MeMO and other manuscript ontologies as design/mapping prior art;
5. promote another normative codicology dependency only after at least two independent target corpora require semantics that CRM/CRMtex/LRMoo cannot represent without repeated local terms.

A sparse corpus advertises absence of the codicological capability rather than installing empty placeholder profiles.

## 11. Provenance, uncertainty, and assertion-status rules

### 11.1 Source facts are not automatically scholarly beliefs

Every mapped assertion must retain whether it comes from:

- direct native/source assertion;
- deterministic converter derivation with explicit rule/closure assumptions;
- reviewed semantic projection;
- attributed scholarly claim/inference;
- TFont runtime/query derivation.

Only the appropriate layers may project to CRMinf belief/inference classes.

### 11.2 Explicit absence differs from missing evidence

Required distinction:

```text
explicit source omission
    != source did not attest witness at this locus
    != source/corpus has no apparatus capability
    != selector/data was not loaded
    != source anomaly/malformed reading
```

These states must remain distinguishable in normalized IR and resolver explanations.

### 11.3 Damage/restoration/uncertainty

TFont must preserve at least:

- native damage/restoration state;
- source certainty/uncertainty value where present;
- responsible source/editor/record when available;
- whether a reconstruction is a source transcription convention or an attributed scholarly proposition;
- exact evidence/reference used for a semantic projection.

No confidence score may be inferred merely from typography or absence unless the source contract defines that rule.

### 11.4 Dating/provenance

A source catalogue date/provenience is a provenance-bearing source assertion. If the corpus separately records the scholar, method/evidence, confidence or competing proposals, those richer claims may activate CRMinf provenance/belief/assessment semantics.

Do not manufacture an inference graph from a flat source date string.

## 12. Canonical mapping/IR requirements for P-003

R-009 requires P-003 to support the following without freezing exact field names here.

### 12.1 Layer/role separation

A native identity or assertion must be able to carry distinct reviewed roles such as:

- physical carrier;
- physical part;
- written text / written segment;
- intellectual work;
- expression/textual realization;
- textual witness;
- variation locus;
- apparatus reading;
- witness attestation;
- explicit omission;
- scholarly claim/inference.

R-013 owns the final controlled role vocabulary.

### 12.2 Multi-entity decomposition

One source record may need several semantic entities rather than one external target. Example:

```text
source manuscript record
  ├── physical carrier projection -> CIDOC CRM
  ├── textual witness projection -> LRMoo/profile-local role
  └── source provenance assertion -> native/PROV/CRMinf as evidence warrants
```

The schema must not force all three into one URI or one mapping assessment.

### 12.3 Assertion shape

A canonical semantic assertion may need:

```text
subject native selector/identity
semantic role/relation
object native selector/identity or literal
source direction/cardinality
assessment/projection(s)
profile membership
source assertion vs derived state
closure assumptions for negative/absence derivations
evidence/review identity
parent component identity
```

This is necessary for apparatus edges and physical/textual relations, not only feature-value mappings.

### 12.4 Native-only profile roles

Profile-local apparatus roles without a supported external target must remain valid `native-only` records. They may support corpus-native query planning and capability reporting but must not appear in common semantic→native indexes as if a common ontology target existed.

### 12.5 Capability granularity

Agent discovery must distinguish at least:

- physical carrier/codicology support;
- written-text segmentation support;
- textual work/version support;
- textual witness discovery;
- reading-at-locus apparatus support;
- explicit-omission support;
- scholarly inference/reconstruction support.

A corpus may support witness discovery but not reading attestation. Exact capability identifiers belong to R-014.

### 12.6 Explanation/provenance

For a textological resolution, agents need to inspect:

- requested common/profile-local semantic role;
- native selector/path/edge actually used;
- mapping assessment/common target if any;
- source assertion vs derived query state;
- closure/witness-inventory context for `unattested`;
- ontology/profile/bridge bundle identities;
- parent corpus/component version;
- evidence/review provenance.

## 13. Representative agent queries

### 13.1 Physical carrier navigation

> Find physical tablets/manuscripts/fragments, then navigate their surfaces/columns/lines where supported.

Expected:

- CUC/TLHdig/ORACC participate only through reviewed physical/written-text mappings;
- Pseudepigrapha participates only if its witness metadata denotes actual carrier identity;
- BHSA/Syriac report unsupported physical-codicology capability.

### 13.2 Textual versions of a work

> Show textual realizations/versions of a work and indicate which are metadata-only or lack this passage.

Expected:

- Pseudepigrapha can expose native version identities and status without manufacturing passage alignment;
- LRMoo projection only where version/expression semantics are reviewed;
- `not_present` and `metadata_only` stay distinct from empty text.

### 13.3 Witness reading at locus

> At this apparatus locus, which witnesses attest each reading?

Expected:

- Pseudepigrapha executes through `unit` + `reading_of` + `witness`;
- TLHdig/Peshitta-style witness metadata does not satisfy this assertion shape unless source semantics independently provide it;
- result explanation states that the apparatus roles are profile-local/native-only until a supported common target exists.

### 13.4 Explicit omissions

> Which witnesses explicitly omit this locus?

Expected:

- only positive empty-reading evidence counts as omission;
- `unattested`, missing edge, absent capability and unloaded feature do not count.

### 13.5 Fragment query

> Find fragments of this textual expression and physical fragments carrying it.

Expected:

- LRMoo R15 may answer symbolic/textual fragments of an expression;
- CIDOC CRM answers physical fragments/parts;
- the two sets are not collapsed; a reviewed relation may connect them.

### 13.6 Scholarly reconstruction

> Which restored/reconstructed readings are editorial claims, who made them, and what evidence supports them?

Expected:

- source-only damage/restoration conventions remain native facts;
- CRMinf is used only where attributed propositions/inference/evidence are actually represented;
- a converter's normalization is not silently described as a scholar's inference.

## 14. Adversarial/negative cases

P-003/R-011 should include at least these failures:

1. **physical/textual fragment collapse:** TLH physical `fragment` → LRMoo R15 solely by label → reject;
2. **witness overload:** Peshitta `witness=A` metadata → reading-at-locus attestation → reject;
3. **apparatus/CRMtex reading collision:** Pseudepigrapha `reading` → CRMtex TX14 → reject;
4. **absence→omission:** no witness edge → explicit omission → reject;
5. **metadata-only→empty text:** metadata-only textual version treated as zero-length expression → reject;
6. **section-label alignment:** identical chapter/verse address across versions → exact textual alignment → reject;
7. **TF containment→codicological part:** `oslots` inclusion → physical part-of → reject without reviewed semantics;
8. **edit→ancient writing:** TLH `edit` → CRMtex TX2 Writing → reject;
9. **damage→inference:** native damage/restoration flag → CRMinf belief/inference without attributed claim → reject;
10. **CEO direct import:** CEO old-FRBR model loaded into current LRMoo bundle without reviewed bridge/governance → fail closed;
11. **SAWS normative activation:** SAWS used as normative dependency despite non-commercial governance conflict → reject;
12. **unattested decontextualization:** derived `unattested` state emitted without witness-inventory/locus closure context → reject.

## 15. Inputs to R-011

The ontology-mapped pilot should test at minimum:

- CRM physical carrier vs CRMtex written-text segmentation on CUC/TLHdig/ORACC;
- LRMoo work/expression/version semantics on Pseudepigrapha where source identity warrants;
- physical fragment vs symbolic fragment separation in TLHdig/textual examples;
- Pseudepigrapha variation-locus/reading/witness/omission roles as profile-local/native-only mappings unless an accepted apparatus target emerges;
- broad witness discovery versus reading-attestation capability distinction;
- CRMinf projection only for real attributed reconstruction/provenance claims;
- unsupported textology/codicology capability on BHSA/Syriac control;
- measured residual gap: whether apparatus roles recur in another independent corpus strongly enough to justify a tiny TFont vocabulary.

A valid R-011 result may conclude that some highly useful textological queries remain corpus-native/profile-local. Coverage metrics must not penalize that by fabricating mappings.

## 16. Inputs to P-003

P-003 should preserve these R-009 conclusions unless later reviewed evidence supersedes them:

1. physical carrier, physical writing, intellectual text, textual witness, apparatus assertion and scholarly inference are separate mapping roles/layers;
2. CIDOC CRM + CRMtex + LRMoo + CRMinf compose the supported foundation for the surrounding textology/codicology semantics;
3. LRMoo R15 textual/symbolic fragments must not be used for physical fragments without a distinct textual-fragment entity;
4. Pseudepigrapha's full apparatus graph remains executable as native/profile-local semantics even without a common ontology target;
5. explicit omission and derived unattested are distinct first-class states with different provenance/closure requirements;
6. textual witness identity and physical witness carrier must be separable;
7. SAWS and CAO remain prior art; CEO 1.0 is the strongest current apparatus prior art/candidate future profile but is not accepted as normative without separate governance/licensing/current-LRMoo review;
8. no TFont apparatus ontology is minted at this stage because full recurrence across independent corpora is not demonstrated;
9. R-013/R-014 must provide role/capability identifiers sufficient to express these distinctions without pretending profile-local roles are ontology targets;
10. R-011 must empirically test both common projections and the residual native-only apparatus gap.

## 17. Rejected alternatives

### A. One `Manuscript` class for carrier + witness + expression

Rejected. Physical object, textual witness and intellectual expression can have different identities and cardinalities.

### B. Use LRMoo for every physical/textual layer

Rejected. LRMoo's expression/work model is complementary to, not a replacement for, CIDOC CRM physical-object semantics or CRMtex physical writing.

### C. Use CRMtex `TX14 Reading` for critical-apparatus readings

Rejected. TX14 is an intellectual reading/comprehension activity. Pseudepigrapha `reading` is a textual alternative at a locus.

### D. Treat every source restoration as CRMinf inference

Rejected. Source transcription/editorial state can be asserted directly without an explicit inference/belief model.

### E. Adopt CAO/SAWS as normative apparatus layer now

Rejected due current support-tier, licensing/version/governance and old-model concerns already captured by R-002/R-009.

### F. Adopt CEO 1.0 immediately

Rejected for the first profile. CEO is better apparatus prior art, but current-LRMoo compatibility and explicit normative ontology licensing/snapshot redistribution have not been reviewed to R-002 standards.

### G. Mint a TFont apparatus ontology now

Rejected. Only one inspected corpus currently exposes a robust full apparatus graph. Profile-local semantic roles preserve functionality without creating a premature vocabulary authority.

## 18. Acceptance-criteria trace

- [x] Keeps physical object, physical writing, intellectual text/version, witness attestation and scholarly inference distinct.
- [x] Covers Pseudepigrapha-TF's actual unit/reading/witness/omission/unattested model, including orphan readings and metadata-only versions.
- [x] Covers TLHdig-TF physical fragments, surfaces/columns/lines, damage/editorial clusters, edit nodes and witness distinctions.
- [x] Distinguishes ORACC physical/textual/catalogue semantics without inventing an apparatus capability.
- [x] Evaluates CIDOC CRM, CRMtex, LRMoo and CRMinf responsibilities and preserves R-012 version/composition constraints.
- [x] Evaluates SAWS and CAO as prior art and identifies CEO 1.0 as stronger modern apparatus prior art without prematurely promoting it.
- [x] Determines that a local TFont apparatus ontology is not yet justified; profile-local roles/native-only mappings are sufficient for the current evidence.
- [x] Defines explicit omission vs unattested/missing/unsupported semantics and scholarly attribution rules.
- [x] Produces implementable R-011/P-003 mapping, IR, capability and adversarial-test requirements.

## 19. References

### Accepted TFont research

- [R-002 ontology governance](R-002-ontology-governance.md)
- [R-005 corpus semantic census](R-005-corpus-semantic-census.md)
- [R-006 common ontology pivot](R-006-common-ontology-pivot.md)
- [R-007 TF structural semantics](R-007-tf-structural-semantics.md)
- [R-008 lexical-semantic profile](R-008-lexical-semantic-profile.md)
- [R-012 CRMtex modern bridge](R-012-crmtex-modern-bridge.md)

### Standards / ontology sources

- CIDOC CRM: <https://cidoc-crm.org/>
- CRMtex 2.0: <https://cidoc-crm.org/crmtex/ModelVersion/version-2.0>
- CRMtex declarations: <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>
- LRMoo 1.1.1: <https://cidoc-crm.org/lrmoo/ModelVersion/version-1.1.1>
- LRMoo declarations: <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- CRMinf 1.2.1: <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>
- Web Annotation Data Model: <https://www.w3.org/TR/annotation-model/>
- SAWS ontology/project: <http://purl.org/saws/ontology>
- Critical Apparatus Ontology: <http://purl.org/spar/c4o/>
- Critical Edition Ontology: <http://purl.org/critical-edition-ontology>
- Medieval Manuscript Ontology: <http://id.essepuntato.it/memo/>

### Corpus evidence

Pseudepigrapha-TF and TLHdig-TF source/converter behavior is pinned by R-005. R-009 additionally checked their current public repository documentation to ensure the interpretation still matches the executable apparatus/document contracts; released R-011 mappings must remain pinned to exact corpus/profile revisions rather than silently following repository heads.