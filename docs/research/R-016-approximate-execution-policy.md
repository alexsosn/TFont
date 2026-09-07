# R-016: approximate semantic execution policy

**Status:** research/prototype complete; pending exact-head CI and fresh logically-independent adversarial review  
**Issue:** #50  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-002/R-003/R-006 and current R-011 pilot evidence

## Decision

Approximate semantic execution must be **explicit, directional, per-mapping authorized, and loss-visible**. TFont must not interpret `semantic_mode=approximate` as “execute every non-exact mapping”.

The first policy is:

| assessment | exact mode | approximate mode | required loss disclosure |
|---|---|---|---|
| `exact` | executable | executable | none |
| `broader` | refuse | executable only when mapping is reviewed as approximation-eligible and caller accepts undercoverage | undercoverage |
| `narrower` | refuse | executable only when mapping is reviewed as approximation-eligible and caller accepts overcoverage | overcoverage |
| `close` | refuse | **informative-only by default**; executable only when a separate reviewed approximation contract states the loss direction and caller accepts it | reviewed `undercoverage`, `overcoverage`, or both |
| `related` | refuse | refuse as substitute constraint | non-substitutive relation |
| `ambiguous` | refuse | refuse | unresolved target choice |
| `native-only` | no common-target reverse execution | no common-target reverse execution | no shared target |
| `unsupported` | refuse | refuse | unsupported |

The governing invariant is:

> **Mapping assessment describes semantic relation; execution authorization is a separate reviewed decision. Approximate mode relaxes policy only where both the mapping and the caller explicitly permit the known loss shape.**

## 1. Direction semantics

TFont assessment direction is always:

```text
native/source concept -> requested external/common target
```

Therefore:

### `broader`

The **external target is broader** than the native concept.

Executing the native selector returns a subset of the requested target:

```text
native ⊂ target
```

Result: **undercoverage** / false negatives relative to the common request, but no false positives from this mapping relation alone.

### `narrower`

The **external target is narrower** than the native concept.

Executing the native selector returns a superset of the requested target:

```text
target ⊂ native
```

Result: **overcoverage** / false positives relative to the common request.

### `close`

`close` means substantial semantic overlap without coextensiveness. The direction of set difference is not guaranteed by the assessment itself.

Therefore the assessment alone cannot authorize execution. A separate reviewed approximation contract must state one of:

- `undercoverage`;
- `overcoverage`;
- `bidirectional` (both false negatives and false positives possible).

If the reviewer cannot justify one of these loss shapes for the exact native selector and common target, the mapping remains **informative-only even in approximate mode**.

## 2. Separate approximation authorization

A non-exact mapping may conceptually carry:

```json
{
  "assessment": "broader",
  "approximation": {
    "status": "reviewed",
    "eligible": true,
    "losses": ["undercoverage"],
    "rationale": "...",
    "review_id": "..."
  }
}
```

P-003 owns final schema names. R-016 requires the semantic separation only.

For `broader` and `narrower`, the assessment supplies the direction, but execution eligibility is still reviewable independently. A mapping can remain informative-only if its native selector is unstable, operationally incomplete, depends on unavailable side data, or otherwise cannot serve as a defensible query approximation.

For `close`, a reviewed loss contract is mandatory; `close + approximate mode` alone is never enough.

## 3. Caller authorization

Approximate execution requires both:

1. mapping-level reviewed eligibility; and
2. request-level acceptance of the actual losses.

Conceptually:

```json
{
  "semantic_mode": "approximate",
  "accept_losses": ["undercoverage"]
}
```

Examples:

- caller accepts only undercoverage -> a reviewed `broader` mapping may execute; `narrower` may not;
- caller accepts only overcoverage -> reviewed `narrower` may execute; `broader` may not;
- caller accepts both -> either directional mapping may execute; a reviewed `close` with `bidirectional` loss may also execute;
- caller says only `approximate` but does not accept concrete losses -> no non-exact constraint executes.

This prevents one vague flag from silently changing query semantics.

## 4. Loss records

Every approximate semantic atom that compiles into a native constraint emits an agent-visible loss record.

Minimum shape:

