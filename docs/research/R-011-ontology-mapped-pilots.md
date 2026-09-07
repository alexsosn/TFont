# R-011: ontology-mapped pilots and cross-corpus semantic coverage

**Status:** research/prototype complete; pending exact-head CI and fresh logically-independent adversarial review  
**Issue:** #43  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-005/R-006/R-007/R-008/R-009/R-010 and R-012

## Decision

The seven-model common semantic basis is **viable as TFont's interoperability pivot**, provided P-003 keeps native semantics, mapping assessment, capability state, authority references, and common ontology projections distinct.

The representative non-production fixture contains all seven required corpora, **53 reviewed rows**, **109 agent-useful weight units**, and **72/109 = 66.1% weighted common-target coverage**. Mapping assessments are: 15 `exact`, 14 `close`, 3 `ambiguous`, 20 `native-only`, 1 `unsupported`, and zero `broader`/`narrower`/`related` in this deliberately conservative sample.

This 66.1% figure is **not raw schema coverage**. Raw schema consideration is computed separately from accepted R-005 inventories by `scripts/research/r011_measure.py`.

The result is a qualified **GO** for the common pivot and a **NO-GO** for minting a broad TFont ontology before R-013–R-017/P-003.

## Reproducible artifacts

- `docs/research/data/r-011/pilots.json` — machine-readable fixture;
- `scripts/research/r011_measure.py` — measurement and prototype query compiler;
- `tests/research/test_r011_measure.py` — research contract tests.

Run:

```bash
python scripts/research/r011_measure.py
pytest tests/research/test_r011_measure.py
```

Compact targets such as `olia:Noun`, `olia:First`, `crmtex:TX7`, and `crm:E22_Human-Made_Object` are research identifiers for the reviewed ontology concepts. R-013 owns final target formal kinds/roles and production IRI handling. Mapping assessment remains a TFont runtime concept, not an RDF publication predicate.

## Corpus set

| fixture id | corpus | evidence boundary |
|---|---|---|
| `bhsa` | ETCBC/BHSA | R-005 generated inventory, TF 2021 pin |
| `cuc` | Copenhagen Ugarit Corpus | R-005 generated inventory, TF 0.2.8 pin |
| `syriac` | ETCBC Syriac | R-005 generated inventory, TF 0.9 pin |
| `extrabiblical` | ETCBC extrabiblical | R-005 generated inventory; high-similarity Hebrew control |
| `pseudepigrapha` | Pseudepigrapha-TF | R-005 + R-009/current converter contract |
| `oracc` | ORACC-TF | R-005 measured target schema + current data-model contract |
| `tlhdig` | TLHdig-TF | R-005 generated inventory + R-007/R-009 evidence |

Pseudepigrapha-TF and ORACC-TF do not have generated R-005 JSON inventories in the current repository. The script reports those raw denominators as unavailable instead of fabricating comparable percentages.

## Coverage

### Agent-useful weighted target coverage

| profile | weight | common-target weight | coverage |
|---|---:|---:|---:|
| linguistic | 40 | 34 | 85.0% |
| lexical | 18 | 14 | 77.8% |
| written text | 16 | 11 | 68.8% |
| heritage/object | 14 | 10 | 71.4% |
| textology | 7 | 3 | 42.9% |
| apparatus | 9 | 0 | 0.0% |
| scholarly annotation | 3 | 0 | 0.0% |
| provenance/editorial | 1 | 0 | 0.0% |
| archaeology negative control | 1 | 0 | 0.0% |
| **total** | **109** | **72** | **66.1%** |

Weights express pilot research usefulness, not corpus frequency or ontology confidence. `native-only` remains legitimate reviewed content and is intentionally excluded from common-target weight.

### Raw schema consideration

For each available R-005 generated inventory the script constructs the denominator from non-warp node types, node-feature concepts, and edge-feature concepts. Fixture rows carry `inventory_refs`; the script reports total inventory items, unique considered items, consideration percentage, and stale/unknown references. The contract test requires every machine-inventory reference used by the fixture to resolve.

This metric answers “which native schema concepts did this pilot inspect?” rather than “what percentage maps to a common ontology?”. Those questions must not be conflated.

## Positive query portability

The prototype has twelve query probes. Six common-target queries compile to native plan fragments for at least two corpora:

