# P-001: foundation POC semantic profile and compiler design

**Status:** design candidate; implementation blocked until exact-head review and merge  
**Issue:** #12  
**Recorded:** 2026-09-05  
**Scope:** design only; no production schemas, profiles, compiler, resolver, or MCP implementation

## 1. Decision

The first TFont POC will use a **validated canonical source bundle compiled deterministically to a normalized semantic IR**, from which all runtime and documentation artifacts are generated.

The canonical source bundle consists of:

1. a **profile manifest**;
2. an expected **parent component manifest** covering every semantically addressable native component;
3. one or more **ontology lock** records;
4. one or more **canonical mapping source** YAML files;
5. review/evidence metadata referenced by stable IDs.

The compiler pipeline is one-way:

```text
canonical source bundle
  profile manifest
  + expected parent component manifest
  + ontology lock(s)
  + canonical mapping source YAML
  + review/evidence references
            |
            v
parse + JSON Schema 2020-12 validation
            |
            v
cross-artifact semantic validation
            |
            v
normalized semantic IR (canonical JSON model)
            |
     +------+------------------+---------------------+
     |                         |                     |
     v                         v                     v
runtime sidecar/index     reference JSON       publication output
     |                         |                 RDF/OWL/SKOS
     |                         v                     |
     |                  generated docs               |
     |                 Markdown / HTML               |
     +-------------------------+---------------------+
                               |
                               v
                    deterministic release bundle
```

The canonical source bundle is authoritative for TFont profile semantics. The normalized semantic IR and every runtime/reference/publication artifact are a **generated derivative**. Generated artifacts are never edited as semantic source.

A parent corpus is never copied into TFont. Runtime compatibility is established by recomputing the observed parent component manifest and validating exact identity or the complete dependency closure defined by the profile.

## 2. Accepted foundation dependencies

This design freezes the accepted research state below. Any material change to one of these dependencies requires explicit P-001 reconciliation before implementation contracts change.

| research | reviewed exact head | merged main commit | design dependency |
|---|---|---|---|
| R-005 empirical census | `48c8bd78d0c3a0501b2fdec6946db5df90517bdb` | `a9c4d74d4de2f9a15eb1464dce341ecd2f92f898` | native corpus evidence, dense-empty distinction, candidate mappings |
| R-001 distribution/version binding | `68b88a820f5519ad65d46b732679a6278e9ca3c9` | `a22a95084a1518882d1e3e87d10e9757121f106d` | component-aware parent identity and compatibility states |
| R-002 ontology governance | `d82e6ef2726f149f903eb43ddbfb615faf399cd5` | `a554d4fdc36c8854519064f3a7611b80efa29622` | mapping assessments, ontology locks, publication formalism |
| R-003 agent/human ergonomics | `6747379a4aa68c17c156344f3ed3b0c2cb29d423` | `02abd89b5b7d4c83027e1e8503a02eef23cab91e` | fail-closed resolver/runtime handoff and protocol independence |
| R-004 documentation architecture | `3dcadc0b32aef95ecbf6ad94f6bbc062f8c6200f` | `00a5d6b7de777074b01bb70ac425d7f187781298` | scoped authority, generated reference, semantic diff dimensions |

## 3. POC source and release layout

This ticket does not create these production directories. It specifies the layout that implementation tickets will create.

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
    parent/
      expected-components.json
    mappings/
      *.yaml
    evidence/
      *.md | *.json
    tests/
      fixtures/

ontology/
  locks/
    <lock-id>.yaml

build/                         # generated, never canonical source
  <profile-id>/
    semantic-ir.json
    runtime-index.json
    compatibility-report.json
    reference/
      index.json
      ...
    publication/
      mapping.ttl

dist/                          # generated release staging
  <profile-id>/<profile-version>/
    profile.yaml
    parent/expected-components.json
    ontology-locks/
    semantic-ir.json
    runtime-index.json
    reference/
    publication/
    ontology-snapshots/        # exact redistributable validation inputs where required
