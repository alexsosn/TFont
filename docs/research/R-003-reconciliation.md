# R-003 reconciliation: compatibility evidence and census-strength boundary

**Status:** normative amendment to `R-003-ergonomics.md` for PR #10  
**Recorded:** 2026-09-05  
**Dependencies reconciled:** repaired R-001/#8 and repaired R-005/#7 research contracts

Where this note conflicts with shorthand/examples in the original R-003 draft, this note supersedes them. Final merge still requires accepted R-005 and a fresh independent review of the final R-003 head.

## 1. Compatibility states use the R-001 evidence model

The generic example value `compatibility: "verified"` in the original R-003 draft is too weak. Semantic capability/resolution responses must use R-001's evidence-bearing states:

- `verified-exact` — loaded parent TF semantic bytes match an exact tested parent-artifact identity;
- `verified-compatible` — parent bytes differ from exact targets but the profile's complete declared dependency closure has been validated;
- `incompatible` — at least one required dependency fails validation;
- `unverified` — exact identity and complete compatibility have not been established.

Only the first two states are executable in the normal semantic API.

`unverified` is diagnostic and planning-only. The ordinary `semantic_search` path must not expose an `allow_unverified` escape hatch.

A capability response therefore needs both the evidence state and, compactly, the identities that produced it:

```json
{
  "profile": "tfont-bhsa@0.1.0",
  "compatibility": "verified-exact",
  "parent_artifact": "sha256:...",
  "dependency_fingerprint": "sha256:..."
}
```

The exact field names remain a design decision.

## 2. R-005 `S` is not a runtime `exact` mapping

R-005 now classifies every cross-corpus apparent match with research-stage codes `S/C/B/N/R/U/L`.

`S` means that the row-level comparison is defensibly the same concept at the deliberately stated abstraction level. It does **not** mean that:

- a particular ontology term has been selected;
- an OWL equivalence claim is licensed;
- a TFont canonical mapping assertion has passed term-level review;
- the resolver may report runtime `exact` merely because the census cell is `S`.

The runtime statuses in R-003 (`exact`, `close`, `broader`, `narrower`, `related`, etc.) apply only to an **approved profile mapping assertion** after ontology-term selection under R-002 and mapping review.

Therefore the pipeline is:

```text
R-005 candidate relationship
        ↓ research/design evidence
R-002 ontology-term selection + relation policy
        ↓ reviewed canonical profile mapping
R-003 runtime resolution status
```

No compiler is permitted to convert `S` to `exact` automatically.

## 3. Empty TF records are absence of a feature value, not a semantic category

The repaired R-005 empirical generator found that dense TF feature data can expose empty-string records. TFont must preserve the distinction between:

- a node having a non-empty native feature value;
- a dense storage/API record containing `""`/no semantic value;
- an explicit source assertion such as textual omission, witness non-attestation, damage, or uncertainty.

Consequences for semantic ergonomics:

1. capability/domain reports must not list `""` or `None` as semantic categories unless a particular source explicitly defines such a literal as meaningful;
2. a feature must not be advertised as applicable to a node type solely because dense empty records occur on that node type;
3. `semantic_resolve` cannot turn an empty native value into `Absent`, `Unknown`, `Omitted`, `Unattested`, or another ontology concept without an explicit reviewed mapping;
4. coverage metrics distinguish `nodes_with_value` from storage/API records encountered;
5. full explanation may report the storage-level empty-record count for diagnostics, but it is not part of the semantic value inventory.

This strengthens the original R-003 rule that “no value” must not become “explicit absence.”

## 4. Candidate and approved relation vocabularies stay visibly distinct

Human and agent output should distinguish provenance stages rather than presenting every relation word as one namespace.

Conceptually:

```json
{
  "research_candidate": {
    "relation": "same",
    "source": "R-005"
  },
  "approved_mapping": {
    "term": "http://...",
    "relation": "exact",
    "mapping_id": "...",
    "reviewed": true
  }
}
```

Normal released semantic execution uses only `approved_mapping`. Research-candidate data may be exposed in developer/review tooling but must not make a profile executable.

## 5. Updated failure behavior

In addition to the original R-003 error model:

- a profile whose exact parent digest differs but whose dependency closure has not been validated is `unverified`, not merely “stale”;
- a profile may be `verified-compatible` even when the exact parent digest differs, but only after validating every native dependency used by the profile, including mapped values in open domains and structural invariants;
- an empty TF value encountered while resolving a required native constraint counts as “constraint not satisfied/no native assertion”, not as an ontology value;
- a mapping compiled from research-candidate strength without approved mapping review is an internal/profile validation defect and must not activate.

## 6. TDD additions for the later implementation

Add these contract tests to the forty criteria in the original R-003 report:

41. `verified-exact` activates when parent artifact identity exactly matches a tested target.
42. A different parent artifact cannot become executable merely because feature names/metadata match; complete dependency validation is required for `verified-compatible`.
43. `unverified` profiles can be inspected but cannot be passed to normal semantic execution.
44. A research-stage R-005 `S` classification alone cannot compile into an executable `exact` mapping.
45. Empty-string/`None` dense TF records are excluded from semantic capability domains.
46. Empty dense records do not expand a feature's advertised applicable node types.
47. Empty native values cannot satisfy an explicit absence/omission/non-attestation semantic constraint without a reviewed source assertion.
48. Capability/coverage output can report raw empty-record counts diagnostically without counting them as mapped semantic values.

## 7. Review trace

A final independent reviewer of R-003 should verify:

- exact wording/behavior against the accepted R-001 compatibility amendment;
- that the accepted R-005 candidate-strength matrix is treated as research evidence rather than production mapping data;
- that dense TF empty records remain non-semantic;
- that no example or tool schema retains generic executable `verified` behavior;
- that the combined R-003 contract remains fail closed.
