# P-001: foundation POC semantic profile and compiler design

**Status:** design candidate; implementation blocked until exact-head review and merge  
**Issue:** #12  
**Recorded:** 2026-09-05  
**Scope:** design only; no production schemas, profiles, compiler, resolver, or MCP implementation

## 1. Decision

The first TFont POC uses a **validated canonical source bundle** compiled deterministically into a **normalized semantic IR**. Runtime, reference, compatibility and publication artifacts are generated derivatives; none is a second semantic source of truth.

The canonical source bundle contains:

1. a **profile manifest**;
2. an expected **parent component manifest**;
3. one or more **ontology lock** records;
4. one or more **canonical mapping source** YAML files;
5. stable evidence and review records referenced by ID.

The one-way artifact flow is:

```text
canonical source bundle
  profile manifest
  + parent component manifest
  + ontology lock(s)
  + canonical mapping source
  + evidence/review records
            |
            v
parse + JSON Schema 2020-12 validation
            |
            v
cross-artifact semantic validation
            |
            v
normalized semantic IR
            |
      +-----+-------------------+--------------------+
      |                         |                    |
      v                         v                    v
runtime sidecar          reference JSON      publication output
                              |                RDF/OWL/SKOS
                              v
                        generated docs
```

Every artifact below normalized semantic IR is a **generated derivative**. The compiler must be deterministic and fail closed when source contracts cannot be proved.

## 2. Accepted foundation dependencies

This design pins the accepted foundation state. Material changes require a new reviewed design change before implementation contracts move.

| research | reviewed exact head | merged main commit |
|---|---|---|
| R-005 | `48c8bd78d0c3a0501b2fdec6946db5df90517bdb` | `a9c4d74d4de2f9a15eb1464dce341ecd2f92f898` |
| R-001 | `68b88a820f5519ad65d46b732679a6278e9ca3c9` | `a22a95084a1518882d1e3e87d10e9757121f106d` |
| R-002 | `d82e6ef2726f149f903eb43ddbfb615faf399cd5` | `a554d4fdc36c8854519064f3a7611b80efa29622` |
| R-003 | `6747379a4aa68c17c156344f3ed3b0c2cb29d423` | `02abd89b5b7d4c83027e1e8503a02eef23cab91e` |
| R-004 | `3dcadc0b32aef95ecbf6ad94f6bbc062f8c6200f` | `00a5d6b7de777074b01bb70ac425d7f187781298` |

The accepted contracts preserved here are: R-001 component-aware parent identity and four compatibility states; R-002 mapping assessment governance and publication separation; R-003 fail-closed semantic resolver handoff and protocol independence; R-004 scoped documentation authority and generated-reference architecture; R-005 empirical edge cases and candidate-only evidence.

## 3. Future production layout

This design PR does **not** create these directories. Implementation tickets will create them after this plan is accepted.

```text
schemas/
  profile.schema.json
  parent-component-manifest.schema.json
  ontology-lock.schema.json
  mapping.schema.json
  semantic-ir.schema.json

profiles/
  <profile-id>/
    profile.yaml
    parent/expected-components.json
    mappings/*.yaml
    evidence/*
    reviews/*
    tests/fixtures/*

ontology/locks/<lock-id>.yaml

build/<profile-id>/
  semantic-ir.json
  runtime-index.json
  compatibility-report.json
  reference/index.json
  publication/mapping.ttl

dist/<profile-id>/<profile-version>/...
```

The release boundary is one profile release, not the whole repository revision.

## 4. Validation and source parsing

Production schemas use **JSON Schema Draft 2020-12** and declare `https://json-schema.org/draft/2020-12/schema`.

Canonical YAML is an authoring surface, not a hashing format. Parsing must:

- decode UTF-8;
- reject duplicate keys;
- reject YAML constructs that cannot be represented losslessly in the JSON-compatible model;
- preserve authored Unicode strings without hidden normalization;
- convert to the JSON-compatible source model before cross-artifact validation.

Structural JSON Schema validation is followed by semantic validation of IDs, references, compatibility dependencies, ontology targets, review bindings and native edge cases.

