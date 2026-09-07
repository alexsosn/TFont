# R-015: ontology-bundle composition and bridge-lock provenance semantics

**Status:** research/prototype complete; revised after multiple exact-head adversarial reviews; pending final logically-independent review  
**Issue:** #49  
**Recorded:** 2026-09-07  
**Depends on:** accepted P-001/R-002/R-006/R-010/R-012 and merged R-011/R-013/R-014

## Decision

TFont semantic composition must be a **content-addressed active bundle** of independently locked ontology releases plus explicit, term-scoped, evidence-bound, reviewed bridge artifacts. It is not one OWL import closure and not a bag of live namespace URLs.

The active bundle identity is derived from:

```text
unique active profile-contract IDs
+ exact participating ontology-lock identities
+ reviewed bridge artifacts referenced by active dependency edges
+ active dependency bindings
    ↓ explicit semantic projection
canonical JSON / UTF-8 / stable set ordering
    ↓
SHA-256 bundle identity
```

P-001 ontology locks remain authoritative for individual ontology snapshots. R-015 adds only the **composition layer**: which exact locks and bridges participate together, which dependency each bridge satisfies, and which active profile contract requires that composition.

The main fail-closed invariant is:

> **A dependency is executable in the R-015 exact reference gate only when the active consumer lock exists, the required dependency identity is exact, and that requirement is satisfied either by the exact required lock digest or by one content-valid, evidence-bound, reviewed, explicitly compatible bridge whose source lock and term scope exactly match the dependency edge and whose declared runtime strength is `exact`.**

Inactive optional-profile diagnostics do not contribute active dependency edges or bridge locks to the bundle identity. R-016 owns any later mode-aware authorization for approximate/related bridge strengths.

## 1. Why individual ontology locks are insufficient

P-001 already pins an individual ontology release/snapshot with identity such as ontology/release/source/content digest/snapshot metadata and terms used. That is sufficient for one model in isolation.

A TFont semantic profile, however, may use several standards whose published dependency releases differ. The composition contract must additionally answer:

1. which exact ontology-lock identities participate;
2. which active term-level dependency edges are required;
3. whether an edge is satisfied by an exact locked release or a reviewed bridge;
4. whether a bridge is bound to the exact source/target lock digests and exact term scope;
5. which immutable evidence identity/digest supports the bridge;
6. which review identity/reviewer/date approved the exact bridge content;
7. what runtime strength and explicit limitations the bridge declares;
8. whether editing bridge semantic content invalidated the content digest or review binding;
9. whether an optional profile is actually active;
10. whether the resulting active closure has one deterministic semantic identity.

## 2. Authoritative version-skew evidence

### CRMtex 2.0

CRMtex 2.0 declares dependencies on:

- CIDOC CRM 7.1.2;
- CRMinf 0.7(b);
- CRMsci 2.0;
- FRBRoo 2.4.

Primary declaration: <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>.

The accepted current TFont basis otherwise uses current releases including CIDOC CRM 7.1.3, LRMoo 1.1.1 and CRMinf 1.2.1. R-012 established that TFont must not silently reinterpret CRMtex 2.0 through current axioms. Only independently reviewed term-scoped continuity bridges may cross that release boundary.

### LRMoo 1.1.1 and CRMinf 1.2.1

Current LRMoo 1.1.1 and CRMinf 1.2.1 use CIDOC CRM 7.1.3 as their current CRM basis.

Primary declarations:

- <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>

This current shared basis does not retroactively modernize CRMtex 2.0's historical dependency closure.

### CRMarchaeo 2.1.1

Stable CRMarchaeo 2.1.1 references CIDOC CRM 7.1.2 and CRMsci 2.0, while the accepted current TFont stack uses CIDOC CRM 7.1.3 and CRMsci 3.2 for current heritage/scientific composition.

Primary release/declaration source: <https://cidoc-crm.org/node/8943>.

This independently confirms that TFont cannot assume one globally current CIDOC-family import closure.

## 3. Three distinct identities

### 3.1 Ontology lock identity

One P-001-pinned ontology snapshot. R-015 references it by stable lock ID plus content digest; it does not duplicate the ontology payload.

Conceptual reference:

```json
{
  "lock_id": "crmtex-2.0",
  "digest": "sha256:..."
}
```

Every participating ontology reference must have a non-empty content digest. Duplicate lock IDs are schema-invalid.

### 3.2 Bridge artifact identity

A bridge is one explicit cross-release semantic assertion. It must bind:

- exact source lock ID + digest;
- exact target lock ID + digest;
- explicit term scope;
- controlled relation/assertion identity;
- explicit compatibility result;
- stable evidence identity + content digest;
- explicit runtime strength + non-empty limitations;
- bridge semantic-content digest;
- review status;
- stable review record ID;
- reviewer identity;
- timezone-aware review timestamp;
- the exact bridge-content digest that was reviewed.

