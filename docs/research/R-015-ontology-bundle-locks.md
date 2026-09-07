# R-015: ontology-bundle composition and bridge-lock provenance semantics

**Status:** research complete; pending fresh logically-independent adversarial review  
**Issue:** #49  
**Recorded:** 2026-09-07  
**Depends on:** accepted P-001/R-002/R-006/R-010/R-012 and merged roadmap guardrail #45

## Decision

TFont should model a semantic composition as a **content-addressed bundle of independently locked ontology releases plus explicit reviewed bridge artifacts**, not as one OWL import closure and not as a bag of live namespace URLs.

The runtime composition contract is:

```text
individual ontology lock(s)
        +
explicit bridge lock(s), only where an active dependency path needs them
        +
profile activation/dependency selection
        ↓
canonical semantic bundle projection
        ↓ canonical JSON / UTF-8 / sorted set-like collections
SHA-256 bundle identity
```

Existing P-001 ontology locks remain authoritative for individual model snapshots. R-015 adds a higher-level composition identity and makes bridge evidence first-class.

A bundle is **not** “all ontologies TFont knows about”. It is the exact semantic dependency closure needed by one active profile/mapping set. Inactive optional profiles do not contribute ontology or bridge dependencies and cannot fail merely because a bridge for that unused profile is unavailable.

## 1. Why individual ontology locks are not enough

The current v1 `ontology-lock.schema.json` correctly pins an individual ontology by fields including:

- `ontology_id`;
- `release`;
- `source_uri` / source revision;
- `content_digest`;
- `snapshot_artifact`;
- licence / redistribution policy;
- `terms_used`.

That solves snapshot identity, but not composition identity.

A query may simultaneously depend on multiple releases whose upstream dependency graphs are not mutually current. The bundle must therefore answer:

1. which exact ontology snapshots participate;
2. which upstream dependency releases are being respected;
3. which explicit cross-release bridge assertions participate;
4. whether those bridges were reviewed for the exact source/target releases and terms used;
5. whether an optional dependency is actually active;
6. whether changing any participating lock/bridge changes the reproducible semantic identity.

## 2. Authoritative version-skew evidence

### 2.1 CRMtex 2.0

CIDOC CRM's CRMtex 2.0 declarations state that CRMtex 2.0 references:

- CIDOC CRM 7.1.2;
- CRMinf 0.7(b);
- CRMsci 2.0;
- FRBRoo 2.4.

Primary source: <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>.

The current TFont semantic basis otherwise uses current releases such as CIDOC CRM 7.1.3, LRMoo 1.1.1 and CRMinf 1.2.1. R-012 already established that TFont must not silently replace CRMtex's historical dependencies with current axioms. It permits only term-scoped reviewed bridges where an active mapping actually needs them.

### 2.2 LRMoo 1.1.1 / CRMinf 1.2.1

LRMoo 1.1.1 references CIDOC CRM 7.1.3. CRMinf 1.2.1 likewise references CIDOC CRM 7.1.3.

Primary sources:

- <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>

These releases can share a current CRM basis, but that does not retroactively modernize CRMtex 2.0's own declared closure.

### 2.3 CRMarchaeo 2.1.1

Stable CRMarchaeo 2.1.1 references CIDOC CRM 7.1.2 and CRMsci 2.0. R-010 accepted current TFont heritage/scientific work against CIDOC CRM 7.1.3 and CRMsci 3.2.

Primary source: <https://cidoc-crm.org/node/8943> and the 2.1.1 model declarations.

Therefore CRMarchaeo creates a second, independent proof that bundle semantics cannot be designed as one assumed-current import closure.

## 3. Three separate identities

TFont must keep these distinct:

### 3.1 Ontology lock identity

Identity of one pinned model release/snapshot.

Conceptually:

```json
{
  "lock_id": "crmtex-2.0",
  "ontology_id": "crmtex",
  "release": "2.0",
  "content_digest": "sha256:..."
}
```