## 5. Profile manifest contract

The future `profile.yaml` minimally contains:

- `schema_version` — profile schema version;
- `profile_id` — stable logical profile ID;
- `profile_version` — immutable release-navigation label;
- `semantic_domains` — declared domains;
- `parent_component_manifest` — expected parent-manifest reference;
- `required_components` — authoritative set of semantically addressable native component IDs used by this released profile;
- `ontology_locks` — lock IDs used by mappings/publication;
- `mapping_sources` — canonical mapping source paths;
- `dependency_contract_version` — dependency-expression contract version;
- `minimum_tfont_runtime` — minimum runtime contract;
- `license` — mapping/profile license metadata;
- `provenance` — non-volatile source provenance.

Example:

```yaml
schema_version: 1
profile_id: tfont-bhsa
profile_version: 0.1.0
semantic_domains: [morphology]
parent_component_manifest: parent/expected-components.json
required_components: [bhsa-tf]
ontology_locks: [olia-2026-02-04]
mapping_sources: [mappings/morphology.yaml]
dependency_contract_version: 1
minimum_tfont_runtime: 0.1.0
license: CC-BY-4.0
```

### 5.1 Required-component authority

`required_components` is authoritative for release activation. Component records do not carry an independent `required` flag.

The expected parent component manifest contains exactly the component records named by `required_components` for that released profile. Every active mapping dependency must reference one of those components. A mapping cannot depend on an undeclared optional component and still participate in the released executable profile.

If a future product needs optional feature packs, they are separate profile/module releases with their own manifests rather than hidden partial activation inside one profile.

## 6. Parent component manifest

The parent component manifest is the transport-independent exact-identity record for every **semantically addressable native component** used by the profile.

Supported POC component kinds include:

- **TF payload**;
- **external/native sidecar**;
- **catalogue**;
- **zero-span** entity store;
- **native-adapter** artifact.

Each component record contains:

- `component_id`;
- `kind`;
- `identity_algorithm`;
- `content_digest`;
- optional non-authoritative `logical_locator`;
- optional `license_ref`.

Conceptual shape:

```json
{
  "algorithm": "tfont-parent-components-sha256-v1",
  "components": [
    {
      "component_id": "bhsa-tf",
      "kind": "tf-payload",
      "identity_algorithm": "tfont-tf-files-sha256-v1",
      "content_digest": "sha256:..."
    }
  ]
}
```

Component records are sorted by `component_id`; the manifest identity is SHA-256 of canonical JSON over semantic identity fields. Absolute machine paths are excluded.

### 6.1 TF and sidecar identity

`tfont-tf-files-sha256-v1` hashes a sorted list of `{relative_logical_path, sha256}` for the addressed TF payload files. Directory-like sidecars use the same sorted-path/per-file-digest pattern. A single-file sidecar uses SHA-256 of exact bytes.

Dense storage empties remain part of exact TF byte identity even though they are not semantic values.

### 6.2 Exact-identity negative invariant

If **TF bytes stay identical** but a required external/native sidecar, catalogue, zero-span store, or native-adapter component changes, the parent manifest changes and the profile **must not remain `verified-exact`**.

This is a mandatory negative regression.

## 7. Native dependency contract

Mappings reference stable dependency IDs through `native_dependencies`.

POC dependency kinds include:

- component present;
- node/entity type present;
- feature present on the expected native object kind;
- edge/path present with explicit direction;
- required native value present;
- value-domain invariant;
- extent interpretation (`semantic`, `anchor-only`, `source-span`, `sidecar-zero-span`);
- adapter capability/version invariant;
- sidecar field/path invariant.

The **complete dependency closure** is the union of profile-level dependencies plus every dependency of every active released mapping. The POC does not partially activate whichever mappings happen to validate.

Every dependency names a `component_id` from the authoritative `required_components` set.

## 8. Compatibility algorithm

The validator compares the expected and observed parent component manifests and, when they differ, validates the complete dependency closure.