```

The central POC repository may later produce independently releasable per-profile bundles. The bundle boundary is the profile release, not the whole TFont repository revision.

## 4. Validation standards and source parsing

### 4.1 Schema dialect

Production schemas use **JSON Schema Draft 2020-12**, the current released JSON Schema dialect at design time. Every schema declares:

```json
{"$schema": "https://json-schema.org/draft/2020-12/schema"}
```

JSON Schema validates structural shape. Cross-file identities, ontology-term presence, mapping-assessment rules, compatibility closure, and semantic edge cases are enforced by a second semantic-validation phase.

### 4.2 YAML authoring constraints

Canonical mapping/profile/lock YAML is a human authoring surface, not a hashing format.

The parser must:

- decode source as UTF-8;
- reject duplicate mapping/object keys;
- reject YAML language features that cannot be represented losslessly in the JSON-compatible source model;
- preserve Unicode string values as authored; no Unicode normalization is allowed as a hidden semantic rewrite;
- convert parsed data to the JSON-compatible model before semantic validation.

YAML comments and formatting are source-review material but do not affect normalized semantic meaning.

## 5. Profile manifest contract

The POC `profile.yaml` minimally contains these machine fields:

- `schema_version` — TFont profile-manifest schema version;
- `profile_id` — stable logical profile identifier, e.g. `tfont-bhsa`;
- `profile_version` — immutable release version;
- `semantic_domains` — declared profile domains such as morphology/lexical/text-critical;
- `parent_component_manifest` — logical path/reference to the expected manifest;
- `required_components` — stable component IDs the profile may semantically address;
- `ontology_locks` — lock IDs required by mappings/publication;
- `mapping_sources` — ordered logical source files/globs included in this profile release;
- `dependency_contract_version` — version of the dependency-expression model;
- `minimum_tfont_runtime` — runtime contract version required to consume generated sidecar;
- `license` — TFont mapping/profile license metadata;
- `provenance` — source/release provenance that is non-volatile and reviewable.

Example design shape:

```yaml
schema_version: 1
profile_id: tfont-bhsa
profile_version: 0.1.0
semantic_domains: [morphology, lexical]
parent_component_manifest: parent/expected-components.json
required_components: [bhsa-tf]
ontology_locks: [olia-2026-02-04]
mapping_sources:
  - mappings/morphology.yaml
dependency_contract_version: 1
minimum_tfont_runtime: 0.1.0
license: CC-BY-4.0
provenance:
  research_baseline: foundation-2026-09-05
```

The manifest does **not** contain a mutable `latest` parent version as compatibility authority. Parent identity lives in the component manifest; reusable compatibility lives in dependency evidence.

## 6. Parent component manifest

### 6.1 Purpose

The parent component manifest is the transport-independent exact-identity record for every **semantically addressable native component** used by a profile.

Component kinds supported by the POC contract are:

- **TF payload** — the relevant `*.tf` payload set;
- **external/native sidecar** — source data outside TF that mappings address;
- **catalogue** or **zero-span** entity store — semantic entities not represented through TF slots;
- **native-adapter** artifact — executable/declarative adapter whose interpretation affects native semantics.

A profile may declare several components. Component identities must be individually auditable.

### 6.2 Manifest shape

Conceptual normalized representation:

```json
{
  "algorithm": "tfont-parent-components-sha256-v1",
  "components": [
    {
      "component_id": "bhsa-tf",
      "kind": "tf-payload",
      "identity_algorithm": "tfont-tf-files-sha256-v1",
      "content_digest": "sha256:...",
      "required": true
    }
  ]
}
```

Minimum component fields:

- `component_id` — stable ID within the profile lineage;
- `kind` — `tf-payload | native-sidecar | catalogue | zero-span-store | native-adapter`;
- `identity_algorithm` — versioned deterministic identity method;
- `content_digest` — exact content identity;
- `required` — whether absence prevents profile activation;
- `logical_locator` — optional non-authoritative path/package locator used to find installed bytes;
- `license_ref` — optional license/provenance reference where needed.

The top-level manifest includes:

- algorithm/version;
- sorted component records by `component_id`;
- manifest `content_digest` computed from canonical JSON of component semantic identity fields.

### 6.3 TF component identity

`tfont-tf-files-sha256-v1` is defined conceptually as:

1. identify the TF files that constitute the addressed payload;
2. compute SHA-256 for the exact bytes of every included file;
3. represent `{relative_logical_path, sha256}` records in sorted path order;
4. hash the canonical JSON record list.

Dense TF storage empties are still part of exact TF bytes. Their presence affects exact component identity even though they do not become semantic values.

### 6.4 File/directory sidecar identity

A file sidecar uses SHA-256 of exact bytes. A directory-like sidecar uses sorted logical relative paths plus per-file SHA-256, then canonical JSON hashing, analogous to the TF payload algorithm.

Logical machine-local absolute paths never contribute to identity.

### 6.5 Exact-identity negative invariant

If **TF bytes stay identical** but any required external/native sidecar, catalogue, zero-span store, or native-adapter component changes, the parent manifest changes and the profile **must not remain `verified-exact`**.

This regression is mandatory in the compatibility implementation ticket.

## 7. Native dependency contract

Exact identity and reusable compatibility are intentionally separate.

Each profile source defines stable dependency assertions. Mappings reference them through `native_dependencies`.

Dependency kinds for the POC include:

- component present;
- node/entity type present;
- feature present on expected native object kind;
- edge/path present with explicit direction;
- required native value present;
- value-domain predicate / allowed observed condition;
- extent interpretation (`semantic`, `anchor-only`, `source-span`, `sidecar-zero-span`);
- adapter capability/version invariant;
- source-sidecar field/path invariant.

Conceptual dependency:

```yaml
dependency_id: bhsa.word.gn.m
affects: [bhsa.word.gn.m-to-olia-masculine]
component_id: bhsa-tf
kind: feature-value
selector:
  node_type: word
  feature: gn
