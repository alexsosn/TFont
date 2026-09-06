# P-001 common-ontology roadmap amendment

**Status:** architecture guardrail pending independent review  
**Recorded:** 2026-09-06  
**Tracks:** P-003 #44; research #38–#43  
**Scope:** roadmap correction only; this document does not itself change production schemas or runtime contracts

## 1. Finding

The accepted foundation research did not lose the original TFont objective. R-002 selected a common open semantic basis centered on **SKOS, OLiA, OntoLex-Lemon, CIDOC CRM, CRMtex, LRMoo, and CRMinf**, with optional domain profiles and external controlled vocabularies. R-003 likewise defined agent-facing cross-corpus semantic resolution as a primary use case.

The loss occurred during reconciliation into P-001. P-001 correctly designed artifact integrity, ontology locking, evidence/review provenance, parent-corpus compatibility, deterministic compilation, and fail-closed runtime behavior, but reduced the semantic target model to a generic `external_target` plus `ontology_lock`. The implemented v1 schemas inherit that abstraction. They can establish that a reviewed URI is pinned; they do not establish that mappings from different corpora converge on a shared semantic profile that an agent can use as a compatibility pivot.

The first POC acceptance fixture also became too narrow: a BHSA morphology mapping plus infrastructure/negative cases does not prove cross-corpus ontology-mediated interoperability.

## 2. Status of P-001

P-001 remains the accepted historical source for the infrastructure invariants already implemented or in progress, including:

- native-corpus authority and explicit mapping assessments;
- parent component identity and compatibility states;
- deterministic canonicalization/digests;
- ontology snapshots/locks and offline reproducibility;
- content-addressed evidence and independent review bindings;
- fail-closed validation and runtime behavior;
- separation between runtime mapping assessment and RDF/OWL/SKOS publication relation;
- thin native Context-Fabric execution rather than a mandatory RDF/triplestore runtime.

P-001 must **not** be treated as the final authority for the semantic target shape, semantic-profile/capability model, normalized semantic IR, or agent resolver contract. Those areas are reopened by P-003 #44 after R-006 through R-011.

## 3. Restored product invariant

A released executable TFont mapping is intended to be a **semantic compatibility adapter** between a native Text-Fabric/Context-Fabric corpus and a reviewed common open ontology layer.

An arbitrary external URI, even when pinned and reviewed, is insufficient by itself. The mapping architecture must make it possible to answer both directions deterministically:

```text
native corpus feature/node/edge/value
    -> reviewed shared semantic concept/relation(s)

shared semantic concept/relation
    -> supported native selector/path/query constraint per corpus
```

The agent-facing objective is:

```text
corpus-neutral semantic request
    -> common ontology concept/relation
    -> per-corpus reviewed mapping
    -> native Context-Fabric query plan
    -> results with mapping/provenance explanation
```

No execution path may infer equivalence from labels, similar feature names, or ontology hierarchy alone.

## 4. Common semantic basis to preserve during reconsideration

R-006 starts from the accepted R-002 basis rather than performing an unconstrained ontology search:

| role | accepted foundation model |
|---|---|
| concept schemes and mapping vocabulary | SKOS — Simple Knowledge Organization System |
| linguistic annotation | OLiA — Ontologies of Linguistic Annotation |
| lexical entries/forms/senses/concepts | OntoLex-Lemon |
| cultural objects/events/provenance | CIDOC CRM — CIDOC Conceptual Reference Model |
| written text on physical artefacts | CRMtex — CIDOC CRM extension for textual entities |
| works/expressions/manifestations/items and transmission | LRMoo — IFLA Library Reference Model, object-oriented formulation |
| scholarly inference/argumentation | CRMinf — CIDOC CRM extension for inference and argumentation |

Optional or domain-specific profiles remain subject to the accepted R-002 governance and new domain research: CRMarchaeo, CRMsci, LexInfo, OntoLex Lexicog, OntoLex VarTrans, Getty AAT, PeriodO, and other candidates only where evidence justifies them.

