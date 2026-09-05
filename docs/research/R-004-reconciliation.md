# R-004 reconciliation: evidence-bearing compatibility and empirical-domain documentation

**Status:** normative amendment to `R-004-documentation-architecture.md` for PR #11  
**Recorded:** 2026-09-05  
**Dependencies reconciled:** repaired R-001/#8, R-002/#9, R-003/#10, and repaired R-005/#7 contracts

Where this note conflicts with shorthand in the original R-004 draft, this note supersedes it. Final merge still requires accepted upstream research dependencies and a fresh independent review of the final head.

## 1. Compatibility documentation uses R-001 states

Generated compatibility pages and machine indexes must expose R-001's evidence states, not a generic `compatible`/`stale` boolean:

- `verified-exact`
- `verified-compatible`
- `incompatible`
- `unverified`

For every state the reference should expose enough identifiers to audit the result, at minimum conceptually:

- parent corpus/profile identity;
- exact loaded parent artifact digest;
- exact tested target digest(s), if any;
- profile dependency fingerprint;
- compatibility evidence/report identity when `verified-compatible`;
- failed/missing dependency summary when `incompatible`;
- reason evidence is incomplete when `unverified`.

Generated documentation must not call a profile “compatible” merely because feature names or generic schema metadata match.

## 2. Research candidate strengths and approved mappings are separate documentation objects

R-005's `S/C/B/N/R/U/L` matrix is research evidence. It is not the canonical released mapping source and must not appear on generated production reference pages as though those cells were approved ontology mappings.

Documentation surfaces should distinguish:

1. **research/census evidence** — candidate cross-corpus relationship and its source artifact;
2. **approved profile mapping** — selected external term, TFont assessment (`exact`, `close`, `broader`, `narrower`, `related`, etc.), applicability, rationale, review provenance;
3. **formal publication relation** — optional RDF/OWL/SKOS formalization under the R-002 cross-formalism rules.

A generated mapping page may link to the R-005 candidate evidence used in review, but the production semantic index is built only from approved canonical profile mappings.

## 3. Observed domains must distinguish semantic values from storage-level empties

The repaired R-005 generator demonstrated that dense TF features may expose empty-string records. Documentation generators therefore need separate fields/counts for:

- `node_records_seen` / raw records encountered;
- `nodes_with_value` / actual non-empty semantic values;
- `empty_observation_count` / storage/API empties;
- `observed_values` / non-empty values only.

`""` and `None` must not appear in a generated semantic value table merely because they occur in a dense TF representation, unless the parent corpus explicitly documents the literal itself as semantically meaningful.

Likewise, a feature page must not claim applicability to a node type based only on empty dense records on that type.

## 4. Observed-small-domain is not the same as documented closed vocabulary

Generated empirical census/reference output must use distinct labels for:

- **observed small domain** — every non-empty value seen in the exact pinned artifact fits under the enumeration threshold;
- **documented bounded/categorical vocabulary** — parent corpus documentation/source semantics establishes a bounded category set;
- **open/large domain** — lexical/textual/entity values or large/unbounded inventories;
- **unknown closure** — observed values are enumerable in one release but closure is not established.

The docs must not turn a finite release observation into a stronger ontology/category contract.

CUC provides the concrete regression example. At pinned 0.2.8, generated evidence records non-empty `emen` values `excised`, `missing`, `redundant`, `remark`, `restored`; the fact that these are all observed values in that release is not by itself a promise that future CUC releases can never add another editorial state.

## 5. Mapping-strength documentation follows R-002's two-layer rule

R-004 originally used phrases such as “maps ... with relation `exact`”. Generated reference must make clear whether a displayed relation is:

- TFont `assessment.strength`, used by runtime/query planning; or
- an RDF/OWL/SKOS publication predicate/pattern.

For OWL-class targets such as OLiA or CIDOC CRM, a TFont assessment of `exact` does not automatically imply `owl:equivalentClass` or `skos:exactMatch`.

A mapping detail page should therefore present the fields separately, e.g. conceptually:

```text
TFont assessment: exact
Formal publication: no equivalence axiom asserted
Target: <OLiA class URI>
Rationale: ...
```

For genuine SKOS concepts, an explicit reviewed SKOS mapping predicate may be shown separately.

## 6. Unsupported and non-executable states remain first-class

Generated concept/profile pages must visibly report:

- `native-only`
- `unsupported`
- `ambiguous`
- `unverified`
- `incompatible`
- approximation-required states

An empty cell is not an adequate representation of one of these states.

For a cross-corpus query concept, documentation should make the same negative cases visible that R-003 exposes through structured MCP output. Examples from R-005 include:

- Peshitta 0.2 has no morphology suitable for a BHSA/Syriac `Noun + Feminine + Plural` query;
- ORACC source `c type=sentence` is not an approved BHSA-style linguistic sentence mapping;
- witness-like data in Peshitta, TLHdig-TF, and Pseudepigrapha-TF have different semantics;
- TLHdig `lex.oslots` is a technical anchor, not lexical occurrence extent.

## 7. Provenance block additions

Generated mapping/profile documentation should expose compact provenance for:

- parent artifact identity (`tf_files_sha256` or the final design-equivalent algorithm);
- parent source revision/version;
- profile source digest/version;
- dependency fingerprint;
- ontology lock/snapshot;
- mapping review status;
- generated artifact source digest;
- optional research-evidence references such as R-005 inventory/matrix rows.

The HTML/Markdown view can abbreviate hashes visually but machine JSON must preserve full values.

## 8. CI additions

Extend the original R-004 drift/release contract with these checks:

1. generated semantic value pages contain no storage-level empty value unless explicitly declared meaningful;
2. generated feature applicability is derived from actual non-empty values / approved native contract;
3. `observed_small_domain` and `documented_bounded_domain` are not conflated;
4. compatibility pages use only the four R-001 evidence states;
5. research candidate strengths cannot enter released mapping reference as approved mappings without canonical mapping IDs/review state;
6. TFont assessment and RDF formalization are rendered in separate fields;
7. generated provenance includes parent artifact identity and dependency fingerprint;
8. negative/unsupported states are rendered explicitly rather than as blank cells.

## 9. Review trace

A final independent reviewer of R-004 should check the final generated-documentation contract against accepted R-001 through R-005 and verify especially that:

- exact/reusable compatibility evidence is not reduced to a schema version label;
- observed TF storage artifacts do not become semantic categories;
- R-005 research classifications do not become production mappings automatically;
- R-002 mapping assessment remains distinct from formal RDF/OWL publication;
- negative corpus capabilities remain inspectable by both humans and agents.