invariant:
  contains_value: m
```

The **complete dependency closure** for profile activation is the union of every required profile-level dependency plus all dependencies of mappings that the released profile declares active. The POC does not support silently activating only the subset that happens to validate.

## 8. Compatibility state algorithm

The compatibility validator receives:

- expected parent component manifest from the released profile;
- observed parent component manifest computed from the loaded corpus/components;
- the complete dependency contract;
- the observed native adapter/API needed to evaluate dependencies.

It produces one of exactly four states.

### `verified-exact`

Every required semantically addressable component identity exactly matches the expected component manifest used for the reviewed profile release.

The release build must previously have validated the complete dependency contract against that exact target; runtime exact identity can therefore reuse the pinned release evidence.

### `verified-compatible`

At least one required component identity differs from the expected manifest, but every dependency in the **complete dependency closure** has been successfully evaluated against the changed component set.

The compatibility report records each dependency result and the observed component identities. No feature-name or repository-version heuristic is sufficient.

### `unverified`

No required dependency is known to fail, but the validator cannot establish complete evidence, for example because:

- a required component identity cannot be computed;
- a dependency evaluator is unavailable;
- required source data are inaccessible;
- the dependency closure is incomplete.

`unverified` is diagnostic and non-executable.

### `incompatible`

At least one required dependency is evaluated and fails, or a required component is known absent/invalid.

`incompatible` is non-executable and records the failed dependency/component.

**Only `verified-exact` and `verified-compatible` are executable** in the normal semantic runtime.

Known failure takes precedence over merely incomplete evidence: if one required dependency has proven false, the result is `incompatible` even if another dependency could not be evaluated.

## 9. Ontology lock contract

Each lock pins the exact external ontology/vocabulary evidence used to validate mappings.

Minimum lock fields:

- `lock_id`;
- `ontology_id`;
- `support_tier` from accepted R-002 governance;
- `term_namespace` / stable namespace metadata;
- `release` and release status where upstream defines one;
- `source_uri`;
- `source_revision` when a repository revision is the stronger pin;
- `content_digest` for exact validated bytes;
- `retrieved_at` as provenance only, not semantic identity;
- `license` and redistribution policy;
- `snapshot_artifact` locator within cache/release bundle;
- `terms_used` or generated term index sufficient for validation/reference.

For supported normative ontology profiles, the release process must make the exact validated snapshot available offline in a content-addressed cache/release artifact when redistribution is permitted. Runtime query resolution does not fetch live ontology URLs: compiled mappings already contain reviewed target identifiers and lock identity.

External controlled vocabularies remain external unless a specific profile declares a pinned snapshot as a validation dependency.

A live namespace response never silently changes the interpretation of an existing profile release.

## 10. Canonical mapping source contract

### 10.1 Mapping identity and fields

Every canonical mapping object minimally contains:

- `mapping_id` — stable mapping-lineage ID;
- `profile_id` — owning profile;
- `native_selector` — native node/feature/value/entity/edge/path expression;
- `native_dependencies` — dependency IDs that must validate for the mapping;
- `external_target` — one external URI/CURIE or null;
- `candidate_targets` — optional candidates used only for an ambiguous reviewed state;
- `assessment` — TFont runtime/query assessment;
- `publication_relation` — optional formal publication relation/pattern, independent from assessment;
- `applicability` — node/object/domain/precondition constraints;
- `ontology_lock` — lock ID for external target/publication semantics;
- `evidence` — stable source/evidence references;
- `review` — review status and provenance;
- `rationale` — human explanation, not executable logic;
- `introduced_in` / `changed_in` release metadata when released.

Example:

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
native_dependencies:
  - bhsa.word.gn.m
external_target: http://purl.org/olia/olia.owl#Masculine
candidate_targets: []
assessment: exact
publication_relation: null
applicability:
  node_type: word
ontology_lock: olia-2026-02-04
evidence:
  - bhsa-doc:gn
review:
  status: reviewed
  review_id: review:...
rationale: >-
  Reviewed native and ontology definitions support this projection.
```

### 10.2 Native selector model

`native_selector` is declarative and corpus-specific. It may represent:

- `feature-value`;
- `node-kind`;
- `edge` with explicit direction;
- multi-step `path`;
- `sidecar-field`;
- `zero-span-entity`;
- `source-span`.