- `verified-exact` — every required component identity matches the reviewed release target exactly and the release evidence already validates the complete dependency contract.
- `verified-compatible` — at least one component identity differs, but the complete dependency closure is successfully validated against the changed components.
- `unverified` — no known failure, but complete evidence cannot be established; non-executable.
- `incompatible` — at least one required dependency fails or required component is absent/invalid; non-executable.

**Only `verified-exact` and `verified-compatible` are executable**.

Known failure dominates incomplete evidence: a proven false dependency yields `incompatible`, not `unverified`.

## 9. Ontology lock contract

An ontology lock pins the exact external evidence used during review and compilation. Minimum fields are:

- `lock_id`;
- `ontology_id`;
- `support_tier`;
- `term_namespace`;
- `release` and upstream release status where applicable;
- `source_uri`;
- optional `source_revision`;
- `content_digest`;
- non-semantic `retrieved_at`;
- `license` / redistribution policy;
- `snapshot_artifact` locator;
- validated `terms_used` index.

Runtime query resolution never changes mappings from live ontology URLs. Existing profile semantics remain bound to their lock.

## 10. Canonical mapping source contract

Every mapping object minimally contains:

- `mapping_id` — stable mapping lineage ID;
- `profile_id` — owning profile;
- `native_selector` — declarative native selector/path;
- `native_dependencies` — dependency IDs;
- `external_target` — approved external URI/CURIE or null;
- `candidate_projections` — ambiguity candidates only;
- `assessment` — runtime/query assessment;
- `publication_relation` — optional separately justified formal relation;
- `applicability` — object/domain/precondition constraints;
- `ontology_lock` — lock for external semantics;
- `evidence` — stable evidence references;
- `review` — review status/provenance plus reviewed digest;
- `mapping_semantic_digest` — machine identity of the reviewed mapping semantics;
- `rationale` — non-executable explanation;
- `introduced_in` / `changed_in` — release-navigation metadata.

A normal reviewed mapping shape is conceptually:

```yaml
mapping_id: bhsa.word.gn.m-to-olia-masculine
profile_id: tfont-bhsa
native_selector:
  kind: feature-value
  component_id: bhsa-tf
  node_type: word
  feature: gn
  operator: eq
  value: m
  extent: semantic
native_dependencies: [bhsa.word.gn.m]
external_target: http://purl.org/olia/olia.owl#Masculine
candidate_projections: []
assessment: exact
publication_relation: null
applicability:
  node_type: word
ontology_lock: olia-2026-02-04
evidence: [bhsa-doc:gn]
mapping_semantic_digest: sha256:...
review:
  status: reviewed
  review_id: review:...
  reviewed_mapping_digest: sha256:...
rationale: Reviewed native and ontology definitions support this projection.
```

## 11. Native selector model

`native_selector` may represent `feature-value`, `node-kind`, directed `edge`, ordered `path`, `sidecar-field`, `zero-span-entity`, or `source-span`.

Edges and paths record direction explicitly. A shared feature/edge label never proves shared meaning.

`extent` is one of:

- `semantic`;
- `anchor-only` for a technical anchor;
- `source-span`;
- `sidecar-zero-span`.

This prevents technical TF anchors from masquerading as semantic extent.

## 12. R-002 mapping assessment contract

Assessment direction is always **native/source → external target**.

- `exact` — external target and native/source concept are judged coextensive.
- `close` — substantial overlap without established coextensiveness.
- `broader` — external target is broader than native/source.
- `narrower` — external target is narrower than native/source.
- `related` — related, not a substitute constraint.
- `ambiguous` — evidence does not justify one target/assessment projection.
- `native-only` — native/source concept is supported with no external projection.
- `unsupported` — profile provides no supported semantic projection.

The **assessment and publication relation are independent**. `assessment: exact` does not imply any OWL/SKOS equivalence assertion.

Validation rules:

- `exact | close | broader | narrower | related` require one `external_target` and a valid ontology lock;
- `native-only` and `unsupported` have no external target and require `external_target: null`;
- `ambiguous` requires `external_target: null`, is non-executable, and uses `candidate_projections` rather than a target-only list;
- `publication_relation` is null unless independently reviewed for the target formalism;
- R-005 candidate codes never populate `assessment` automatically.

### 12.1 Ambiguity representation

Each `candidate_projections` entry contains at least:

```yaml
external_target: <candidate URI or CURIE>
assessment_candidate: exact | close | broader | narrower | related
evidence: [<evidence IDs>]
```

This represents both target ambiguity and relation ambiguity. Two entries may use the **same external target** with **different candidate assessments**, for example the same ontology term with `exact` versus `close` unresolved. The approved mapping still has `external_target: null` until ambiguity is resolved.

Candidate ordering, labels, result counts and first-match behavior must not make `ambiguous` automatically executable.

## 13. Review binding and readiness

Review states are:

- `reviewed` — may participate in released executable behavior if all other gates pass;
- `provisional` — diagnostic/authoring only;
- `disputed` — audit/research only.

### 13.1 Per-mapping semantic digest

`mapping_semantic_digest` is SHA-256 of RFC 8785 canonical JSON over behavior/publication-affecting mapping fields, including:

- `mapping_id` and owning `profile_id`;
- `native_selector`;
- `native_dependencies`;
- `external_target` or ambiguity `candidate_projections`;
- `assessment`;
- `publication_relation`;
- `applicability`;
- `ontology_lock`;
- behavior-affecting evidence/provenance IDs when the mapping contract declares them normative.

It excludes the **review record itself**, rationale prose, release-navigation fields and the digest field itself, avoiding self-reference.

For `review.status: reviewed`, `review.reviewed_mapping_digest` **must match** the recomputed `mapping_semantic_digest`. A mismatch is a **stale review** and is non-executable/non-releasable. Changing selector, target, candidate projection, assessment, publication relation, applicability or ontology binding therefore invalidates review automatically.

This rule is checked by the compiler; a contributor cannot preserve `status: reviewed` across a material mapping edit without a new review binding.

## 14. Normalized semantic IR

The **normalized semantic IR** is the only compiler input to generated runtime/reference/publication artifacts. It is deterministic and JSON-compatible.

It contains:

- normalized profile metadata;
- expected parent component manifest identity and component identities;
- dependency definitions;
- ontology locks/term pins;
- normalized mappings including `mapping_semantic_digest` and review binding;
- review readiness;
- generated lookup indexes;
- explicit IR format version.

Behavior-affecting fields are separated from prose/display metadata.

Normalization rules:

- documented field names/types only;
- identifiers validated but not silently case-folded;
- set-like collections **sorted** by stable IDs;
- semantically ordered arrays preserve order;
- no build-machine absolute paths;
- no generated timestamps in behavior identity;
- authored Unicode strings are preserved.

## 15. Canonicalization and digest rules

All semantic hashes use **SHA-256** with versioned algorithms.

### 15.1 Source digest

For each canonical UTF-8 source file:

1. reject invalid UTF-8;
2. remove an optional UTF-8 BOM;
3. normalize CRLF/CR **line endings** to LF;
4. preserve all other characters and whitespace;
5. hash the resulting bytes.

The bundle `source_digest` hashes a **sorted** list of `{logical_path, file_sha256}` encoded as canonical JSON. Source formatting/comments can therefore change `source_digest` without changing runtime meaning.

### 15.2 Canonical JSON

JSON-compatible normalized objects use RFC 8785 JSON Canonicalization Scheme semantics: deterministic property ordering, no insignificant whitespace, UTF-8 output and preserved JSON string values. The design calls this **canonical JSON**.

### 15.3 Profile semantic digest

`semantic_digest` is SHA-256 of canonical JSON over the behavior/publication-affecting **profile semantic projection**. It includes:

- stable `profile_id` and semantic contract/schema versions;
- expected parent component-manifest semantic identity;
- dependency definitions;
- ontology locks/target pins;
- mapping semantic records/digests;
- executable/review readiness rules;
- applicability and publication semantics.

