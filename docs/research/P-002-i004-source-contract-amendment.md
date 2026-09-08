# P-002 research: forward-compatible TF-native source contract for I-004

**Issue:** #37  
**Recorded:** 2026-09-07  
**Current baseline:** A-001 merged main `9e644f57ab5b5a019f6a4a9384e5bee897c62003`  
**Supersedes:** the pre-A-001 carrier/adapter conclusions previously carried in this artifact

## Decision

P-002 implements only source-side facts that are independent of P-003's final ontology-projection shape and satisfy A-001's TF-native runtime boundary.

The amendment is:

1. profile-owned native dependency definitions in profile schema v2;
2. a closed dependency envelope scoped to already-materialized Text-Fabric / Context-Fabric facts;
3. a **minimum closed assertion shape per dependency kind**, sufficient to make the in-scope native contract mechanically decidable without introducing ontology-projection semantics;
4. explicit TF structural extent/occurrence/technical-anchor interpretation without a generic carrier abstraction;
5. embedded mapping review remains the POC review authority;
6. evidence integrity remains offline/content-addressed; identifiers and URIs do not imply fetching;
7. target multiplicity, target role/type, semantic profiles/capabilities, ontology bundles, per-projection assessment/publication relations, approximation policy, and authority-reference semantics remain P-003 work.

P-002 must not introduce generic `sidecar` / `native-adapter` runtime carriers, external-record/file/field selectors, source-format/database/API adapters, or URI/network dereferencing.

## 1. Mechanical gap

Mappings already carry `native_dependencies: [id, ...]`, but merged source artifacts had no canonical definitions for those IDs. P-001 requires stable dependency identity and complete dependency closure, and I-002's profile semantic projection already anticipates a `dependencies` collection keyed by `dependency_id`.

Profile-owned definitions are preferred over mapping-local duplication or another standalone join layer.

Each dependency contains:

```text
dependency_id    stable non-empty ID
component_id     materialized parent component that owns the fact
kind             controlled TF-native dependency kind
assertion        closed kind-specific TF-native object
evidence?        content-addressed evidence bindings
```

All definitions in a released profile are active requirements. There is no hidden optional/dormant dependency state.

Duplicate dependency IDs with different bodies and cross-artifact component/evidence resolution are semantic reference-integrity checks for I-004; P-002 does not make source records executable before those checks succeed.

## 2. A-001 boundary

Accepted A-001 separates identity/provenance compatibility from executable query-carrier authority.

Legacy parent manifests may remain structurally readable with labels such as `sidecar`, `catalogue`, `zero-span`, or `native-adapter` for identity/provenance purposes. Those labels do not authorize dependency assertions to query files, records, fields, databases, APIs, or network resources.

Current ORACC-TF ADR-0001 confirms the corrected zero-span model: independently positioned textual entities stay inside TF via explicit synthetic/empty slots. Such slots are technical positional anchors, not semantic signs; zero span alone is not a sidecar justification.

External identifiers and URIs remain legitimate reviewed semantic, authority, identity, evidence, and provenance values. Their presence does not imply a fetch/storage capability.

## 3. Dependency contract version

Profile schema v2 carries `dependency_contract_version`.

P-002 implements exactly version **1**. The schema must use `const: 1`, not a lower bound. Accepting an unknown future version would claim semantics the validator does not implement.

## 4. Closed TF-native dependency kinds and assertions

Dependency contract v1 has exactly these eight kinds.

### `component-present`

The owning `component_id` is the fact. Assertion is exactly an empty object:

```json
{}
```

No locator/path/backend field is permitted.

### `node-type-present`

```json
{"node_type": "word"}
```

`node_type` is a non-empty authored TF node type.

### `feature-present`

```json
{"node_type": "word", "feature": "sp"}
```

Both fields are required non-empty authored TF names. P-002 does not infer feature applicability from corpus statistics.

### `edge-present`

```json
{"edge": "mother", "direction": "outgoing"}
```

`direction` is required and is exactly `outgoing` or `incoming`, interpreted relative to the native entity selected by later mapping/query logic. Direction may not be guessed from a feature name.

### `path-present`

```json
{
  "steps": [
    {"edge": "mother", "direction": "outgoing"},
    {"edge": "mother", "direction": "outgoing"}
  ]
}
```

`steps` is a non-empty ordered list of the same closed edge-step shape. Order is semantic. No arbitrary filesystem/source path is represented by this kind.

### `native-value-present`

```json
{
  "node_type": "word",
  "feature": "gn",
  "value": "m",
  "value_semantics": "semantic"
}
```

`value` is a JSON scalar (`string`, finite JSON number, boolean, or null). `value_semantics` is required and fixed to `semantic`; this is an explicit reviewed claim that the authored value is semantically meaningful.

