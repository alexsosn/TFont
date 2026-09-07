# R-011: ontology-mapped pilots and cross-corpus semantic coverage

**Status:** research/prototype complete; pending exact-head CI and fresh logically-independent adversarial review  
**Issue:** #43  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-005/R-006/R-007/R-008/R-009/R-010 and R-012

## Decision

The seven-model common semantic basis is **viable as TFont's interoperability pivot**, but only if P-003 keeps native semantics, mapping assessment, capability state, authority references, and common ontology projections separate.

The pilot does **not** support a design in which every native feature gets one external URI or in which ontology-label similarity authorizes execution.

The representative fixture contains:

- all seven required corpora;
- **53 reviewed mapping rows**;
- **109 units of agent-useful weight**;
- **72/109 = 66.1% weighted target coverage** through a defensible common semantic target;
- **15 exact**, **14 close**, **3 ambiguous**, **20 native-only**, and **1 unsupported** rows;
- zero `broader`, `narrower`, or `related` rows in this conservative sample;
- **12 corpus-neutral query probes**, of which **6 common-target queries compile to native plan fragments for at least two corpora**.

The 66.1% figure is **not raw schema coverage**. It is the weighted coverage of the deliberately selected agent-useful fixture. Raw schema consideration is measured separately from the accepted R-005 inventories by `scripts/research/r011_measure.py`.

The result is a qualified **GO** for the common semantic pivot and a **NO-GO** for minting a new broad TFont ontology before R-013–R-017 and P-003. The main remaining gaps are genuine domain gaps, not evidence that the pivot has failed:

- critical-apparatus reading/attestation semantics;
- corpus-specific editorial/damage semantics;
- external authority values such as material/period identifiers;
- language-specific verbal systems;
- unresolved physical-vs-symbolic fragment roles.

## 1. Reproducible artifacts

Machine-readable fixture:

`docs/research/data/r-011/pilots.json`

Measurement/prototype compiler:

`scripts/research/r011_measure.py`

Research contract tests:

`tests/research/test_r011_measure.py`

Run from repository root:

```bash
python scripts/research/r011_measure.py
pytest tests/research/test_r011_measure.py
```

The fixture is intentionally non-production. Compact CURIE-like targets such as `olia:Noun`, `crmtex:TX7`, and `crm:E22_Human-Made_Object` identify the reviewed research concept. R-013 owns final formal-kind/role vocabulary and exact target IRI decisions; P-003 owns the production schema.

R-011 mapping assessment is the R-002/TFont runtime assessment, **not** an RDF publication predicate.

## 2. Corpus set and evidence boundary

The required pilots are all present:

| fixture id | corpus | evidence boundary |
|---|---|---|
| `bhsa` | ETCBC/BHSA | R-005 machine inventory, pinned 2021 artifact |
| `cuc` | Copenhagen Ugarit Corpus | R-005 machine inventory, pinned 0.2.8 artifact |
| `syriac` | ETCBC Syriac | R-005 machine inventory, pinned 0.9 artifact |
| `extrabiblical` | ETCBC extrabiblical | R-005 machine inventory; high-similarity Hebrew control |
| `pseudepigrapha` | Pseudepigrapha-TF | R-005 + R-009/current converter contract |
| `oracc` | ORACC-TF | R-005 measured target schema + current data-model contract |
| `tlhdig` | TLHdig-TF | R-005 machine inventory + R-007/R-009 evidence |

Pseudepigrapha-TF and ORACC-TF do not currently have corresponding generated R-005 JSON inventory files in `docs/research/data/generated/r005/`. The raw-schema measurement therefore reports those two as `not-machine-inventoried-in-r005-generated-set` rather than inventing a denominator. Their representative semantic rows remain evidence-backed by R-005/R-009/R-010 source/converter analysis.

## 3. Coverage metrics

### 3.1 Agent-useful weighted target coverage

Weights are small explicit integers in the fixture. They express **research-query importance inside this pilot**, not corpus frequency and not ontology confidence.