The research prototype requires scope equivalent to:

```json
{
  "source_term": "...",
  "target_term": "...",
  "relation": "reviewed-continuity"
}
```

Empty, scalar, or opaque ontology-wide bridge scope is invalid. This preserves the R-012 rule that one valid F28 continuity bridge never upgrades an entire old ontology to “compatible with current”.

Bridge semantic content is content-addressed separately from review wrapper metadata. The reference prototype digests canonical semantic fields including source/target lock identities, term scope, compatibility, evidence identity/digest, runtime strength and runtime limitations. A changed endpoint/scope/compatibility/evidence/runtime semantic field with an old bridge digest is invalid input. A newly computed bridge digest with an old `reviewed_content_digest` is non-executable until reviewed again.

Review identity is operationally identity-bearing at bundle level: `review_id`, `reviewer_id`, `reviewed_at`, review state and reviewed-content binding participate in the bundle projection. Human-readable reviewer display names or free-form review notes do not.

Runtime-strength vocabulary in the non-production prototype is deliberately small:

- `exact` — may satisfy the R-015 exact reference gate;
- `approximate` — recorded but not exact-executable here;
- `related` — discovery/composition information only in this gate;
- `composition-only` — sequencing/composition relation, not substitute execution.

Unknown runtime strength is schema-invalid. R-016 owns any future authorization rules for the non-exact strengths.

Duplicate bridge IDs are schema-invalid.

### 3.3 Bundle identity

The bundle identifies the exact active semantic composition used for capability inspection/resolution. It references ontology locks and reviewed bridge artifacts; it does not copy ontology graphs into one synthetic import closure.

## 4. Canonical semantic projection

The bundle digest is computed from an explicit allow-list projection, not from a deep copy of arbitrary JSON.

Identity-bearing fields include:

- `schema_version`;
- unique profile contract IDs;
- ontology lock `{lock_id, digest}` references;
- bridge semantic identity/content digest;
- bridge review state/binding and stable review identity/date;
- **active** dependency-edge binding fields.

Nested presentation metadata such as retrieval timestamps, reviewer display names, licence notes, free-form review notes and display labels do not affect semantic bundle identity. Stable review identity/date do affect it because they are part of the operational authorization provenance.

Set-like collections are canonicalized deterministically. Duplicate semantic IDs are rejected rather than silently overwritten or double-counted.

Inactive dependency edges may remain in diagnostic input, but are excluded from the active semantic projection. Activating such an edge changes bundle identity.

Every bridge lock included in the active bundle must be referenced by at least one active dependency edge. An unreferenced bridge or a bridge referenced only by an inactive edge is not active-bundle content and is rejected by the reference validator.

Ontology locks are the already-selected active lock set supplied by the bundle builder; registry-only known ontologies remain outside the bundle.

## 5. Dependency-edge contract

An active dependency edge has conceptual fields such as:

```json
{
  "id": "crmtex-f28-dependency",
  "consumer": "crmtex-2.0",
  "requires": "frbroo-2.4",
  "satisfied_by": "bridge:crmtex-f28-lrmoo",
  "required_bridge_scope": {
    "source_term": "frbroo-2.4:F28",
    "target_term": "lrmoo-1.1.1:F28",
    "relation": "reviewed-continuity"
  },
  "active": true
}
```

The edge is not merely descriptive metadata. The reference validator enforces graph binding:

- `consumer` must identify a participating ontology lock;
- for `lock:<id>`, `edge.requires` must equal that lock ID and `required_lock_digest` must be explicit and match;
- for `bridge:<id>`, `bridge.source_lock_id` must equal `edge.requires`;
- edge `required_bridge_scope` must exactly match the bridge's validated term scope;
- bridge source and target lock digests must match participating ontology locks;
- evidence ID/digest and review ID/reviewer/date must be present and valid;
- bridge review must be `reviewed` and bound to the current bridge content digest;
- bridge compatibility must be explicitly `compatible`;
- bridge runtime strength must be `exact` to satisfy this exact-mode reference gate.

Unknown/missing compatibility never defaults to success. A known non-exact bridge strength produces a non-executable diagnostic rather than silent promotion to exact.

## 6. Fail-closed outcomes

The research contract distinguishes dependency diagnostics equivalent to:

- `satisfied-exact-lock`;
- `satisfied-reviewed-bridge`;
- `inactive`;
- `missing-consumer-lock`;
- `missing-lock`;
- `dependency-lock-mismatch`;
- `unbound-exact-lock`;
- `missing-bridge`;
- `bridge-requires-mismatch`;
- `bridge-scope-mismatch`;
- `stale-bridge`;
- `unreviewed-bridge`;
- `incompatible-bridge`;
- `unknown-bridge-compatibility`;
- `non-exact-bridge-strength`.