Selectors name the `component_id` from which semantics originate.

For edges/paths, each step records direction explicitly. A shared label such as `witness` is never enough to infer shared semantics.

An `extent` field is one of:

- `semantic`;
- `anchor-only` for a technical anchor;
- `source-span`;
- `sidecar-zero-span`.

This prevents TLHdig technical anchors or ORACC zero-span entities from being forced into TF containment semantics.

## 11. R-002 assessment contract in machine form

Assessment direction is always **native/source → external target**.

The eight source values and design meanings are:

- exact — external target and native/source concept are judged semantically coextensive;
- close — substantial overlap / near-equivalence without established coextensiveness;
- broader — external target is broader than the native/source concept;
- narrower — external target is narrower than the native/source concept;
- related — semantically related, not a substitute constraint;
- ambiguous — evidence does not justify one unambiguous external-target assessment;
- native-only — native/source concept is intentionally supported with no external projection;
- unsupported — active profile provides no supported semantic projection.

The **assessment and publication relation are independent** fields. `assessment: exact` does not imply `owl:sameAs`, `owl:equivalentClass`, or `skos:exactMatch`.

Validation rules:

- `exact | close | broader | narrower | related` require one `external_target` and a valid `ontology_lock`;
- `native-only` and `unsupported` have no external target and require `external_target: null`;
- `ambiguous` has `external_target: null`, is non-executable, and may record two or more `candidate_targets` for explanation;
- `publication_relation` is null unless a separately reviewed target-formalism relation is justified;
- SKOS publication predicates are legal only for genuine SKOS concepts/concept schemes under R-002 rules;
- research-stage R-005 `S/C/B/N/R/U/L` codes are evidence metadata only and cannot populate `assessment` automatically.

`ambiguous` must not become **automatically executable** through candidate ordering, label similarity, result count, or first-match behavior.

## 12. Review/readiness semantics

Canonical source may contain mappings under review, but release compilation distinguishes review readiness.

POC review states:

- `reviewed` — mapping has completed required semantic review and may participate in executable/released mapping behavior subject to assessment and compatibility;
- `provisional` — visible in authoring/diagnostic reports but not executable in released profile;
- `disputed` — retained for audit/research but not executable.

Changing native selector/path, external target, assessment, publication relation, ontology lock, or review readiness is a material semantic change requiring semantic diff and independent review.

Rationale-only prose changes are recorded but do not by themselves change executable semantics.

## 13. Normalized semantic IR

### 13.1 Purpose

The **normalized semantic IR** is the only compiler input to generated runtime/reference/publication artifacts. It is generated, deterministic, and JSON-compatible.

It contains:

- normalized profile metadata;
- expected parent component manifest identity;
- component records;
- normalized dependency definitions;
- ontology locks and term pins used by the profile;
- normalized mapping objects;
- review readiness;
- derived indexes needed for generation;
- explicit schema/IR format version.

It may contain a `documentation` section for rationale/evidence display, but behavior-affecting fields are separated from prose fields for semantic digest/diff purposes.

### 13.2 Normalization rules

Before IR serialization:

- object fields are normalized to documented field names/types;
- identifiers are validated but not case-folded unless the identifier specification requires it;
- set-like collections are **sorted** by their stable IDs;
- arrays whose order is semantically meaningful keep their order;
- no build-machine paths are embedded;
- no generated timestamps are embedded in behavior-affecting IR;
- Unicode string values are preserved as authored; the compiler does not normalize corpus/ontology strings.

## 14. Canonicalization and digest rules

The POC uses SHA-256 with explicit versioned algorithms.

### 14.1 Text source digest

For each canonical UTF-8 text source file:

1. reject an invalid UTF-8 stream;
2. remove an optional UTF-8 BOM;
3. normalize CRLF/CR **line endings** to LF;
4. preserve all other characters and whitespace;
5. hash the resulting bytes with **SHA-256**.

The source-bundle `source_digest` hashes a **sorted** list of `{logical_path, file_sha256}` records encoded as canonical JSON.

Thus review-relevant source formatting/comments can change `source_digest` even when runtime meaning does not.

### 14.2 Canonical JSON

JSON-compatible normalized objects are serialized with RFC 8785 JSON Canonicalization Scheme semantics: deterministic object property ordering, no insignificant whitespace, UTF-8 output, and preservation of JSON string values.

The design refers to this as **canonical JSON**.

### 14.3 Semantic digest

`semantic_digest` is SHA-256 of canonical JSON over the behavior/publication-affecting IR projection, including:

- profile identity/version contract fields;
- parent expected component manifest identity and dependency definitions;
- ontology locks/target pins;
- native selectors/paths;
- mapping assessment;
- publication relation;
- applicability;
- review readiness.