This is the dense-empty guardrail: `""` or `null` is not semantic merely because dense TF storage contains it. Such a value is usable only when an explicit reviewed dependency makes the semantic assertion and later I-004 evidence/reference checks succeed.

### `value-domain`

```json
{
  "node_type": "word",
  "feature": "gn",
  "values": ["m", "f", "NA", "unknown"],
  "domain_semantics": "observed"
}
```

`values` is a non-empty unique array of JSON scalars. `domain_semantics` is exactly:

- `observed` — values are evidenced for the pinned source/release but do **not** form an automatically closed ontology domain;
- `closed-reviewed` — the reviewed source contract explicitly claims a closed domain.

A `closed-reviewed` dependency must carry at least one evidence binding at the dependency level. This prevents a finite observed release sample from silently becoming a closed semantic domain.

### `extent-interpretation`

```json
{"node_type": "word", "interpretation": "textualExtent"}
```

`interpretation` is exactly one of:

```text
textualExtent
occurrenceSet
technicalAnchor
noSlot
```

These are interpretations of already-materialized TF structure, not storage carriers. `technicalAnchor` identifies positional mechanics such as synthetic/empty slots and does not assert source-sign/lexical content. `noSlot` records that no semantic textual extent is represented by a slot set. No domain semantics may be inferred from `oslots` alone.

## 5. Why assertions are closed now

The earlier reconciled draft left `assertion` as an unconstrained object and deferred kind-specific fields. That is insufficient for #37 and A-001:

- `edge-present: {}` cannot mechanically express required direction;
- `extent-interpretation: {"sidecar_path": "..."}` would structurally admit a renamed outside-TF selector;
- value/domain assertions could not distinguish explicit semantic empties from dense storage artifacts or observed domains from reviewed closure.

Therefore P-002 owns these minimum TF-native assertion shapes. Later I-004 may validate whether the asserted TF facts actually exist and whether referenced evidence/components resolve, but it must not reinterpret the source shapes.

## 6. Native selector/applicability boundary

P-002 does not change `mapping.schema.json`; P-003 will revise the semantic projection envelope.

The dependency assertions above are the reusable native fact vocabulary for later selector/applicability validation. They cover node kinds, feature/value facts, directed edges, ordered paths, value-domain semantics, and slot/extent/anchor interpretation without encoding ontology target shape.

Generic external-record selectors, sidecar paths, adapter fields, arbitrary source-file paths, database/API selectors, and implicit URI dereferencing remain outside the baseline contract.

## 7. Review authority

Current mapping sources embed the complete review object; the standalone review schema mirrors that shape but there is no review-reference join field.

**Decision:** embedded mapping review remains authoritative for the first POC. P-003 may later move review binding to per-projection content; P-002 does not introduce a second simultaneous authority.

## 8. Publication and ontology-target boundary

P-002 adds no new publication-relation legality or ontology-target matching semantics.

Reusable later plumbing may preserve authored publication/target data and existing content/review binding, but common-semantic execution must wait for P-003's typed projection/bundle contract. No live ontology lookup is introduced.

## 9. Evidence byte boundary

Later reusable validation may prove that evidence IDs resolve uniquely, declared content digests match normalized records, and explicitly supplied payload bytes match their digest.

It must not fetch evidence over the network, claim unsupplied bytes were verified, infer semantic truth from evidence presence alone, or treat evidence verification as a corpus-data adapter.

## 10. Profile version and digest compatibility

Adding required dependency definitions is an explicit profile source schema v2 change. There is no silent v1 extension.

I-002 digest algorithm changes are not required: the accepted profile semantic projection already includes `schema_version` and normalized dependency content. Assertion content is therefore semantic and already participates in profile identity. Mapping/evidence digest algorithms remain unchanged.

## 11. P-003 deferrals

P-002 does not decide:

- number of semantic projections per native mapping;
- target formal kind / semantic role;
- mapping assessment placement per projection;
- controlled semantic profile/capability identifiers;
- ontology-bundle/bridge-lock schema;
- publication relation placement/legality;
- semantic target CURIE/IRI matching rules;
- approximate execution policy;
- authority/identity/reference reverse indexes;
- final common semantic IR.

## 12. Acceptance conclusion

The smallest forward-compatible amendment is a profile-owned TF-native dependency registry with a closed common envelope and closed minimum assertion shapes for its eight native kinds.

This makes the source-side facts mechanically decidable without introducing an external-storage carrier or selecting P-003's ontology-projection architecture. I-004 remains semantically blocked on P-003 and must additionally validate reference integrity/closure before any dependency can authorize execution.