Malformed bridge scope, duplicate IDs, missing content/evidence/review/runtime fields, invalid review timestamps, unknown runtime strength, unreferenced bridge locks, and bridge semantic-content digest mismatch are schema/identity errors and therefore non-executable before dependency evaluation.

Aggregate exact-mode bundle execution is allowed only when every active dependency is satisfied by an exact lock or exact-strength reviewed compatible bridge and the ordinary parent/profile compatibility gates also pass.

## 7. Optional-profile semantics

Mandatory distinction:

```text
profile absent/inactive
    !=
profile active but dependency unresolved
```

Example:

- no archaeology capability in a corpus → no active CRMarchaeo dependency/bridge in the bundle → profile `absent`, no bridge warning;
- future corpus activates a CRMarchaeo mapping → its required locks/dependency edges enter the active bundle;
- required cross-release bridge missing/stale/unreviewed/incompatible/non-exact for requested exact mode → profile `unavailable` / query non-executable with explicit dependency diagnostic.

Inactive diagnostic edges do not affect bundle identity. Bridge locks used only by inactive edges are not valid active-bundle content.

## 8. Composition examples

### 8.1 OLiA + OntoLex + SKOS

A linguistic+lexical profile may include separate OLiA, OntoLex and SKOS locks. Multiple ontology locks alone do not imply a bridge. If no cross-release bridge is required for the reviewed mappings, the bundle contains zero bridge locks.

### 8.2 CIDOC CRM + LRMoo + CRMinf

A current textological composition may use CRM 7.1.3, LRMoo 1.1.1 and CRMinf 1.2.1. The exact lock set still participates in bundle identity even when no bridge is required.

### 8.3 CRMtex 2.0

A CRMtex mapping that uses only semantics that do not cross the R-012 bridge surface keeps CRMtex's version-faithful dependency basis.

When a query activates a reviewed bridge-covered term such as the officially retained FRBRoo 2.4 F28 → LRMoo 1.1.1 F28 continuity case, that exact bridge and edge scope enter the active bundle and resolution provenance. The bridge records the migration-table evidence digest, review identity, exact runtime strength and term-scoped limitation; no ontology-wide FRBRoo/LRMoo equivalence follows.

No old/new hierarchy union reasoning is implied.

### 8.4 CRMarchaeo 2.1.1

A corpus without archaeology capability has no CRMarchaeo active dependency.

A future archaeology profile must respect CRMarchaeo 2.1.1's declared CRM 7.1.2/CRMsci 2.0 basis. If composed with current CRM/CRMsci semantics, every needed cross-release bridge must be explicit, term-scoped, content-addressed, evidence-bound and reviewed.

## 9. Migration and identity behavior

### Participating ontology update

Changing a participating ontology lock digest changes bundle identity. Bridges pinned to the old endpoint digest become stale until replaced/reviewed.

### Bridge semantic edit

Changing bridge endpoint/scope/compatibility/evidence/runtime semantic content changes the bridge content digest and therefore bundle identity. Existing review binding no longer authorizes the changed bridge.

### Review-state or review-identity change

Bridge review state/binding and stable `review_id`/`reviewer_id`/`reviewed_at` participate in the bundle semantic/operational projection. A draft/unreviewed bridge cannot satisfy an active edge. Human-readable reviewer display metadata remains presentation-only.

### Inactive/registry-only update

Updating a known ontology or optional-profile artifact that is not part of the active bundle does not change the active bundle identity.

## 10. Agent-facing provenance

### `semantic_capabilities`

Compact output should expose at least:

- profile ID/contract version;
- bundle digest;
- active ontology lock IDs/releases;
- number/aggregate state of active bridges;
- aggregate runtime-strength state relevant to requested mode;
- profile operational state;
- no full bridge dump by default.

### `semantic_resolve`

Per-corpus plan should expose:

- bundle digest;
- mapping/projection IDs;
- required ontology locks;
- bridge IDs actually traversed for requested semantic atoms;
- runtime strength of traversed bridges;
- unresolved dependency state/reason;
- execution allowed/denied.

### Full explanation

Add source/target lock digests, bridge scope, content digest, reviewed-content digest, evidence ID/digest, review ID/reviewer ID/review timestamp, runtime strength/limitations and dependency path.

Pagination/results must not silently switch bundle identity.

## 11. P-001 retained vs P-003 amendment

### Retain P-001

- individual ontology snapshot locks;
- content digests;
- deterministic canonicalization rules;
- source/snapshot provenance;
- fail-closed parent compatibility discipline.

### P-003 must add