`profile_version` must not affect `semantic_digest`. Release-navigation labels, rationale prose, local paths, CI IDs, build **timestamps**, generated-at fields and MCP transport/session metadata also **must not affect** it.

Exact bundle identity is the tuple **profile_id + profile_version + semantic_digest** plus the release artifact digests. Thus two release labels can refer to identical semantic content while remaining distinct immutable release artifacts.

A separate `ir_digest` may cover non-volatile evidence/documentation metadata for exact build reproduction.

## 16. Versioning and exact-parent rebase

SemVer is a release-navigation convention; `semantic_digest` is exact semantic identity.

- **patch** — release/tooling/rationale correction with unchanged `semantic_digest` and unchanged supported runtime behavior;
- **minor** — additive backward-compatible semantic capability;
- **major** — removal or behavior-changing alteration of an existing released mapping/executable contract.

An **exact-parent rebase** means publishing a new exact tested parent component manifest while mappings and dependency semantics remain unchanged and the complete dependency closure validates on the new parent. The parent pin changes `semantic_digest` because parent compatibility evidence is behavior-affecting, but that change **does not by itself require a major version**. SemVer impact follows user-visible semantic compatibility: normally patch/minor according to release policy, unless the rebase removes or changes supported behavior.

An ontology-lock update likewise creates a new semantic digest; SemVer impact follows resulting behavior, not the existence of a changed lock alone.

Stable `mapping_id` identifies mapping lineage; released meaning is reconstructed from the profile release plus semantic digest and mapping record.

## 17. Compiler pipeline and failures

The deterministic compiler stages are:

1. **parse** — UTF-8 YAML/JSON, reject duplicate/unsupported structures;
2. **schema validation** — JSON Schema 2020-12;
3. **cross-artifact semantic validation**;
4. **exact parent release validation**;
5. **IR normalization/canonicalization**;
6. **generated derivatives**;
7. **determinism/drift verification**.

Cross-artifact validation fails on at least:

- duplicate IDs;
- missing component/dependency/lock/evidence references;
- any active mapping dependency outside authoritative `required_components`;
- illegal assessment/external-target or ambiguity combinations;
- illegal publication relation for target formalism;
- unknown ontology target;
- explicit semantic use of dense storage empty without native evidence;
- contradictory selector/applicability metadata;
- `reviewed_mapping_digest` mismatch;
- profile data violating accepted normative TFont rules.

Release validation recomputes the exact tested parent component manifest and requires `verified-exact` for the release target.

## 18. Runtime sidecar and compatibility handoff

The first POC runtime derivative is deterministic JSON `runtime-index.json`, containing indexes such as:

- external target → approved mapping IDs;
- native selector key → mapping IDs;
- assessment → mapping IDs;
- dependency → affected mapping IDs;
- semantic domain → capability summary;
- compact provenance IDs;
- expected parent manifest/compatibility metadata.

The runtime consumes a validated bundle and loaded parent components:

```text
compute observed parent component manifest
  -> exact match: verified-exact
  -> changed identity: evaluate complete dependency closure
       -> all pass: verified-compatible
       -> incomplete: unverified
       -> known fail: incompatible
```

Runtime never rewrites canonical mappings from live ontology lookup.

## 19. Capability and resolution plan contracts

A capability record includes:

- `profile_id` / `profile_version` / `semantic_digest`;
- compatibility state;
- expected and observed component-manifest identities;
- semantic domains;
- mapping assessment support;
- ontology lock IDs;
- explicit `native-only`, `unsupported` and `ambiguous` states;
- bounded provenance/detail IDs.

A **resolution plan** contains:

- normalized-request fingerprint;
- profile identity and semantic digest;
- compatibility state/evidence ID;
- requested external concepts;
- selected mapping IDs;
- per-mapping `assessment`;
- `native_constraints` and explicit native edge/path steps;
- approximation/loss annotations;
- executability + reason codes;
- compact `provenance`;
- **resolution fingerprint**.