| semantic profile | rows | weight | weight with common target | target coverage |
|---|---:|---:|---:|---:|
| linguistic | 17 | 40 | 34 | 85.0% |
| lexical | 9 | 18 | 14 | 77.8% |
| written text | 8 | 16 | 11 | 68.8% |
| heritage/object | 6 | 14 | 10 | 71.4% |
| textology | 3 | 7 | 3 | 42.9% |
| apparatus | 5 | 9 | 0 | 0.0% |
| scholarly annotation | 3 | 3 | 0 | 0.0% |
| provenance/editorial event | 1 | 1 | 0 | 0.0% |
| archaeology negative control | 1 | 1 | 0 | 0.0% |
| **total** | **53** | **109** | **72** | **66.1%** |

The metric deliberately counts `native-only` as legitimate reviewed content while excluding it from **common-target** weight. It is not treated as a defective mapping.

### 3.2 Mapping-assessment distribution

| assessment | rows | interpretation in this pilot |
|---|---:|---|
| `exact` | 15 | reviewed semantic equality at the requested abstraction level |
| `close` | 14 | useful common concept, but native scope/identity is not asserted identical |
| `broader` | 0 | no sampled case justified this direction safely |
| `narrower` | 0 | no sampled case justified this direction safely |
| `related` | 0 | informative-only relation not needed in the minimal sample |
| `ambiguous` | 3 | source role cannot choose one common target safely |
| `native-only` | 20 | valid source semantics with no accepted common target |
| `unsupported` | 1 | requested capability absent from the corpus contract |

Zero values matter. R-011 does not manufacture broader/narrower/related mappings merely to exercise every enum.

### 3.3 Raw schema consideration

`r011_measure.py` reopens each available R-005 generated inventory and constructs the raw denominator from:

- non-warp node types;
- non-warp node-feature concepts;
- non-warp edge-feature concepts.

Each fixture row names one or more `inventory_refs`. The script reports, per machine-inventoried corpus:

- total raw inventory items;
- unique items considered by the R-011 fixture;
- the percentage considered;
- any fixture reference that does not exist in the accepted inventory.

This is a **consideration metric**, not semantic mapping success. R-011 intentionally samples agent-useful concepts instead of trying to map every orthographic/rendering/helper feature. The contract test requires every machine-inventory reference in the fixture to resolve; a stale or guessed feature therefore fails closed.

Bounded native feature values are represented in the fixture where they are needed for the query suite, for example:

- BHSA `sp=subs/verb`, `nu=pl`, `ps=p1`, `gn=m`;
- Syriac `sp=subs/verb`, `nu=pl`, `ps=first`, `gn=m`;
- CUC `trailer_emen=restored`;
- source-specific verbal-stem values are retained native rather than falsely aligned.

R-005 remains the exhaustive source for the rest of the observed bounded domains.

## 4. Positive cross-corpus query compilation

R-011 distinguishes **plan compilability** from **execution authorization**. A `close` mapping can demonstrate that a common concept resolves to a concrete native selector, while R-016 still decides whether production approximate mode may execute that selector.

### 4.1 Noun

Common request:

`olia:Noun`

Compiles exactly to:

- BHSA: `F.sp.v(n) == 'subs'`;
- Syriac: `F.sp.v(n) == 'subs'`;
- extrabiblical: `F.sp.v(n) == 'subs'`.

This is the strongest positive portability case: one semantic atom, three corpora, exact reviewed mapping in the fixture.

### 4.2 Plural verb

Common conjunction:

`olia:Verb AND olia:Plural`

Compiles exactly in BHSA, Syriac and extrabiblical by combining each corpus's native `sp` and `nu` constraints.

This proves that the semantic IR must compile **conjunctions of common atoms** to one corpus-native plan rather than resolving only independent labels.

### 4.3 First person

`olia:FirstPerson` compiles exactly to:

- BHSA `ps=p1`;
- Syriac `ps=first`;
- extrabiblical `ps=p1`.

The common layer hides spelling differences without erasing the native values reported in provenance/explanation.

### 4.4 Lexical entry

`ontolex:LexicalEntry` compiles to five corpus-specific identity strategies:

- BHSA lexical node — exact in this fixture;
- Syriac corpus-scoped repeated `lex` key — close;
- extrabiblical reviewed lexical identity selector — close;
- ORACC lexical key/object — close;
- TLHdig converter-defined lexical node keyed by its native construction — close.

This is the strongest evidence that one target URI is insufficient. The common concept is reusable while **native identity construction and mapping assessment remain different**.

R-016 must decide whether the four `close` plans can execute in approximate mode. R-011 does not authorize them.

### 4.5 Written-text line segment

`crmtex:TX7` compiles as a `close` candidate for:

- CUC `otype=line`;
- ORACC-TF `otype=line`;
- TLHdig-TF `otype=line`.

The mapping is intentionally not marked `exact`: TF line storage alone is insufficient; R-007/R-009 require the physical-written-text semantics to be active.

### 4.6 Physical textual object

`crm:E22_Human-Made_Object` compiles as a `close` candidate for:

- CUC tablet;
- Pseudepigrapha physical manuscript carrier;
- ORACC object-bearing document;
- TLHdig document.

The target does not imply excavation context, textual-expression identity, or bibliographic-item identity.

## 5. Negative and fail-closed probes

### Apparatus reading + witness attestation

Pseudepigrapha provides a strong native graph (`unit`, `reading`, `reading_of`, `witness`, explicit omission), but R-009 found no accepted common apparatus target. The query therefore remains profile-local/native-only.

This is the most important current ontology gap, but one full apparatus corpus is not enough evidence to mint a general TFont apparatus ontology.

### Damage / restoration

CUC editorial restoration and TLHdig damage/editorial clusters are related research phenomena but differ in granularity, carrier, and source assertion shape. R-011 refuses to collapse them into one shared concept.

### Period

ORACC period values remain native/authority candidates. R-010 establishes PeriodO as a source-defined period authority profile; R-017 must define how authority-resource references participate in query resolution. R-011 therefore does not pretend a period label is a common ontology class.

### Provenience / archaeology

Current pilot evidence does not establish a reusable excavation/stratigraphy graph. BHSA has an explicit `unsupported` archaeology control. Absence of the profile is a capability result, **not a missing-bridge error**.

### Hebrew vs Syriac verbal stems

BHSA `vs` and Syriac `vs={pe,pa,af}` are intentionally native-only in this fixture. Shared feature names do not make the language-specific stem systems equivalent.

This is the required unsafe cross-linguistic comparison control.

## 6. False-equivalence hazards found

The pilot reproduced or strengthened several hazards from R-005–R-010:

1. `lex` does not imply identical lexical identity construction across corpora.
2. `line` does not imply CRMtex segment semantics from TF storage alone.
3. `sign` does not choose glyph vs grapheme automatically.
4. Pseudepigrapha `reading` is not CRMtex `TX14 Reading`.
5. TLHdig physical fragment and LRMoo symbolic fragment cannot be collapsed.
6. `witness` can mean book witness metadata, line→fragment attestation, or reading→manuscript attestation.
7. period/material strings are not ontology classes merely because an AAT/PeriodO URI may later be attached.
8. catalogue/source facts are not CRMinf inference events.
9. ancient-object metadata does not imply CRMarchaeo excavation capability.
10. common feature names in related Semitic corpora do not authorize identity of language-specific verbal categories.

## 7. Multiple complementary targets

The **minimal 53-row fixture contains zero rows for which two common targets are simultaneously asserted as necessary and defensible**. That is a measurement, not a schema recommendation.

R-006/R-009 already demonstrate why P-003 still needs multiple complementary projections:

- one native object can participate in a physical-carrier role and a textual/intellectual role;
- lexical resources can need distinct lexical-entry, form, sense and concept projections;
- source assertions and scholarly-inference descriptions can coexist without identity.

R-011 deliberately refused to create a second target merely to make this metric non-zero. R-013 must test target formal kinds/roles against the actual role separations found here; P-003 should support multiplicity even if this conservative fixture does not force a dual-target row.

## 8. P-003 requirements demonstrated empirically