A research ticket may recommend changing this basis, but only from authoritative ontology/corpus evidence and with an explicit migration consequence. The genericity of P-001 is not evidence for replacing the accepted basis.

## 5. Research gates before the replacement design

The semantic architecture is decomposed into independently reviewable research tickets:

- **R-006 #38** — reconcile the seven-model common basis into an executable semantic pivot and determine typed/composable ontology projections;
- **R-007 #39** — determine common structural semantics for TF nodes, slots, features, valued/unvalued edges, direction, discontinuity and sidecars; evaluate POWLA and the need for a tiny structural vocabulary;
- **R-008 #40** — define OntoLex/SKOS lexical-semantic and dictionary interoperability, preserving lexeme/lemma/gloss/sense/concept distinctions;
- **R-009 #41** — define codicology, textual transmission, critical-apparatus and scholarly-inference mappings using CRM/CRMtex/LRMoo/CRMinf and relevant prior art;
- **R-010 #42** — define archaeology/material-culture/provenance/period mappings using CRM, CRMarchaeo, CRMsci, AAT and PeriodO where warranted;
- **R-011 #43** — build non-production ontology-mapped pilot profiles across heterogeneous corpora, measure coverage/mapping strength, and demonstrate corpus-neutral query-plan compilation.

These tickets may run in parallel where their evidence is independent. R-011 integrates their reviewed conclusions.

## 6. Replacement design gate

**P-003 #44** is the next authority for semantic target/profile/IR/resolver architecture. It must reconcile R-006–R-011 with R-001–R-005 and with the production infrastructure already merged under I-001/I-002/I-003.

At minimum P-003 must decide:

- typed ontology target/projection roles rather than opaque URI-only semantics;
- whether one native concept can carry multiple complementary ontology projections;
- controlled semantic profiles/capabilities in place of or in addition to free-form `semantic_domains`;
- bidirectional native-to-semantic and semantic-to-native indexes in normalized IR/runtime artifacts;
- common-concept -> multi-corpus native query-plan resolution;
- exact/approximate/ambiguous/unsupported execution gates;
- migration/versioning of v1 mapping/profile schemas and semantic digests;
- the smallest necessary TFont-local vocabulary for recurrent gaps, if empirical research demonstrates one.

## 7. Immediate implementation guardrail

Until P-003 is accepted:

- existing I-001/I-002/I-003 infrastructure remains valid unless P-003 explicitly versions/amends it;
- P-002 #37 may continue only on forward-compatible selector/dependency/review/evidence/namespace mechanics and must not cement the one-target model;
- I-004 #36 may research generic validator mechanics, but semantic-contract implementation/merge is blocked by P-003;
- no new semantic compiler, resolver, corpus-profile, or MCP integration ticket should derive its semantic model from P-001's single `external_target` representation alone;
- no final corpus mapping should be released until the common-pivot contract is accepted and exercised across heterogeneous corpora.

## 8. Revised POC success criterion

The first meaningful semantic POC must prove an end-to-end vertical slice:

```text
one reviewed common ontology concept/relation
    -> mappings in at least two independent corpora
    -> native Context-Fabric query plans
    -> executable or explicitly non-executable resolution
    -> result/explanation containing mapping strength and provenance
```

The broader POC acceptance suite must include multiple semantic domains and at least BHSA, CUC, one ETCBC Syriac corpus, Pseudepigrapha-TF, ORACC-TF, and TLHdig-TF, as required by P-003/R-011.

Infrastructure correctness remains necessary, but it is not evidence of semantic interoperability by itself.

## 9. Development loop

Every new research/design/implementation PR created from this roadmap follows the repository loop:

```text
research -> plan/design -> RED contract tests -> minimal implementation
         -> focused/full CI -> fresh logically-independent adversarial review
```

Research-only tickets stop after reviewed research. P-003 stops after reviewed design. Production work is decomposed only after P-003 has made the relevant semantic contract explicit.