This is the existing P-001 layer.

### 3.2 Bridge lock identity

Identity of one reviewed cross-release semantic bridge artifact.

A bridge lock binds at least:

- bridge artifact ID and schema version;
- exact source ontology lock ID + digest;
- exact target ontology lock ID + digest;
- bridge direction;
- exact term/assertion scope;
- relation/continuity assertion kind;
- evidence references;
- review identity/status;
- bridge content digest;
- optional expiry/supersession metadata.

A bridge is not authorized by matching local names, labels, namespaces or stable-looking IRIs.

### 3.3 Bundle identity

Identity of the exact active semantic composition used for capability discovery/resolution.

It includes references to participating ontology lock identities, bridge lock identities and dependency/profile activation facts. It does **not** copy live ontology content into the bundle projection.

## 4. Canonical bundle projection

P-003 should define a versioned canonical projection equivalent to:

```json
{
  "schema_version": 1,
  "profile_contracts": ["written-text@1"],
  "ontology_locks": [
    {"lock_id": "crm-7.1.3", "digest": "sha256:..."},
    {"lock_id": "crmtex-2.0", "digest": "sha256:..."}
  ],
  "bridge_locks": [
    {"bridge_id": "crmtex-f28-to-lrmoo-1", "digest": "sha256:..."}
  ],
  "dependency_edges": [
    {
      "consumer": "crmtex-2.0",
      "requires": "frbroo-2.4/F28",
      "satisfied_by": "bridge:crmtex-f28-to-lrmoo-1"
    }
  ]
}
```

Set-like collections are sorted by stable identity before canonicalization. JSON object keys follow the accepted canonical JSON/digest rules from P-001/I-002. Presentation order, retrieval timestamp and audit-only reviewer display metadata do not affect the semantic digest unless explicitly promoted into the canonical semantic contract.

## 5. Bridge artifact semantics

### 5.1 Bridges are explicit evidence-bearing assertions

Every bridge assertion must identify:

```text
source release + source term
        ↓ reviewed continuity/mapping assertion
exact target release + target term
```

A bridge may assert continuity, replacement, retained identifier semantics, reviewed broader/narrower relation, or another controlled migration relation. R-015 does not require one universal bridge predicate.

### 5.2 Term-scoped, not ontology-wide

R-012 demonstrated why ontology-wide compatibility is unsafe. For example, F28 continuity may be supportable from official FRBRoo→LRMoo migration evidence while old/new CRMinf hierarchy cannot be wholesale substituted.

Therefore one valid bridge never upgrades the entire source model to “compatible with latest”.

### 5.3 Content-addressed and reviewed

A bridge artifact must have:

- deterministic canonical content;
- `content_digest`;
- immutable source/target lock digests;
- evidence and rationale;
- explicit review state;
- review bound to the bridge content digest;
- reproducible local snapshot/reference for the evidence where licensing permits.

Editing bridge semantics invalidates its review and changes all bundle identities that consume it.

## 6. Bundle dependency resolution

Bundle construction is demand-driven from active profiles/mappings.

Algorithmically:

```text
active mappings/profile capabilities
    ↓
collect ontology locks actually used
    ↓
collect declared dependency edges required by those terms/projections
    ↓
for each dependency edge:
    exact compatible locked release available? -> satisfy directly
    reviewed bridge available?                 -> satisfy via bridge
    otherwise                                  -> unresolved dependency
    ↓
if any required dependency unresolved -> bundle non-executable
else -> canonicalize and digest
```

Do not traverse an ontology's entire superclass/import graph merely because a snapshot contains it. The canonical semantic dependency closure is the reviewed TFont execution dependency closure.

## 7. Optional-profile rule

This distinction is mandatory:

```text
profile absent/inactive
    !=
profile active but bridge missing
```

Example:

- corpus has no archaeology capability → no CRMarchaeo bundle dependency → status `absent`; no bridge error;
- corpus activates a CRMarchaeo mapping whose term requires the 7.1.2/CRMsci 2.0 closure → dependency enters active bundle;
- if current-stack composition needs an explicit bridge and it is missing/stale/incompatible → `unavailable` / non-executable with bridge diagnostic.

TFont must never emit a scary “CRMarchaeo bridge broken” warning for a linguistic corpus that never activated archaeology.

## 8. Failure states

At minimum P-003 needs machine-readable dependency outcomes equivalent to:

- `satisfied-exact-lock` — active requirement is satisfied by the exact locked dependency release;
- `satisfied-reviewed-bridge` — active requirement is satisfied through a reviewed bridge locked to exact source/target snapshots;
- `missing-lock` — required ontology snapshot is absent;
- `missing-bridge` — active cross-release dependency has no accepted bridge;
- `stale-bridge` — bridge points to old source/target lock digest;
- `unreviewed-bridge` — bridge exists but is not accepted for execution;
- `incompatible-bridge` — review/evidence explicitly rejects the attempted composition;
- `inactive` — optional dependency/profile not activated; not an error.

Aggregate bundle state is executable only when every active requirement is satisfied by exact lock or reviewed bridge and normal parent/profile compatibility gates also pass.

## 9. Migration behavior

### 9.1 Ontology release changes

If one participating ontology lock changes, the bundle digest changes even if no mapping YAML changes.

Mappings referencing terms from the new lock require the ordinary mapping/lock compatibility validation. Any bridge referencing the previous digest becomes stale until reviewed or regenerated.

### 9.2 Bridge changes

Any semantic change to a bridge changes bridge digest and bundle digest. Review is content-bound and must be refreshed.

### 9.3 Unused ontology updates

Updating a known but inactive ontology does **not** change a corpus/profile bundle that does not include it.

This makes capability/result provenance meaningful rather than globally invalidating TFont whenever any supported ontology publishes a new release.

## 10. Composition examples

### 10.1 OLiA + OntoLex + SKOS

A linguistic+lexical corpus may use:

- OLiA lock for corpus annotation categories;
- OntoLex core lock for lexical entry/sense classes;
- SKOS lock where shared LexicalConcept/concept mapping semantics are used.

If these projections do not require a cross-version semantic bridge, the bundle has several ontology locks and zero bridge locks. Multiple ontologies alone do not imply bridge complexity.

### 10.2 CRM + LRMoo + CRMinf

A textological corpus may activate current CRM 7.1.3, LRMoo 1.1.1 and CRMinf 1.2.1. Their current dependency basis is coherent around CRM 7.1.3 for the reviewed terms used.

Again, explicit bundle identity is still required because a later release of any member changes reproducibility.

### 10.3 CRMtex 2.0

A written-text mapping that uses only CRMtex terms whose execution does not activate the FRBRoo/old-CRMinf bridge surface may keep the version-faithful CRMtex dependency closure without inventing a modern bridge.

If a mapping/query uses a CRMtex path whose semantics depend on a term covered by R-012's reviewed modern bridge, the bridge becomes part of the active bundle and therefore of the resolution fingerprint/provenance.

### 10.4 CRMarchaeo 2.1.1

For a corpus with no archaeology capability: no CRMarchaeo lock/bridge in the active bundle.

For a future corpus with explicit excavation semantics: CRMarchaeo 2.1.1 and its declared CRM 7.1.2/CRMsci 2.0 dependencies must be respected. If TFont composes those semantics with current CRM/CRMsci projections, any necessary cross-release bridge is explicit and reviewed; absence is fail-closed.

## 11. Agent-facing provenance

### `semantic_capabilities`

Compact output should expose:

- profile identity/version;
- bundle ID/digest;
- active ontology lock IDs/releases;
- bridge count and aggregate bridge state;
- optional profile state (`active|absent|unavailable`);
- no full bridge dump by default.

