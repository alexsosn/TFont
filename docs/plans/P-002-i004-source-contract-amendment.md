# P-002 plan: amend source contracts required by I-004

**Issue:** #37  
**Research:** `docs/research/P-002-i004-source-contract-amendment.md` at `cc3bddb24cdbe9ee366e606c4a4c962dfec0dc27`  
**Baseline:** `d2e393c79c6c2521b68a5c0ee71be46161ce46dd`

## 1. Goal

Make the accepted I-004 semantic-validation scope mechanically expressible without implementing I-004 itself and without changing I-002 digest algorithms.

P-002 changes only the current profile structural source contract plus the normative semantic-contract decisions documented here. It does not add cross-artifact validator production code, compatibility evaluation, IR compilation or runtime behavior.

## 2. Normative design decisions

### 2.1 Profile source schema v2

`profile.schema.json` moves from `schema_version: 1` to `schema_version: 2`.

Profile v2 adds required:

```text
dependencies: [dependency-record, ...]
```

The array is non-empty. Semantic uniqueness by `dependency_id`, component authority and assertion semantics remain I-004 responsibilities.

Each dependency record structurally requires:

```text
dependency_id    non-empty string
component_id     non-empty string
kind             accepted dependency-kind enum
assertion        JSON object
evidence?        array of exact {evidence_id, content_digest} bindings
```

No `required` flag exists. Every dependency definition in one released profile is active. There are no dormant/optional definitions in the first POC.

Accepted dependency kinds:

```text
component-present
node-type-present
feature-present
edge-present
path-present
native-value-present
value-domain
extent-interpretation
adapter-capability
sidecar-field
```

### 2.2 Dependency contract v1

When `dependency_contract_version == 1`, I-004 must later enforce exact semantic assertion shapes:

- `component-present`: `{}`
- `node-type-present`: `{node_type}`
- `feature-present`: `{node_type, feature}`
- `edge-present`: `{edge, direction[, source_node_type, target_node_type]}`; direction `out | in`
- `path-present`: `{steps:[{edge,direction}, ...]}`; non-empty and ordered
- `native-value-present`: `{node_type, feature, value}`; value exact JSON scalar
- `value-domain`: `{node_type, feature, domain_mode[, values]}` where mode is `observed | documented-bounded | closed | open | unknown`; `observed`, `documented-bounded`, `closed` require non-empty unique scalar values; `open`, `unknown` prohibit values
- `extent-interpretation`: `{native_object, extent}` where extent is `semantic | anchor-only | source-span | sidecar-zero-span`
- `adapter-capability`: `{capability, minimum_version}`
- `sidecar-field`: `{field_path:[segment, ...]}` with non-empty ordered non-empty segments

I-004 must reject unknown assertion fields rather than ignore them.

Evidence requirements for I-004:

- `documented-bounded` and `closed` domains require dependency evidence;
- `native-value-present` with value `""` or `null` requires dependency evidence;
- `anchor-only` and `sidecar-zero-span` extent interpretations require dependency evidence.

P-002's JSON Schema does not duplicate these semantic conditionals; it establishes the common record envelope and known kind only.

### 2.3 Native selector contract v1

The mapping schema remains structurally unchanged in P-002. I-004 must semantically accept only:

- `feature-value`: `kind, component_id, node_type, feature, operator=eq, value, extent`
- `node-kind`: `kind, component_id, node_type, extent`
- `edge`: `kind, component_id, edge, direction, extent` plus optional source/target node types
- `path`: `kind, component_id, steps[{edge,direction}], extent`
- `sidecar-field`: `kind, component_id, field_path[], extent`
- `zero-span-entity`: `kind, component_id, entity_type, extent=sidecar-zero-span`
- `source-span`: `kind, component_id, field_path[], extent=source-span`

Allowed extent values are exactly `semantic | anchor-only | source-span | sidecar-zero-span`. Unknown selector keys fail semantic validation.

A `feature-value` selector with `value == ""` or `null` requires a matching evidence-backed `native-value-present` dependency. `anchor-only` and `sidecar-zero-span` selectors require a matching evidence-backed extent dependency. Storage coincidence alone never grants semantic meaning.

### 2.4 Applicability contract v1

I-004 accepts only optional fields:

```text
node_type       non-empty string
semantic_domain non-empty string
preconditions   unique dependency-ID strings
```

Unknown keys fail. Selector/applicability `node_type`, when both present, must agree. `semantic_domain` must be declared by the profile. Preconditions resolve through profile dependencies.

### 2.5 Review authority

The embedded mapping `review` object is authoritative for the first POC. No separate review artifact is required for mapping validity. `review_id` is audit provenance, not a join key to a second authoritative record.

`review.schema.json` remains a reusable standalone shape; its existence does not create a second source of truth.

This supersedes P-001 prose implying mandatory separate review-record references.