```json
{
  "mapping_id": "...",
  "assessment": "broader",
  "requested_target": "...",
  "native_selector": "...",
  "losses": ["undercoverage"],
  "effect": "native selector may miss members of requested target",
  "authorization": {
    "mapping_review": "...",
    "caller_accepted": ["undercoverage"]
  }
}
```

Loss records are part of the resolution fingerprint/provenance and survive into search results.

## 5. Conjunctions

For conjunctions, each semantic atom resolves independently. The plan is executable only if **every required atom** is executable under the requested mode.

Aggregate loss is the union of atom losses:

- exact + exact -> exact;
- exact + undercoverage -> undercoverage;
- exact + overcoverage -> overcoverage;
- undercoverage + undercoverage -> undercoverage;
- overcoverage + overcoverage -> overcoverage;
- undercoverage + overcoverage -> bidirectional;
- any executable bidirectional close + anything -> bidirectional;
- one non-executable required atom -> whole conjunction non-executable by default.

No required semantic atom is silently dropped.

This follows R-003's fail-closed conjunction rule.

## 6. Multi-corpus requests

Each corpus gets an independent plan and loss summary.

Example:

```text
request: shared concept X

Corpus A -> exact       -> executable, no semantic loss
Corpus B -> broader     -> executable only with undercoverage acceptance
Corpus C -> narrower    -> executable only with overcoverage acceptance
Corpus D -> close       -> informative-only unless reviewed close-loss contract exists
```

The API must not label those result sets “equivalent cross-corpus results”.

Agent comparison state should distinguish:

- `exactly-comparable` — all participating executed plans are exact for requested atoms;
- `approximately-comparable` — all executed plans are authorized but one or more have disclosed losses;
- `heterogeneous-loss` — executed corpora have different loss shapes;
- `partial/non-executable` — one or more required corpus plans cannot execute.

Cross-corpus aggregate counts/statistics should be exact-only by default. Approximate aggregate comparison requires an explicit caller opt-in and preserves per-corpus loss annotations.

## 7. Representative corpus cases

### 7.1 Exact linguistic controls

R-011's reviewed OLiA cases such as noun/plural/first-person across BHSA, Syriac and ExtraBiblical remain exact controls. Approximate mode must not alter their native plans or mark them lossy.

### 7.2 CRMtex line candidates

R-011 uses `close` candidates for some native line objects to CRMtex `TX7 Written Text Segment` when the physical-written-text semantics fit.

R-016 conclusion: those `close` rows are **not executable merely because R-011 can compile a native selector**. They require a reviewed approximation contract that states what mismatch remains between the native line object and TX7. Until that contract exists, they are plan-research candidates / informative-only.

### 7.3 Lexical-entry candidates

Feature-keyed or converter-derived lexical identities may be `close` to OntoLex `LexicalEntry`. Again, close mapping strength does not authorize a lookup as an OntoLex-equivalent entry query. A reviewed identity/coverage contract must state the approximation loss before common-target execution.

### 7.4 Structural/textological controls

Physical carrier vs written segment, textual witness vs physical manuscript, and edition record vs tablet are not “approximate enough” merely because they are related. Where the native selector changes semantic object kind, the mapping should normally be `related`, `ambiguous`, or native-only rather than abusing approximate execution.

R-016 must not rescue an invalid mapping-strength decision.

## 8. Informative-only cases

Even in approximate mode, these never compile as substitute constraints by default:

### `related`

A related concept is not a subset/superset/near-equivalent constraint. It may appear in explanation/discovery but not execute for the requested target.

### `ambiguous`

No unique target is justified. Approximate mode does not choose among candidates.

### `native-only`

There is no shared target for reverse semantic resolution.

### `unsupported`

No usable semantic representation exists.

### unreviewed `close`

Substantial overlap without a reviewed loss contract is insufficient.

## 9. Ontology hierarchy is not execution policy

The resolver must not turn ontology reasoning into runtime widening/narrowing authorization.

Forbidden examples:

- requested superclass -> search for any native mapping to an ontology subclass and execute it automatically;
- requested SKOS broader concept -> follow `broader` links until a mapped concept is found;
- requested class -> substitute a sibling/related class because labels are similar;
- derive `broader`/`narrower` execution from ontology graph edges when the TFont mapping assessment was not reviewed for that native concept.