The resolution fingerprint is **protocol-independent** and derives from semantic request + profile semantic identity + observed compatibility evidence + native plan. It never derives from **MCP session state**, negotiated protocol, connection ID or timestamp.

## 20. Runtime execution gate

Exact-mode execution requires:

1. compatibility is `verified-exact` or `verified-compatible`;
2. every required mapping is `reviewed` and its reviewed digest matches;
3. every required assessment is `exact`;
4. no requested constraint is ambiguous/native-only/unsupported/unavailable;
5. generated native plan validates against the active adapter.

Approximate mode may explicitly allow `close`, `broader`, or `narrower` and must report loss direction:

- `broader` may under-cover the external request;
- `narrower` may over-cover the external request;
- `close` may differ extensionally either way.

`related` is not an executable substitute in the first POC. `ambiguous` must not auto-select. `unverified` and `incompatible` compatibility remain fail closed.

Stable error/result categories include `profile_not_found`, `parent_unverified`, `parent_incompatible`, `ontology_lock_missing`, `term_unknown`, `unsupported`, `ambiguous`, `approximation_required`, `unsafe_relaxation`, `native_query_invalid`, and `internal_inconsistency`.

## 21. Native-data edge cases

### 21.1 Zero-span/catalogue/native sidecar

A `zero-span-entity` / `sidecar-zero-span` selector explicitly names its non-TF component. No fake TF slot is invented. The component participates in exact identity and dependency validation.

### 21.2 Technical anchor versus semantic extent

A selector uses `extent: anchor-only` for a **technical anchor**. Semantic occurrence queries follow reviewed paths rather than pretending the anchor is full **semantic extent**.

TLHdig `lex.oslots` is the mandatory stress example.

### 21.3 Dense TF empty

A **dense TF empty** `""`/`None` storage record is non-semantic by default. The inventory/IR distinguishes raw records, non-empty nodes, empty observation count and semantic observed values.

A dense empty cannot become **explicit absence**, omission, non-attestation, damage, unknown or uncertainty unless the native source explicitly asserts that meaning.

### 21.4 Observed versus closed domain

Domain metadata distinguishes:

- **observed small domain** — finite non-empty observations in one exact release;
- **documented bounded** vocabulary — source evidence establishes bounded categories;
- closed vocabulary — only where explicit source semantics establish closure;
- open/large domain;
- unknown closure.

A finite observed release inventory is never silently promoted to permanent closure.

## 22. Generated documentation and semantic diff

The IR/source fields must generate all R-004 reference directions:

- **native -> semantic** reference;
- **semantic -> corpora** reference;
- mapping-detail pages;
- compatibility/provenance pages;
- explicit negative capability states;
- compact agent reference JSON.

Semantic diff dimensions include at least:

- **mapping assessment changed**;
- **publication relation changed**;
- **native selector/path changed**;
- ontology lock changed;
- **parent compatibility evidence changed**;
- required component/dependency change;
- review binding/readiness change;
- ambiguity candidate-projection change;
- **prose-only** change.

Generated docs expose source/profile/ontology/parent identities and never infer semantic values from dense empties.

## 23. POC fixture matrix

The first implementation fixtures must include positive and adversarial cases.

| fixture | purpose | mandatory assertion |
|---|---|---|
| BHSA positive morphology | happy path | reviewed exact `sp`/`gn`/`nu` style mapping compiles and resolves |
| changed-parent | compatibility | changed component set with complete closure → `verified-compatible` |
| changed sidecar with unchanged TF | identity negative | must not remain `verified-exact` |
| ORACC-like zero-span | non-TF semantics | zero-span component is addressed without fake slots |
| TLHdig technical-anchor | extent semantics | anchor-only does not become semantic occurrence extent |
| dense-empty | storage negative | empty record does not become semantic value/applicability |
| native-only | no-target state | no external target, non-substitute |
| unsupported | negative capability | explicit unsupported result, no blank/guess |
| ambiguous relation | ambiguity | same target with different candidate assessments remains non-executable |
| stale-review | review binding | material mapping edit with old reviewed digest becomes non-executable |

## 24. Reproducible build and CI contract