P-003 needs at least:

1. **typed projections**, because OLiA classes, OntoLex entities, CRM/CRMtex classes and future authority resources do not have the same execution/publication semantics;
2. **native selector identity**, including feature/value predicates, node types, edge paths and derived identity rules;
3. **per-projection mapping assessment**;
4. **profile/capability state** separate from mapping rows;
5. **first-class native-only and unsupported records**;
6. **ambiguous candidates without a fabricated reverse index**;
7. **common target → corpus-native plan indexes**;
8. **conjunction compilation** for multi-atom requests;
9. **explanation output** containing the exact native plan and mapping assessment used;
10. **authority-reference separation** for AAT/PeriodO and similar resources, delegated to R-017;
11. **bundle/bridge identity** delegated to R-015;
12. **approximate-execution authorization** delegated to R-016;
13. **closed target-kind/role vocabulary** delegated to R-013;
14. **controlled agent-facing capability IDs** delegated to R-014.

The production resolver must not infer a target from label similarity, ontology hierarchy traversal, or common TF feature names.

## 9. Go/no-go judgement

### Seven-model common basis: GO

The pivot demonstrates meaningful reuse across heterogeneous corpora:

- OLiA supports exact morphology-category portability among three linguistic corpora;
- OntoLex provides a reusable lexical-entry concept across five corpora while preserving different identity constructions;
- CRMtex supports written-text structural projections across three sign/document corpora;
- CIDOC CRM supports physical-object projection across four heterogeneous corpora;
- LRMoo contributes a defensible text-version/expression candidate in the textology pilot.

The absence of a CRMinf/CRMarchaeo positive row in this minimal fixture is not a rejection of those models. R-009/R-010 showed that current native evidence does not justify activating those profiles merely for coverage.

### New broad TFont ontology: NO-GO

Do not mint a broad local ontology now.

The only strong recurrent gap candidate is apparatus/witness-attestation semantics, and current evidence still has one corpus with the complete reading-at-locus graph. CEO remains strong reference prior art from R-009 but requires separate governance/current-LRMoo/license evaluation before normative adoption.

Profile-local roles/native-only mappings are therefore the correct current result.

## 10. Acceptance trace

- [x] All seven required corpora are represented.
- [x] ETCBC extrabiblical is retained as the required high-similarity Hebrew control.
- [x] Raw schema consideration is reproducibly measured from accepted R-005 inventories where generated machine inventories exist; missing machine denominators are reported explicitly rather than fabricated.
- [x] Agent-useful weighted target coverage is measured independently: 72/109 = 66.1%.
- [x] Mapping-strength distribution is explicit, including zero-count assessments and an explicit `unsupported` negative control.
- [x] Reusable semantic concepts compile across 3–5 corpora.
- [x] Linguistic, lexical, structural/written-text, textological and heritage cases are represented.
- [x] Apparatus, archaeology, damage/editorial and unsafe verbal-category controls fail closed.
- [x] Native-only rows are preserved rather than optimized away.
- [x] Common-concept → native-plan compilation is implemented at fixture/prototype level.
- [x] P-003 schema/IR/runtime requirements are enumerated.
- [x] The common basis receives a qualified GO; a new broad TFont ontology receives NO-GO.

## 11. Review targets

The independent reviewer should actively try to falsify:

1. the `exact` OLiA category rows, especially person/number/POS semantics across BHSA, Syriac and extrabiblical;
2. the lexical-entry identity claims and whether `close` is strong enough/too strong for feature-keyed corpora;
3. CRMtex `TX7` line projections and the physical-written-text precondition;
4. CRM `E22` object projections, especially Pseudepigrapha manuscript and ORACC document roles;
5. LRMoo `F2` use for Pseudepigrapha textual version;
6. the explicit omission/unattested distinction inherited from R-009;
7. the decision to keep apparatus/damage/period/verbal-stem semantics native-only;
8. whether raw schema consideration is being confused with weighted target coverage;
9. whether the prototype accidentally authorizes `close` execution before R-016;
10. whether any fixture row names a native feature/type not present in its pinned evidence.