Pure rationale prose, generated documentation layout, local cache paths, CI run IDs, build **timestamps**, and MCP transport/session metadata **must not affect** `semantic_digest`.

A separate full `ir_digest` may cover non-volatile documentation/evidence metadata when needed for exact build reproduction.

### 14.4 Volatile metadata

`generated_at`, build host, CI run URL, temporary directory, negotiated MCP protocol, and request/session IDs may appear in surrounding build logs/manifests, but they never alter semantic identity.

## 15. Profile versioning and change classification

Profile releases use SemVer as a release-navigation convention; semantic digest remains the exact machine identity.

- **patch** — documentation/rationale/build-tool corrections that do not change `semantic_digest` or supported runtime behavior;
- **minor** — additive backward-compatible semantic capability, such as a newly reviewed mapping or additional optional publication representation;
- **major** — removal or behavior-changing alteration of an existing released mapping, native selector/path, assessment, compatibility dependency, or executable contract.

An ontology-lock update always creates a new profile release and semantic digest. Its SemVer impact follows the resulting mapping/behavior change rather than the fact of a lock update alone.

Stable `mapping_id` identifies a mapping lineage; exact released meaning is identified by profile version + semantic digest + mapping record in that release.

## 16. Generated runtime sidecar/index

The first POC runtime artifact is deterministic JSON, optimized enough for correctness before binary optimization.

`runtime-index.json` is generated from normalized semantic IR and contains indexes such as:

- external target → approved mapping IDs;
- native selector key → mapping IDs;
- semantic domain → capability summary;
- assessment → mapping IDs;
- dependency ID → affected mapping IDs;
- compact provenance IDs;
- expected parent manifest/compatibility contract metadata.

It does not contain the full parent corpus or a triplestore.

A future binary/indexed representation may replace JSON behind the same semantic IR/runtime contract without changing mapping semantics.

## 17. Compiler stages and failure behavior

The deterministic compiler has explicit stages.

### Stage 1 — parse

Read UTF-8 YAML/JSON; reject duplicate/unsupported structures.

### Stage 2 — structural schema validation

Validate profile, manifest, lock, mapping, and later IR structures against JSON Schema 2020-12.

### Stage 3 — cross-artifact semantic validation

Fail on:

- duplicate stable IDs;
- missing referenced component/dependency/lock/mapping/evidence IDs;
- illegal assessment/external-target combinations;
- illegal publication relation for the target formalism;
- unreviewed mapping marked executable;
- unknown locked ontology target;
- component references outside `required_components`;
- contradictory native selector/applicability metadata;
- explicit semantic use of a storage empty without native evidence;
- profile data that violate accepted normative TFont rules.

### Stage 4 — parent release validation

For release validation, recompute the exact tested parent component manifest and require `verified-exact`. A profile cannot be released against a parent that is merely guessed compatible.

### Stage 5 — IR normalization/canonicalization

Produce normalized semantic IR, semantic/source digests, and deterministic indexes.

### Stage 6 — generated derivatives

Generate runtime sidecar, reference JSON/docs, compatibility seed data, semantic diff input, and optional publication output.

### Stage 7 — determinism/drift verification

Regenerate and compare canonical digests. Committed generated artifacts, where policy requires committing them, must match generated output byte-for-byte after canonical generation.

## 18. Runtime compatibility handoff

The runtime consumes only a validated generated profile bundle and the loaded parent components.

Activation flow:

```text
load runtime sidecar
      |
      v
compute observed parent component manifest
      |
      +-- exact identities match expected --> verified-exact
      |
      +-- identities differ --> evaluate complete dependency closure
                                |
                                +-- all pass --> verified-compatible
                                +-- incomplete --> unverified
                                +-- known fail --> incompatible
```

Runtime never changes canonical mappings based on live ontology lookup.

## 19. Capability contract

A profile capability summary produced from the sidecar contains:

- `profile_id` / `profile_version`;
- `semantic_digest`;
- compatibility state;
- observed/expected parent component-manifest identifiers;
- semantic domains;
- requested mapping assessment states;
- ontology lock IDs;
- bounded links/IDs for detailed mapping explanation;
- explicit `native-only`, `unsupported`, and `ambiguous` states where evaluated.

Dense empty TF records never inflate semantic capability domains.

## 20. Resolution plan contract

A **resolution plan** is a deterministic generated data structure, not an MCP-session object.

Minimum fields:

- request-normalization fingerprint;
- `profile_id`, `profile_version`, `semantic_digest`;
- compatibility state and compatibility evidence ID;
- requested external targets/concepts;
- selected mapping IDs;
- per-mapping `assessment`;
- optional `publication_relation` only for explanation/publication context;
- `native_constraints` / explicit native edge/path steps;
- approximation/loss annotations;
- executability flag and reason codes;
- compact provenance;
- **resolution fingerprint**.