Ontology structure can assist mapping research, validation and documentation. Runtime execution uses explicit reviewed mappings plus explicit approximation policy only.

## 10. Query/result ergonomics

Compact `semantic_resolve` output for an approximate atom should expose:

- assessment;
- execution status;
- native plan;
- loss direction(s);
- whether mapping authorization exists;
- whether caller accepted each loss;
- refusal reason if informative-only.

Full explanation adds rationale/evidence/review identity and any corpus-specific caveats.

A model should be able to answer “why did corpus B return fewer kinds of things than corpus A?” from the plan itself, not from hidden policy.

## 11. Prototype policy model

The research prototype uses:

```text
assessment
mapping_approximation_eligible
reviewed_loss_set
request semantic_mode
request accepted_loss_set
```

Resolution output is one of:

- `executable-exact`;
- `executable-approximate`;
- `informative-only`;
- `unsupported` / other explicit refusal reason.

The prototype does not generate Text-Fabric syntax. It evaluates execution policy against already-reviewed native plan fragments.

## 12. Required contract tests

1. exact executes in exact mode;
2. broader refuses in exact mode;
3. broader executes only with reviewed eligibility + accepted undercoverage;
4. narrower executes only with reviewed eligibility + accepted overcoverage;
5. close without reviewed loss contract is informative-only in approximate mode;
6. close with reviewed undercoverage contract can execute only if caller accepts undercoverage;
7. close with bidirectional loss requires acceptance of both under- and overcoverage;
8. related never substitutes;
9. ambiguous never auto-selects;
10. native-only has no common reverse execution;
11. unsupported refuses;
12. exact + broader conjunction reports undercoverage;
13. broader + narrower conjunction reports bidirectional loss;
14. one refused required atom blocks whole conjunction;
15. two corpora with different loss shapes report heterogeneous-loss;
16. approximate cross-corpus aggregate comparison is disabled by default;
17. approximate aggregate comparison requires explicit opt-in;
18. ontology hierarchy metadata cannot make an unreviewed mapping executable;
19. compile-able native plan fragment alone cannot make `close` executable;
20. mapping loss authorization must be content/review-bound in later P-003 schema.

## 13. P-003 inputs

P-003 must preserve separate fields/concepts for:

- mapping assessment;
- approximation eligibility/review;
- reviewed loss direction(s);
- request semantic mode;
- caller-accepted loss direction(s);
- atom execution status;
- aggregate conjunction loss;
- per-corpus comparison state;
- exact native plan fragment;
- explanation/provenance.

Do not encode approximate policy as a single boolean on the request or mapping.

## 14. Non-goals

R-016 does not:

- change mapping assessments;
- automatically infer mappings from ontology hierarchy;
- define production API field names;
- execute Context-Fabric queries;
- authorize invalid object-kind substitutions;
- make approximate results statistically equivalent across corpora;
- define external authority-reference semantics (R-017).

## 15. Acceptance trace

- [x] executable/non-executable rules defined for every non-exact assessment;
- [x] direction-specific under/over/bidirectional loss semantics defined;
- [x] close mapping separated from close execution authorization;
- [x] representative linguistic/lexical/written-text/textology cases included;
- [x] conjunction loss composition defined;
- [x] multi-corpus comparison semantics defined;
- [x] related/ambiguous/native-only/unsupported negative controls preserved;
- [x] ontology hierarchy kept separate from runtime authorization;
- [x] concrete prototype/test contract supplied for P-003.

## Review targets

A fresh logically-independent reviewer should challenge especially:

1. whether `broader`/`narrower` direction is interpreted correctly from R-002's native->external convention;
2. whether broader/narrower should ever execute without an additional mapping eligibility review;
3. whether close should be more permissive or even more restrictive;
4. whether the caller-loss acceptance contract is ergonomic but still fail-closed;
5. whether conjunction loss union is semantically sound;
6. whether approximate multi-corpus comparison should permit aggregate statistics at all;
7. whether any representative corpus case accidentally treats a mapping-strength defect as an approximation problem;
8. whether the prototype tests cover all refusal paths.