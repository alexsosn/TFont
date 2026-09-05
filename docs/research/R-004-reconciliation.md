# R-004 reconciliation history

**Status:** historical reconciliation record; the canonical R-004 report is authoritative  
**Recorded:** 2026-09-05

This file records why `docs/research/R-004-documentation-architecture.md` was consolidated after R-005, R-001, R-002, and R-003 reached accepted exact-head states. It is not a second normative contract.

## Accepted dependencies

- R-005 reviewed head `48c8bd78d0c3a0501b2fdec6946db5df90517bdb`, merged as `a9c4d74d4de2f9a15eb1464dce341ecd2f92f898`.
- R-001 reviewed head `68b88a820f5519ad65d46b732679a6278e9ca3c9`, merged as `a22a95084a1518882d1e3e87d10e9757121f106d`.
- R-002 reviewed head `d82e6ef2726f149f903eb43ddbfb615faf399cd5`, merged as `a554d4fdc36c8854519064f3a7611b80efa29622`.
- R-003 reviewed head `6747379a4aa68c17c156344f3ed3b0c2cb29d423`, merged as `02abd89b5b7d4c83027e1e8503a02eef23cab91e`.

## Reasons for consolidation

Independent review and final upstream changes exposed these issues in the earlier draft/amendment pair:

1. source authority was represented as numeric precedence even though normative rules, native semantics, ontology semantics, mappings, and compatibility evidence have different authority domains;
2. mapping assessment and RDF/OWL/SKOS publication relation were still conflated in several canonical labels/examples;
3. R-001 evolved from a generic parent-artifact digest to a component-aware parent component manifest and complete dependency-closure contract;
4. `broader`/`narrower` query consequences needed to match accepted R-003 directionality;
5. research candidate evidence, dense TF storage empties, and observed-vs-documented domain closure needed to be first-class drift checks;
6. R-003 established a current-host/current-protocol distinction and protocol-independent semantic identity;
7. the old canonical CI list and amendment additions formed two competing implementation checklists.

The canonical report now contains scoped authority domains, explicit conflict behavior, component-aware compatibility/provenance, assessment/publication separation, host/protocol ownership, and one canonical CI drift/release contract.

Future changes should edit the canonical report. This historical record should change only when the dependency trace or reason for reconciliation itself changes.