- first-class semantic-bundle identity;
- multiple ontology-lock references per active mapping/profile set;
- explicit bridge artifacts and content digests;
- evidence identity/digest for every executable bridge;
- stable review record/reviewer/time provenance bound to bridge content;
- explicit runtime strength and limitations;
- term-scoped active dependency edges;
- bundle/bridge identity in normalized IR and resolution fingerprint;
- explicit exact-lock vs reviewed-bridge satisfaction;
- unique-ID and content-address validation;
- inactive optional-profile separation;
- canonical semantic projection that excludes presentation metadata but preserves operational review identity.

A single per-mapping `ontology_lock` field is insufficient as the final composition model.

## 12. Executable research/TDD contract

Non-production artifacts:

- `scripts/research/r015_bundle_id.py`
- `tests/research/test_r015_bundle_id.py`
- `tests/research/test_r015_bridge_provenance.py`
- `.github/workflows/r015-bundle-research.yml`

The test suite covers at least:

1. order-independent canonical identity;
2. top-level and nested presentation metadata exclusion;
3. ontology digest sensitivity and missing-digest rejection;
4. bridge semantic-content digest verification;
5. bridge endpoint/scope/evidence/runtime sensitivity;
6. evidence identity/digest required for executable bridges;
7. review record/reviewer/time required and review time timezone-aware;
8. bridge review bound to exact changed content digest;
9. exact vs non-exact runtime-strength execution behavior;
10. non-empty runtime limitations and controlled strength vocabulary;
11. duplicate profile/lock/bridge identity rejection;
12. explicit term-scope validation;
13. exact-lock requires/digest binding;
14. bridge source-lock/edge-requires binding;
15. active consumer-lock participation;
16. missing/stale/unreviewed/incompatible/unknown/non-exact bridge failures;
17. inactive dependency diagnostics excluded from active bundle identity;
18. activating an optional edge changes identity;
19. unreferenced/inactive-only bridge locks rejected from active bundle;
20. same namespace with different content digest remains different identity;
21. stable review identity changes bundle identity while reviewer display text does not.

The prototype does not perform ontology reasoning. It validates an explicit reviewed TFont dependency closure and models only the exact execution gate; R-016 owns later approximate-mode authorization.

## 13. Non-goals

R-015 does not:

- choose final production JSON/YAML field names;
- implement production bundle loading;
- replace P-001 individual ontology locks;
- authorize approximate semantic execution (R-016);
- define external authority reference semantics (R-017);
- require RDF/OWL imports or a triplestore at runtime;
- assert ontology-wide equivalence between old and current releases;
- prove cryptographic reviewer identity/authentication; production review provenance/signing policy belongs to governance/tooling implementation.

## 14. Acceptance trace

- [x] deterministic composed bundle identity without a single OWL import closure;
- [x] active semantic projection uses explicit identity-bearing fields only;
- [x] ontology/bridge identity is content-addressed and duplicate IDs fail closed;
- [x] bridge evidence identity/digest is mandatory and content-addressed;
- [x] bridge review record/reviewer/time is mandatory and operationally identity-bearing;
- [x] bridge review is bound to canonical semantic bridge content;
- [x] bridge runtime strength/limitations are explicit; only exact strength passes this reference exact gate;
- [x] bridge use is exact term scoped, not ontology-wide;
- [x] exact-lock and bridge dependency edges are graph-bound to participating locks;
- [x] missing/stale/unreviewed/incompatible/unknown/non-exact dependencies fail closed;
- [x] inactive optional profile is distinct from active unresolved dependency;
- [x] inactive diagnostic edges do not perturb active bundle identity;
- [x] unreferenced bridge locks cannot pollute active bundle identity;
- [x] P-001 lock/digest invariants are retained and P-003 amendments identified;
- [x] OLiA/OntoLex/SKOS, CRM/LRMoo/CRMinf, CRMtex/R-012 and CRMarchaeo/R-010 cases are covered;
- [x] compact agent provenance fields defined;
- [x] executable research tests enforce the principal identity/fail-closed invariants.

## 15. Final independent review targets

Fresh exact-head review should challenge especially:

1. whether the canonical projection contains all and only semantic/operational identity fields;
2. whether bridge semantic-content hashing genuinely invalidates stale review after edits;
3. whether evidence identity/digest and review identity/date are sufficiently bound to executable bridge content;
4. whether runtime strength/limitations preserve the R-016 boundary rather than silently authorizing approximate bridges;
5. whether scope requirements are sufficiently term-specific to prevent ontology-wide compatibility;
6. whether active dependency edges are fully bound to participating consumer/required locks;
7. whether inactive optional diagnostics are separated from active identity;
8. whether any unused bridge/lock can still pollute the active closure;
9. whether CRMtex/CRMarchaeo version-skew claims match authoritative release declarations;
10. whether tests are independent enough to catch self-consistent but fail-open validator behavior;
11. whether P-001 lock identity is reused rather than reimplemented;
12. whether P-003 receives concrete schema/IR inputs without R-015 prematurely freezing production field names.