### `semantic_resolve`

Each corpus plan should expose:

- bundle digest used for resolution;
- mapping/projection IDs;
- required ontology lock identities;
- bridge identities actually traversed by the requested semantic atoms;
- any unresolved dependency and reason;
- execution allowed/denied.

### Full explanation

Add:

- exact source/target lock digests;
- bridge assertion scope;
- evidence/review identity;
- dependency path;
- supersession/staleness reason when applicable.

A result page/pagination token must not silently switch bundle identity.

## 12. P-001 contracts retained vs amended

### Retained

- individual ontology snapshot locks;
- content digests;
- deterministic canonicalization;
- evidence/review binding;
- fail-closed compatibility;
- semantic digest/provenance discipline.

### P-003 amendment required

- add first-class semantic-bundle identity;
- allow multiple ontology locks per active profile/mapping projection set;
- add explicit bridge artifacts/locks;
- include bundle + bridge identities in normalized IR and resolution fingerprints;
- dependency validation must distinguish exact-lock vs reviewed-bridge satisfaction;
- optional inactive profiles do not create missing-dependency errors;
- a single per-mapping `ontology_lock` field is insufficient as the final composition model.

## 13. Research prototype / TDD contract

R-015 should be accompanied by a non-production deterministic bundle-ID prototype and tests.

Required RED/GREEN invariants:

1. reordering ontology locks does not change bundle digest;
2. reordering bridge locks does not change bundle digest;
3. reordering dependency edges does not change bundle digest;
4. changing a participating ontology digest changes bundle digest;
5. changing bridge content digest changes bundle digest;
6. adding an unused known ontology does not change the active bundle;
7. activating a previously absent optional profile changes the dependency closure/bundle identity;
8. active missing bridge fails closed;
9. inactive optional profile with unavailable bridge remains `inactive`, not error;
10. bridge source lock digest mismatch produces `stale-bridge`;
11. unreviewed bridge cannot produce executable bundle;
12. exact dependency lock needs no bridge;
13. bridge review is bound to bridge content digest;
14. two bundles with same live namespace URLs but different release/content digests are different identities;
15. presentation/audit-only fields do not alter semantic bundle digest.

## 14. Non-goals

R-015 does not:

- choose production JSON schema names;
- implement production bundle loading;
- authorize approximate semantic execution (R-016);
- define external authority reference semantics (R-017);
- replace P-001 individual ontology locks;
- require RDF, OWL imports or a triplestore at runtime;
- make old/new ontology releases globally equivalent.

## 15. Acceptance trace

- [x] deterministic composed bundle identity defined without a single OWL import closure;
- [x] bridge artifacts are content-addressed, evidence-bound and review-bound;
- [x] missing/stale/unreviewed/incompatible bridge behavior is fail-closed;
- [x] inactive optional profile is distinguished from active profile dependency failure;
- [x] P-001 lock/digest invariants are retained and precise P-003 amendments identified;
- [x] OLiA/OntoLex/SKOS, CRM/LRMoo/CRMinf, CRMtex/R-012 and CRMarchaeo/R-010 cases covered;
- [x] compact capability/resolution provenance fields defined;
- [x] research TDD invariants defined for a reference prototype.

## Review targets

A fresh logically-independent reviewer should challenge especially:

1. whether bundle identity includes too much or too little semantic state;
2. whether dependency closure is sufficiently deterministic without reimplementing ontology reasoning;
3. whether bridge scope/review rules prevent accidental ontology-wide compatibility claims;
4. whether inactive optional profiles can truly avoid false bridge failures;
5. whether CRMtex and CRMarchaeo version-skew examples match authoritative release declarations;
6. whether audit/presentation fields are correctly excluded from semantic identity;
7. whether P-001 ontology locks remain reusable rather than being duplicated;
8. whether the prototype tests actually prove the digest/fail-closed claims.