### 2.6 Publication relation

For semantic contract v1, executable I-004 validation requires:

```text
publication_relation: null
```

A non-null publication relation fails with an explicit unsupported/formalism-contract error. No ontology-namespace guessing is allowed. A later reviewed publication-formalism contract may extend this before I-009.

The structural mapping schema remains string-or-null so audit/authoring source can carry a proposed relation; I-004 decides executable validity.

### 2.7 Ontology target matching

Target membership is exact authored-string equality against the selected lock's `terms_used`. No CURIE expansion, namespace concatenation, case folding, Unicode normalization or live lookup occurs.

### 2.8 Evidence boundary

I-004 will:

- resolve mapping/candidate/dependency evidence IDs;
- require binding digest equality to the referenced record;
- recompute `normalized-record` evidence with I-002;
- never fetch external-payload evidence over the network.

Exact external-payload byte verification remains explicit caller/tooling work via I-002 when bytes are available; absence of embedded bytes is not silently treated as a successful payload re-verification.

## 3. I-002 compatibility

No digest algorithm or projection code changes in P-002.

Rationale:

- `profile_semantic_digest()` already requires a `dependencies` collection and normalizes it by `dependency_id`;
- `schema_version` already participates in the profile semantic projection;
- mapping semantic digest already includes selector, dependency IDs, applicability and publication relation exactly as authored;
- embedded review remains excluded exactly as before.

Existing I-002 fixed vectors must remain byte-for-byte unchanged.

## 4. Production file changes

P-002 production change is limited to:

```text
src/tfont/schemas/profile.schema.json
```

Required edit:

- profile `schema_version` const `1 -> 2`;
- add `$defs.evidenceBinding` and `$defs.dependency` (or equivalent local definitions);
- add required `dependencies` property;
- dependency common-envelope validation and known kind enum;
- retain `additionalProperties: false` at profile/dependency/binding levels.

No Python production module is changed.

## 5. Test changes

Before schema production edit, add `tests/p002/` regressions proving current main is RED for the amended contract.

Mandatory focused cases:

1. profile v2 with one well-formed dependency should be structurally valid after GREEN;
2. profile v1 is rejected by the amended current contract;
3. profile v2 missing `dependencies` is rejected;
4. empty dependencies is rejected;
5. unknown dependency kind is rejected structurally;
6. missing dependency common field is rejected;
7. malformed dependency evidence binding is rejected;
8. dependency assertion is required to be an object but kind-specific contents are deliberately deferred to I-004;
9. component records still cannot carry an independent `required` flag;
10. mapping/review/ontology/evidence schemas remain unchanged by P-002;
11. representative existing I-002 mapping/evidence fixed digests remain unchanged;
12. profile semantic digest remains order-invariant for dependency records and changes when behavior-affecting dependency content changes, using the existing I-002 API.

The RED commit must fail specifically because current profile schema requires v1 and rejects `dependencies`, while non-profile/I-002 controls pass.

## 6. Workflow

Add `.github/workflows/p002-i004-source-contract.yml` triggering on:

```text
src/tfont/schemas/profile.schema.json
tests/p002/**
docs/research/P-002-i004-source-contract-amendment.md
docs/plans/P-002-i004-source-contract-amendment.md
.github/workflows/p002-i004-source-contract.yml
```

Matrix Python 3.10/3.12. Steps:

1. install package;
2. run focused `tests/p002`;
3. run I-001 structural validator tests;
4. run I-002 digest tests;
5. run full repository suite.

If F-007 merges before P-002 finalization, integrate current main and remove duplicate generic full-suite ownership from this feature workflow, leaving the authoritative centralized full-suite gate to F-007.

## 7. RED -> GREEN sequence

1. research commit (already complete);
2. this plan commit;
3. focused P-002 test package commit;
4. P-002 workflow commit;
5. record exact RED CI failure;
6. edit profile schema only;
7. run focused + I-001 + I-002 + full exact-head CI;
8. compare against current main to prove no accidental Python/runtime edits;
9. fresh independent adversarial review of exact head;
10. merge only after PASS; then resume I-004 #36 from the amended main.

## 8. Independent-review attack surface

Review must try to falsify:

- whether `dependencies` really closes the missing I-004 reference gap;
- accidental optional/dormant dependency semantics;
- accidental I-002 digest/version changes;
- schema v1 being silently reinterpreted instead of versioned;
- ability to smuggle unknown dependency kinds/common fields;
- review double-authority ambiguity;
- non-null publication relation accidentally becoming executable;
- CURIE/namespace inference not grounded in locks;
- dense-empty semantics becoming valid without evidence;
- semantic rules being incorrectly hidden in structural JSON Schema rather than the versioned I-004 contract.

Any requested change that alters fields, authority, digest semantics or execution policy requires amendment of this plan before implementation.