1. **Noun — `olia:Noun`**: exact in BHSA, Syriac, extrabiblical via their native `sp=subs` constraints.
2. **Plural verb — `olia:Verb AND olia:Plural`**: exact conjunction in the same three corpora.
3. **First person — `olia:First`**: exact mapping from BHSA/extrabiblical `ps=p1` and Syriac `ps=first`. OLiA linking models map annotation-model “FirstPerson” classes to the Reference Model class `olia:First`; R-011 therefore uses the Reference Model identifier, not `olia:FirstPerson`.
4. **Lexical entry — `ontolex:LexicalEntry`**: BHSA exact candidate; Syriac, extrabiblical, ORACC, and TLHdig are `close` because their native lexical identity construction differs.
5. **Written-text line — `crmtex:TX7`**: `close` candidates for CUC, ORACC-TF, and TLHdig-TF when physical-written-text semantics are active.
6. **Physical textual object — `crm:E22_Human-Made_Object`**: `close` candidates for CUC tablet, Pseudepigrapha physical manuscript carrier, ORACC object-bearing document, and TLHdig document.

A compiled `close` plan is **not execution authorization**. The prototype marks it `approximate-candidate-R016-required`; R-016 owns production approximate-mode policy.

## Fail-closed probes

- **Apparatus reading/witness attestation:** Pseudepigrapha has a strong native graph, but R-009 found no accepted common apparatus target. It remains native/profile-local.
- **Damage/restoration:** CUC restoration and TLHdig damage/editorial ranges remain native because their granularity and assertion semantics differ.
- **Period:** ORACC period values remain native authority candidates until R-017 defines PeriodO/external-authority resolution semantics.
- **Provenience/archaeology:** current pilot evidence does not establish reusable excavation/stratigraphy semantics. BHSA carries an explicit `unsupported` negative control; absent archaeology capability is not a bridge failure.
- **Hebrew vs Syriac verbal stems:** native `vs` systems are deliberately not equated merely because the feature names match.

## False-equivalence hazards confirmed

1. `lex` does not imply identical lexical identity construction.
2. `line` storage does not automatically imply CRMtex TX7 semantics.
3. `sign` does not select glyph vs grapheme without source evidence.
4. Pseudepigrapha `reading` is not CRMtex `TX14 Reading`.
5. TLHdig physical fragment cannot be collapsed into LRMoo symbolic fragment.
6. `witness` has materially different assertion shapes across corpora.
7. material/period strings are authority values, not ontology classes by default.
8. catalogue/source facts are not CRMinf inference events.
9. ancient-object metadata does not imply CRMarchaeo excavation capability.
10. common feature names do not make language-specific verbal categories equivalent.

## Multiple complementary projections

This minimal fixture has **zero rows with two simultaneously asserted common targets**. That is a measured result, not a schema recommendation. R-006/R-009 still require P-003 to support complementary projections because physical carrier, textual/intellectual role, lexical identity, grammatical annotation, and scholarly inference can legitimately coexist as different semantic dimensions. R-011 refuses to add a second target merely to make this metric non-zero.

## P-003 requirements demonstrated

P-003 must support:

- typed projections and native selector/path identity;
- per-projection mapping assessment;
- controlled profile/capability state separate from rows;
- first-class `native-only`, `unsupported`, and ambiguity;
- common-target → corpus-native plan indexes;
- conjunction compilation;
- explanations exposing the exact native plan and assessment;
- R-015 bundle/bridge identity;
- R-016 approximate execution authorization;
- R-017 authority-resource separation;
- R-013 target-kind/role vocabulary and R-014 agent-facing capability IDs.

The resolver must never manufacture mappings from label similarity, shared TF feature names, or ontology hierarchy traversal alone.

## Go/no-go

**GO:** the common pivot shows real reuse across heterogeneous corpora: OLiA across three linguistic corpora, OntoLex lexical-entry semantics across five, CRMtex written-text segments across three, CRM physical-object semantics across four, plus an LRMoo text-version candidate.

**NO-GO for a broad new TFont ontology:** the strongest unresolved gap is apparatus/witness-attestation semantics, and only Pseudepigrapha currently supplies the complete reading-at-locus graph. Keep profile-local/native-only semantics until recurrence or a governed external apparatus profile justifies more.

## Acceptance trace

- [x] all seven required corpora represented;
- [x] extrabiblical retained as high-similarity control;
- [x] raw schema consideration reproducibly measured where R-005 machine inventories exist;
- [x] weighted common-target coverage measured independently: 72/109 = 66.1%;
- [x] all eight assessment categories reported, including zero-count categories and an explicit `unsupported` control;
- [x] six reusable common-target query probes compile across multiple corpora;
- [x] linguistic, lexical, structural/written-text, textological, and heritage cases included;
- [x] apparatus, damage/editorial, archaeology and unsafe verbal-category controls fail closed;
- [x] native-only rows preserved rather than optimized away;
- [x] P-003 schema/IR/runtime requirements identified;
- [x] qualified GO for the pivot and NO-GO for a broad local ontology.

## Review targets

A fresh reviewer should challenge the exact OLiA mappings, lexical-entry identity strength, CRMtex TX7 preconditions, CRM E22 projections, LRMoo F2 use, native-only gap decisions, metric separation, R-016 execution boundary, and every fixture reference against pinned native evidence.