For every future profile change CI must eventually:

1. validate canonical sources against schemas;
2. validate cross-artifact references and authority rules;
3. recompute mapping semantic digests and review bindings;
4. validate exact release parent manifest;
5. compile normalized IR;
6. regenerate runtime/reference/publication derivatives;
7. run generation twice or otherwise verify deterministic canonical digests;
8. fail stale committed generated artifacts;
9. execute positive and negative fixtures;
10. produce semantic diff dimensions from §22;
11. fail on unreviewed/stale-review executable mappings;
12. preserve explicit four-state compatibility evidence.

Source digest and semantic digest are both reported so formatting-only source changes are distinguishable from semantic behavior changes.

## 25. Implementation ticket decomposition

Every ticket below follows **research -> plan -> implement -> test** as applicable, with explicit **RED -> GREEN -> independent review** before merge. A ticket that changes public semantics requires a design amendment first rather than silently changing this contract.

### `I-001` — structural schemas and source validator

**Dependency order:** first.  
Create JSON Schema 2020-12 contracts for profile, parent components, ontology lock and mapping source plus parser/structural validator. Include duplicate-key and no-independent-`required` regressions.

### `I-002` — canonicalization and digest library

Depends on `I-001`.  
Implement UTF-8 source digest, RFC 8785 canonical JSON, `mapping_semantic_digest`, profile `semantic_digest`, source digest and test vectors proving `profile_version` exclusion.

### `I-003` — parent component identity

Depends on `I-001`, `I-002`.  
Implement TF/file/directory component identity and parent manifest composition. Mandatory negative: TF unchanged + required sidecar changed.

### `I-004` — cross-artifact semantic validator

Depends on `I-001`..`I-003`.  
Validate required-component authority, all eight assessment shapes, `candidate_projections`, ontology targets, native dependencies, dense-empty assertions and review-digest binding.

### `I-005` — compatibility validator/report

Depends on `I-003`, `I-004`.  
Implement `verified-exact | verified-compatible | unverified | incompatible` with complete dependency closure and changed-parent fixtures.

### `I-006` — normalized IR compiler

Depends on `I-002`, `I-004`, `I-005`.  
Compile deterministic semantic IR and semantic/source digests; reject stale review and nondeterministic ordering.

### `I-007` — runtime sidecar and capability index

Depends on `I-006`.  
Generate deterministic runtime index plus capability records including negative states and provenance.

### `I-008` — semantic resolver core

Depends on `I-005`, `I-007`.  
Implement protocol-independent resolution plans and fail-closed exact/approximate gating; no MCP transport implementation yet.

### `I-009` — generated reference and semantic diff

Depends on `I-006`, `I-007`.  
Generate native -> semantic / semantic -> corpora reference JSON/Markdown and structured semantic diff.

After each ticket: focused RED/GREEN tests, relevant full suite, then a fresh independent review of the exact head. A head change invalidates that review.

## 26. Test strategy

Tests should be contract-oriented, not implementation snapshots.

Required layers:

- schema validation positives/negatives;
- canonicalization/digest fixed vectors;
- mapping digest/review-binding stale-review regression;
- component-manifest fixed vectors;
- exact/compatible/unverified/incompatible compatibility matrix;
- ambiguous same-target/different-assessment regression;
- no-target native-only/unsupported regressions;
- zero-span/sidecar and technical-anchor fixtures;
- dense-empty and observed-vs-closed-domain negatives;
- deterministic compile: same semantic inputs => same semantic IR/runtime/reference digests;
- protocol-independent resolver plans.

No test may treat a repository version string, feature-name coincidence, TF-only digest or author confidence as proof of semantic compatibility.

## 27. Non-goals and implementation boundary

P-001 creates no production schemas, no `profiles/`, no compiler/runtime implementation, no final corpus mapping release and no MCP code changes.

After this plan is reviewed and merged, `I-001` becomes the first production ticket. Any implementation uncertainty that would change fields, authority, digest semantics, compatibility behavior or execution policy must return through a design change rather than be guessed in code.