The resolution fingerprint is derived from canonical request semantics + semantic profile identity + observed compatibility evidence + native plan, not from an MCP session state, connection ID, timestamp, or pagination token.

This is **protocol-independent** semantic identity. The same semantic inputs must produce the same plan meaning under a handshake-era or stateless MCP host.

## 21. Runtime execution gate

Normal exact-mode execution requires:

1. compatibility is `verified-exact` or `verified-compatible`;
2. every required mapping is `reviewed`;
3. every required mapping assessment is `exact`;
4. no requested constraint is `ambiguous`, `native-only`, `unsupported`, or operationally unavailable;
5. generated native plan validates against the active adapter.

Approximate execution may explicitly allow `close`, `broader`, or `narrower`, and the resulting plan must expose the effect:

- `broader` may under-cover the external request;
- `narrower` may over-cover the external request;
- `close` may differ extensionally either way.

`related` is not an executable substitute constraint in the first POC.

`ambiguous` must not auto-select a candidate. `native-only` and `unsupported` have no external target. `unverified` and `incompatible` compatibility are fail-closed.

## 22. Runtime error categories

The first implementation should expose stable internal error/result categories that later MCP adapters can map to protocol-specific tool results:

- `profile_not_found`;
- `parent_unverified`;
- `parent_incompatible`;
- `ontology_lock_missing`;
- `term_unknown`;
- `unsupported`;
- `ambiguous`;
- `approximation_required`;
- `unsafe_relaxation`;
- `native_query_invalid`;
- `internal_inconsistency`.

These semantic categories are independent of negotiated MCP transport/protocol error representation.

## 23. Native-data edge cases

### 23.1 Zero-span and catalogue entities

A `zero-span-entity`/`sidecar-zero-span` mapping names the non-TF component explicitly. It never receives an invented slot solely to fit TF containment.

The external/native sidecar or catalogue component is included in the parent component manifest and in the mapping's `native_dependencies`.

### 23.2 Technical anchor versus semantic extent

A native selector records `extent: anchor-only` when `oslots` is technical rather than semantic. Queries for occurrences then follow reviewed edge/path dependencies instead of slot containment.

The TLHdig lexical path is the mandatory stress fixture.

### 23.3 Dense TF empty records

A **dense TF empty** (`""`/`None` storage observation) is not a semantic value by default.

The inventory/compiler distinguishes:

- raw records seen;
- nodes with non-empty values;
- empty observation count;
- semantic observed values.

An empty record cannot satisfy `Unknown`, explicit absence, omission, non-attestation, damage, or uncertainty unless the native source explicitly assigns the literal that meaning.

### 23.4 Observed versus closed domains

The source/IR domain metadata distinguishes:

- **observed small domain**;
- **documented bounded** / categorical vocabulary;
- open/large domain;
- unknown closure.

A finite observed release does not become a permanently closed vocabulary.

### 23.5 Explicit absence

Explicit absence/omission/non-attestation is represented only by a reviewed native selector/value/edge/path that the parent source documents as such. Lack of a node/value/row is not converted into an absence assertion.

## 24. Documentation/reference generation contract

The normalized semantic IR must contain enough machine data for accepted R-004 surfaces without scraping prose.

Generated indexes support:

- **native -> semantic** navigation by component/native selector/path;
- **semantic -> corpora** navigation by external target/profile;
- mapping detail pages with assessment and publication relation separated;
- compatibility/provenance pages with parent component identity and dependency evidence;
- coverage/gap pages with explicit negative states;
- ontology-lock/release references;
- stable mapping/profile links;
- compact agent reference JSON.

Every generated reference derives from the same IR used by runtime sidecar generation.

## 25. Semantic diff contract

The compiler/diff layer classifies independent change dimensions:

- mapping added/removed;
- **mapping assessment changed**;
- **publication relation changed**;
- external target changed;
- **native selector/path changed**;
- applicability changed;
- dependency contract changed;
- **ontology lock** / release changed;
- **parent compatibility evidence changed**;
- review readiness changed;
- rationale/evidence/prose-only change;
- generated-format-only change.

The semantic diff compares normalized IR/source metadata, not Markdown output.

A prose-only change may alter `source_digest` but not `semantic_digest`. A runtime/publication behavior change must alter `semantic_digest`.

## 26. Deterministic release bundle

A profile release bundle contains enough data to inspect and execute mappings offline without redistributing parent corpus data:

- profile manifest;
- expected parent component manifest;
- ontology locks;
- exact redistributable ontology snapshot artifacts required for offline validation, keyed by digest;
- normalized semantic IR;
- runtime sidecar/index;
- generated reference JSON/Markdown as chosen by implementation policy;
- optional RDF/Turtle publication artifact;
- license/attribution data;
- build manifest containing `source_digest`, `semantic_digest`, generator version, and artifact SHA-256 values.

Volatile build timestamps may be outside the signed/hashable semantic manifest. If included for human provenance, they are explicitly excluded from semantic digest computation.

## 27. POC fixture matrix

The first implementation wave must use a small fixture suite rather than full production corpora for every unit test. Integration tests can validate pinned real corpora where licensing/access permits.

### F-001 — BHSA positive morphology

A minimal BHSA-like TF fixture contains `word.gn=m` and a reviewed mapping to an OLiA masculine target.

Exercises:

- YAML mapping parse;
- ontology lock resolution;
- `assessment: exact` with `publication_relation: null`;
- `verified-exact` parent manifest;
- exact capability/resolution plan;
- native constraint generation.

### F-002 — changed-parent compatibility

Two parent fixture component sets share the native dependencies but differ in non-semantic bytes/component identity.

Exercises:

- exact target → `verified-exact`;
- **changed-parent** manifest + complete closure → `verified-compatible`;
- changed parent + missing validation evidence → `unverified`;
- changed parent + failed dependency → `incompatible`.

A subcase keeps TF bytes unchanged and changes a required sidecar to prove exact identity is lost.

### F-003 — zero-span sidecar

An ORACC-like fixture stores a catalogue/zero-span entity in a sidecar rather than TF slots.

Exercises:

- **zero-span** component identity;
- sidecar dependency;
- selector without invented slot extent;
- reference generation.

### F-004 — technical-anchor path

A TLHdig-like fixture has a `lex` node whose slot is a **technical-anchor**, with occurrences available only through a reviewed analysis→lexeme→lex path.

Exercises explicit direction/path resolution and rejects containment-only interpretation.

### F-005 — dense-empty negative

A dense feature exposes empty storage records on nodes where no semantic value exists.

Exercises **dense-empty** exclusion from capability domains, applicability, and explicit-absence semantics.

### F-006 — native-only / unsupported

A source-local conversion/editorial concept has no external target, plus a requested semantic concept with no native support.

Exercises both **native-only** and **unsupported** no-target records and fail-closed resolver behavior.

## 28. Test strategy by layer

### Schema tests

- valid minimum object;
- missing/unknown fields;
- illegal enum combinations;
- duplicate IDs/keys;
- external-target requirements by assessment.

### Canonicalization tests

- CRLF vs LF source normalization;
- source comments/formatting affect source digest but not semantic digest when semantics unchanged;
- key ordering does not alter canonical JSON digest;
- Unicode strings preserved exactly;
- timestamps/build paths/session IDs do not affect semantic digest;
- deterministic generation twice yields same artifact bytes/digests.

### Compatibility tests

- exact component identity;
- TF-equal/sidecar-different loses exactness;
- complete closure permits `verified-compatible`;
- incomplete evidence is `unverified`;
- failed dependency is `incompatible`;
- zero-span/native-adapter dependencies participate.

### Mapping validation tests

- all eight assessments;
- no-target states;
- ambiguous candidate handling;
- assessment/publication relation independence;
- illegal SKOS/OWL formalization rejected;
- unreviewed mapping non-executable;
- R-005 evidence code cannot populate assessment automatically.

### Resolver-core tests

- exact BHSA fixture;
- approximate gating/direction warnings;
- no silent constraint drop;
- native path direction;
- no session/protocol metadata in resolution fingerprint;
- semantic search adapter later executes the exact returned plan.

### Documentation/diff tests

- native→semantic and semantic→corpora indexes derive from same IR;
- negative states explicit;
- mapping assessment/publication relation display independently;
- semantic diff categories stable;
- generated reference cannot drift from IR.

## 29. Implementation ticket decomposition

The design deliberately splits production work. Every implementation ticket follows RED → confirm intended failure → minimal GREEN → relevant full suite → **independent review** of the exact final head.

### Dependency order

```text
I-001 schemas + source validator
        |
        v
I-002 canonicalization + normalized semantic IR
        |
        +-------------------+
        v                   v
I-003 parent identity   I-004 ontology lock + mapping semantics
      + compatibility          validator
        |                   |
        +---------+---------+
                  v
            I-005 compiler + runtime sidecar
                  |
          +-------+--------+
          v                v
I-006 resolver core   I-007 generated reference + semantic diff
          |                |
          +-------+--------+
                  v
          I-008 Context-Fabric/MCP adapter
                  |
                  v
          I-009 first real BHSA POC profile
```

### `I-001` — source schemas and validator

Creates JSON Schema 2020-12 contracts for profile manifest, parent component manifest, ontology lock, mapping source, and basic cross-file ID validation. No runtime resolution.

Primary RED cases: illegal assessment/target combinations, duplicate IDs, missing dependencies/locks.

### `I-002` — canonicalization and normalized semantic IR

Implements YAML→validated JSON-compatible model, normalization, RFC 8785 canonical JSON, source/semantic digests, and IR schema.

Primary RED cases: source formatting vs semantic digest, deterministic ordering, volatile timestamp/session exclusion.

### `I-003` — parent component identity and compatibility validator

Implements TF/file/directory component identities, parent component manifest, complete dependency closure, and four compatibility states.

Primary RED cases: TF unchanged + sidecar changed; compatible changed parent; unverified incomplete evidence; failed dependency.

### `I-004` — ontology-lock and mapping semantic validator

Implements pinned ontology snapshot lookup, target presence, assessment semantics, publication-relation formalism checks, review readiness, and no-target rules.

Primary RED cases: OLiA OWL target with manufactured SKOS predicate; ambiguous auto-selection; native-only external target; unreviewed executable mapping.

### `I-005` — deterministic profile compiler and runtime sidecar

Compiles validated normalized IR into runtime index/reference seed artifacts and release build manifest.

Primary RED cases: repeat build equality, generated drift detection, indexes consistent with IR.

### `I-006` — resolver core

Implements capability lookup and deterministic resolution plan independent of MCP.

Primary RED cases: exact BHSA request, approximate fail-closed behavior, broader/narrower warning direction, unsupported/ambiguous/no-target handling, protocol-independent resolution fingerprint.

### `I-007` — generated reference and semantic diff

Implements R-004 reference JSON/Markdown and semantic diff dimensions from normalized IR.

Primary RED cases: negative states explicit; assessment/publication split; native/semantic bidirectional links; prose-only vs semantic change.

### `I-008` — Context-Fabric/MCP adapter

Exposes `semantic_capabilities`, `semantic_resolve`, and `semantic_search` on top of resolver core while preserving native `search()` behavior.

Primary RED cases: native search unchanged; search executes resolver plan exactly; handshake-era and 2026 stateless negotiated transports preserve equivalent semantic resolution semantics.

### `I-009` — first real BHSA POC profile

Authors and validates a minimal reviewed BHSA profile using real pinned native evidence and supported ontology locks. This is the first corpus mapping release candidate, not part of the schema/compiler infrastructure tickets.

Primary RED cases: selected positive mappings, native-only/unsupported negatives, exact parent binding, generated reference and end-to-end semantic query.

No implementation ticket may bypass an earlier dependency merely because equivalent ad-hoc fields can be hard-coded locally.

## 30. Non-goals for P-001

This design PR itself must not create:

- production `schemas/`;
- production `profiles/`;
- a `src/` runtime package;
- a released ontology snapshot;
- production corpus mappings;
- Context-Fabric/MCP code;
- a triplestore runtime.

Only this plan, its characterization tests, and its read-only CI validation workflow belong in P-001.

## 31. Acceptance trace

- Accepted R-001…R-005 exact heads/merge commits are pinned in §2.
- One canonical source → validation → IR → runtime/reference/publication flow is fixed in §1.
- Profile, component manifest, ontology lock, mapping, dependency, IR, runtime and reference responsibilities/fields are defined in §§5–17 and 24–26.
- Component-aware exact/reusable compatibility and all four states are defined in §§6–8.
- All eight R-002 assessments, native/source→target direction and publication separation are fixed in §§10–11.
- Deterministic source/canonical JSON/SHA-256 digest rules and version semantics are fixed in §§14–15.
- Fail-closed runtime handoff is fixed in §§18–22.
- Zero-span/sidecar, technical anchor, dense empty, observed-vs-bounded domain and explicit absence are fixed in §23.
- R-004 documentation/reference and semantic-diff inputs are fixed in §§24–25.
- Concrete positive/adversarial fixtures are defined in §27.
- Test strategy is in §28.
- The required **implementation ticket decomposition** and **dependency order** are fixed in §29, with explicit RED/GREEN/independent-review expectations.
- P-001 contains no production implementation by §30 and CI characterization tests enforce that boundary.

## 32. Design sources

Foundation research sources are the accepted R-001 through R-005 artifacts pinned above.

External technical specifications selected for implementation contracts:

- JSON Schema Draft 2020-12, current released JSON Schema specification at design time: `https://json-schema.org/draft/2020-12`;
- RFC 8785 JSON Canonicalization Scheme for deterministic canonical JSON: `https://www.rfc-editor.org/rfc/rfc8785.html`.

Implementation tickets may research library choices, performance and platform behavior, but they must not silently change these semantic/data contracts. A required contract change goes back through design review.
