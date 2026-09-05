# R-004: documentation architecture and generated reference design

**Status:** research complete as a draft; final merge is blocked on reconciliation with accepted R-001/R-002/R-003/R-005  
**Issue:** #4  
**Recorded:** 2026-09-05

## Decision

TFont should use a **source-first, generated-reference documentation architecture**.

The canonical semantic mapping data must not be duplicated manually into prose tables. Human-readable reference pages, agent-facing capability indexes, RDF publication views, coverage tables and compatibility matrices should be generated from the same validated mapping/profile source that the runtime consumes. Hand-authored documentation explains architecture, scholarly rationale, workflows and examples; it does not become a second source of mapping truth.

The POC should publish three documentation surfaces from one repository:

1. **normative project documentation** — architecture, mapping/governance rules and versioning contracts;
2. **scholarly/user guides** — explanations, tutorials, mapping methodology and contribution/review guidance;
3. **generated semantic reference** — exact per-profile, per-native-feature and per-ontology-concept documentation derived from machine-readable profile sources and locks.

A static documentation site should be built from committed Markdown plus generated Markdown/JSON. Plain repository Markdown remains usable without the site. The POC should use a conventional static-site generator such as MkDocs rather than invent a custom documentation application; the exact theme is not a semantic contract.

The source-of-truth rule is deliberately strict:

> If generated documentation and canonical mapping/profile data disagree, the generated documentation is wrong and CI must fail. If hand-authored prose makes a mapping claim that disagrees with canonical mapping data, the prose is wrong and must be corrected; prose never silently overrides the mapping.

## 1. Research execution plan

This research followed four steps.

1. Inspect documentation patterns in the standards and corpus ecosystems TFont depends on: OLiA, CIDOC CRM, OntoLex, Text-Fabric/BHSA, Context-Fabric and Agora.
2. Separate four kinds of information that are easy to conflate: native corpus facts, TFont mapping assertions, normative project rules and explanatory prose.
3. Design bidirectional human/agent navigation over those layers without duplicating mapping rows.
4. Turn the result into an exact repository layout and CI drift contract suitable for the first POC design ticket.

This is a research-only ticket. It does not introduce production schemas, a site generator, runtime code or corpus mappings.

## 2. Evidence and useful prior patterns

### 2.1 OLiA: separate native annotation models, reference terminology and links

OLiA documents three conceptually distinct artifacts:

- Annotation Models formalize an individual corpus/tagset;
- the Reference Model provides shared linguistic terminology;
- Linking Models state the mappings between the two.

The public site separately documents the architecture, available models and instructions for building new annotation/linking models. The OWL artifacts remain machine-readable sources while the website gives humans overview and navigation.

This is directly relevant to TFont: a BHSA native feature/value must remain distinguishable from the external OLiA concept to which TFont maps it, and the mapping assertion itself is another object with provenance and strength.

Inspected sources:

- <https://acoli-repo.github.io/olia/>
- <https://acoli-repo.github.io/olia/models.html>
- <https://acoli-repo.github.io/olia/overview.html>

### 2.2 CIDOC CRM: explicit release/status documentation

CIDOC CRM publishes version-specific specification documents and a release index that distinguishes **Official**, **Stable** and **Draft** model versions. As of 2026-09-05, CRM 7.1.3 is the official ISO-correspondence release while 7.4, published in August 2026, is marked Draft. Compatible extension families likewise publish their own version/status tables.

Two lessons matter for TFont documentation:

1. a user must be able to see the exact ontology release/status against which a profile was reviewed, rather than only a timeless ontology name;
2. `latest` is useful navigation but must not replace immutable release identity in provenance.

Inspected sources:

- <https://cidoc-crm.org/versions-of-the-cidoc-crm>
- <https://cidoc-crm.org/Version/version-7.4>
- <https://cidoc-crm.org/crminf/fm_releases>

R-002 remains authoritative for which exact ontology releases TFont will support; this ticket only defines how those choices are documented.

### 2.3 OntoLex: modular specification and optional profiles

OntoLex documents a minimal core plus optional modules such as VarTrans and Lexicog. Lexicog explicitly recommends using the simpler OntoLex model when additional dictionary-specific structure is unnecessary.

TFont should mirror that documentation ergonomically: a profile page should state its active semantic modules rather than forcing a user to read documentation for every ontology in the global supported set.

Inspected sources:

- <https://ontolex.github.io/ontolex/specification.html>
- <https://ontolex.github.io/lexicog/>

### 2.4 Text-Fabric and BHSA: native feature pages are useful but must remain native

Text-Fabric exposes feature metadata through the corpus API even when a feature is not loaded. BHSA publishes human feature pages containing:

- feature name;
- native description;
- applicable node types;
- value/code tables;
- corpus-specific notes and cautions.

Examples inspected:

- <https://etcbc.github.io/bhsa/features/sp/>
- <https://etcbc.github.io/bhsa/features/gn/>
- <https://etcbc.github.io/bhsa/features/nu/>
- <https://etcbc.github.io/bhsa/features/vs/>
- <https://etcbc.github.io/bhsa/features/vt/>
- <https://etcbc.github.io/bhsa/features/otype/>
- <https://annotation.github.io/text-fabric/tf/core/fabric.html>

This native documentation is evidence, not something TFont should copy wholesale. TFont reference pages should link to native documentation and show the TFont projection beside it.

A particularly important example is BHSA `vs`: the native page itself warns that the Hebrew/Aramaic stem division and functions need clarification. TFont documentation must preserve such uncertainty; a generated semantic page must not make the external mapping look more certain than its evidence.

### 2.5 Context-Fabric MCP: progressive disclosure

R-003 inspected Context-Fabric MCP at `Context-Fabric/context-fabric@3a38ca80e617d872ce1664e0f0740486d0e7e8ac`. The MCP already separates corpus discovery, feature discovery and actual search. TFont documentation should support the same progressive-disclosure principle:

- compact agent capability metadata by default;
- native/mapping details on request;
- full rationale and references only when requested.

The docs site should therefore not be the only machine interface. It should publish a compact generated JSON reference that mirrors the conceptual capability data used by the semantic resolver.

### 2.6 Agora: normative architecture separate from generated marketplace data

Agora keeps a normative architecture boundary in hand-authored documentation while registry/generated artifacts are machine-managed. That separation is useful for TFont as well.

The ownership rule remains:

- TFont documents semantic mappings and their scholarly evidence;
- Context-Fabric documents native query execution/MCP behavior;
- Agora documents discovery/install/integration metadata;
- parent corpus repositories document their own native semantics.

TFont may link to those sources but must not fork their mutable documentation into its own prose.

## 3. Four information layers that documentation must not collapse

### 3.1 Native corpus facts

Examples:

- BHSA `sp=subs` is a native feature/value;
- CUC `emen` and `cert` are independent source/editorial features;
- TLHdig-TF `lexeme` is an `analysis -> lex` edge;
- Pseudepigrapha-TF `witness` links a reading to a manuscript.

Authority: parent corpus artifact and its documentation.

TFont records the exact native selector/path necessary to identify the fact, but does not redefine it.

### 3.2 TFont mapping assertions

Examples:

- native `sp=subs` maps to an external noun concept with relation `exact`;
- a corpus-specific verbal-stem value has no approved cross-language external equivalent and is `native-only`;
- two witness-like relations are only `related`, not interchangeable.

Authority: canonical TFont mapping source for the exact profile version.

Every assertion needs a stable mapping ID, relation strength, source/target, applicability, review state and evidence/rationale reference.

### 3.3 Normative TFont rules

Examples:

- `related` mappings are never executable substitutions by default;
- generated docs never override canonical mapping data;
- a stale parent-schema binding fails closed.

Authority: approved architecture/specification documents produced through the design gate.

Normative documents define interpretation rules for mapping data; they should not enumerate every corpus mapping row.

### 3.4 Explanatory/research prose

Research documents, tutorials and essays explain why a decision exists and preserve rejected alternatives and unresolved questions.

Authority: historical/explanatory only. A research note may motivate a mapping change but does not activate it.

## 4. Source-of-truth hierarchy

The POC should use the following precedence.

| rank | artifact | authority |
|---:|---|---|
| external | parent corpus artifact/docs | native corpus semantics and native values |
| external | ontology release/specification | external term semantics |
| 1 | canonical TFont mapping source | TFont mapping assertions and strengths |
| 2 | profile manifest | profile identity, parent compatibility, release coordinates and artifact digests |
| 3 | ontology lock | exact tested ontology namespaces/releases/digests/status |
| 4 | approved TFont normative specs | how mappings/manifests/locks are interpreted |
| derived | compiled runtime index | deterministic derivative of ranks 1-3 |
| derived | RDF/Turtle/JSON semantic export | deterministic publication derivative |
| derived | generated reference Markdown/HTML/JSON | deterministic documentation derivative |
| explanatory | guides/research/release prose | explanation; never overrides semantic source |

Ranks 1-3 must be mutually consistent and validated together. “Rank” does not mean a manifest can redefine a mapping; each artifact has a non-overlapping responsibility.

### Conflict rules

- **mapping source vs generated reference:** generation bug/drift; CI fails;
- **mapping source vs runtime index:** compiler/cache bug; runtime bundle invalid;
- **mapping source vs hand-authored guide:** guide bug; fix prose;
- **mapping source vs external corpus evidence:** substantive mapping defect; mapping must be reviewed/revised;
- **mapping source vs ontology definition:** substantive mapping defect or ontology-version mismatch; fail review/activation;
- **manifest vs actual parent artifact:** compatibility failure; profile must not activate normally.

## 5. Exact POC repository layout

R-001 recommends a central source repository with independently releasable corpus profiles. Documentation should fit that structure rather than invent another hierarchy.

```text
TFont/
├── AGENTS.md
├── CONTRIBUTING.md
├── profiles/
│   ├── bhsa/
│   │   ├── manifest.yaml              # future canonical profile metadata
│   │   ├── mappings/                  # future canonical mapping source
│   │   ├── notes/                     # optional long scholarly notes, linked by IDs
│   │   └── tests/
│   ├── cuc/
│   ├── syriac/
│   ├── peshitta/
│   ├── syrnt/
│   ├── extrabiblical/
│   └── tlhdig-tf/
├── ontology/
│   ├── lock.yaml                      # future exact external ontology locks
│   └── local/                         # future TFont-local ontology terms if R-002 permits
├── schemas/                            # future machine contracts after design
├── docs/
│   ├── research/                       # R-XXX evidence/recommendations
│   ├── plans/                          # P-XXX design artifacts
│   ├── architecture/                   # approved stable normative docs after POC design
│   ├── guides/                         # hand-authored user/scholar/contributor guides
│   │   ├── querying.md
│   │   ├── mapping-review.md
│   │   └── versioning-and-provenance.md
│   ├── reference/                      # GENERATED; do not hand edit
│   │   ├── index.json                  # compact machine navigation index
│   │   ├── profiles/
│   │   │   └── <profile-id>/
│   │   │       ├── index.md
│   │   │       ├── compatibility.md
│   │   │       ├── coverage.md
│   │   │       └── native/
│   │   ├── concepts/
│   │   │   └── <stable-concept-key>.md
│   │   ├── mappings/
│   │   │   └── <stable-mapping-id>.md
│   │   └── ontologies/
│   │       └── <ontology-id>.md
│   └── releases/
│       └── <profile-id>/               # hand prose + generated semantic-diff section
├── scripts/
│   └── ...                             # future generator/validator tooling
└── tests/
    └── ...
```

The exact canonical YAML filenames remain a design decision. The **documentation directories and source/derived distinction** should survive that decision.

## 6. What is hand-authored and what is generated

### Hand-authored

- research reports and rejected alternatives;
- approved normative architecture/specification prose;
- tutorials/cookbooks;
- contribution and review guidance;
- long-form scholarly notes that cannot fit cleanly in a mapping assertion;
- release narrative describing scholarly intent/change context.

Long-form notes must be linked from a stable mapping ID. They may elaborate rationale but cannot change machine semantics.

### Generated

- profile reference index;
- compatibility table from manifest bindings;
- native feature/value -> semantic mapping tables;
- semantic concept -> corpus/native realization tables;
- mapping-detail pages;
- coverage/gap reports;
- mapping-strength counts;
- ontology term/version pages for terms actually used;
- license/provenance summaries that are already present in locks/manifests;
- machine `reference/index.json`;
- semantic mapping diff for releases;
- RDF/Turtle/JSON publication exports;
- optional generated TF-module documentation.

### Hybrid release notes

A release note may contain hand-written motivation plus a generated semantic diff. The generated section must be visibly delimited and reproducible.

## 7. Bidirectional navigation model

A user must be able to start from either side.

### 7.1 Native -> semantic

Example path:

```text
profile: bhsa@0.1.0
  native: word / sp=subs
    -> mapping ID: bhsa.word.sp.subs
      -> external concept
      -> relation: exact/close/...
      -> applicability
      -> rationale/evidence
      -> tests
```

The generated native page should show:

- exact parent corpus/version/revision;
- node/edge kind and direction;
- native feature/value description from the pinned inventory plus link to upstream docs;
- every applicable TFont mapping assertion;
- mapping strength and review status;
- mapping ID and profile version;
- no misleading “universal label” when no mapping exists.

### 7.2 Semantic -> corpora

Example path:

```text
concept: olia:<noun-concept>
  -> BHSA: exact -> word sp=subs
  -> ExtraBiblical: exact/verified independently -> native selector
  -> Syriac: exact/close according to reviewed profile -> native selector
  -> Peshitta: unsupported in inspected TF release
  -> CUC: unsupported
```

The generated concept page must distinguish:

- supported exact;
- executable approximate under an explicit policy;
- ambiguous;
- native-only related distinctions;
- unsupported;
- profile unavailable/incompatible.

An empty cell is forbidden where a profile has been evaluated. Empty means documentation failure, not semantic absence.

### 7.3 Mapping-detail page

One stable mapping ID gets one generated detail page showing:

- source profile and native selector/path;
- target term URI/CURIE;
- relation strength;
- applicability conditions;
- evidence/rationale;
- review status;
- profile/ontology/parent version locks;
- tests/fixtures exercising it;
- first-introduced and last-changed profile release;
- links to both native and semantic indexes.

## 8. Stable identifiers and URLs

Human labels change. URLs and anchors must therefore be derived from stable identifiers, not page titles.

Rules:

1. Every mapping assertion has a stable mapping ID independent of repository hosting path.
2. Every profile has a stable logical profile ID independent of GitHub organization/repository.
3. External concepts are keyed by full URI internally; generated pages use a deterministic encoded key/CURIE only as a filesystem/URL convenience.
4. Page anchors use stable IDs, not generated heading slugs.
5. A `/latest/` or unversioned site view may exist for navigation, but provenance links in query results point to an immutable profile release/version.
6. Redirects may preserve renamed documentation paths, but old release artifacts themselves remain immutable.

Recommended public page identity is conceptually:

```text
/reference/<profile-id>/<profile-version>/...
/reference/concepts/<stable-concept-key>/
/reference/mappings/<stable-mapping-id>/
```

The deployment hostname is not part of the semantic identity.

## 9. How mapping strength and uncertainty appear

The UI/reference vocabulary should use the same machine states as the resolver wherever possible:

- `exact`
- `close`
- `broader`
- `narrower`
- `related`
- `ambiguous`
- `native-only`
- `unsupported`
- `incompatible` / unavailable profile

Color may supplement but never replace these words.

Every approximate mapping shows a short consequence statement such as:

```text
Relation: broader
Effect on query: executing this mapping may include native cases outside the requested concept.
Default exact mode: not executable.
```

Do not hide approximate mappings behind a generic “mapped” badge.

### Evidence uncertainty versus mapping strength

These are separate fields.

A mapping can be semantically `exact` relative to a native category whose upstream interpretation is itself marked uncertain. The generated page must surface both:

- mapping relation;
- evidence/native-documentation caveat.

This matters for BHSA verbal stems and many historical-language categories.

## 10. Provenance block on every generated profile/mapping page

Minimum compact provenance:

```text
TFont profile:      tfont-bhsa 0.1.0
Parent corpus:      ETCBC/bhsa 2021
Parent revision:    <exact tested commit>
Schema fingerprint: <digest>
Mapping source:     <source digest/revision>
Ontology lock:      <lock ID/digest>
Target ontology:    <term URI + tested release/status>
Mapping relation:   exact
Review status:      reviewed / provisional / disputed
Generated by:       <generator version>
```

Where licensing is relevant, include:

- mapping artifact license;
- ontology license/reference policy;
- parent corpus license link;
- restrictions on generated/materialized data if any.

A profile page may summarize parent/ontology licensing once; mapping pages can link to that summary unless a particular term/source has exceptional licensing.

## 11. Agent-facing documentation

Humans need narrative pages; agents need bounded structured discovery.

The generated `docs/reference/index.json` should be a **navigation/capability index**, not a dump of the entire ontology or all mappings.

Conceptual top level:

```json
{
  "schema_version": 1,
  "generated_from": "<source digest>",
  "profiles": {
    "bhsa": {
      "version": "0.1.0",
      "parent": {"id": "ETCBC/bhsa", "version": "2021", "revision": "..."},
      "semantic_domains": ["morphology", "syntax", "lexical"],
      "coverage_url": "...",
      "concept_index_url": "..."
    }
  }
}
```

Detailed mapping rows are fetched by mapping/concept/profile ID when needed.

R-003's provisional ergonomic target of a small default capability payload should constrain this design. The static reference JSON can be richer than a single MCP response, but it must support selective lookup rather than require loading one giant file.

## 12. Human-facing documentation

### First page for a corpus scholar

A profile landing page should answer, without ontology expertise:

- Which corpus release is this mapping for?
- Which kinds of questions are interoperable?
- Which native distinctions remain local?
- Which mappings are approximate/disputed?
- How do I query it through TFont/Context-Fabric?
- How do I inspect the exact native constraints?

### First page for an ontology/linked-data user

A concept page should answer:

- Which TFont corpus profiles map to this concept?
- With what relation strength?
- What native feature/value/node/edge realizes it?
- What corpus/version was tested?
- What evidence/reviewer status supports the assertion?

### First page for a contributor

Contribution docs should explain:

1. find the native corpus evidence;
2. find/verify the external ontology definition/version;
3. change canonical mapping source;
4. add/adjust positive and negative semantic fixtures;
5. run validation/generation;
6. inspect semantic diff and generated docs;
7. obtain independent skeptical review.

## 13. Concrete documentation prototypes

These examples are **documentation shapes**, not final R-002 ontology decisions.

### 13.1 BHSA POS and agreement

Generated native entry:

```text
BHSA / word / sp=subs
Native meaning: noun/substantive according to BHSA documentation
Applies to: word and lex where present in the pinned schema
TFont mapping: <external noun concept>
Relation: candidate exact, subject to accepted R-002 mapping policy
Evidence: BHSA sp feature documentation + pinned corpus inventory
Native query: word sp=subs
```

`gn=f` and `nu=pl` should have analogous pages. A combined guide example may show a semantic query resolving to:

```text
word sp=subs gn=f nu=pl
```

but the generated reference remains one mapping assertion per reviewed native semantic unit.

### 13.2 BHSA `vt` and `vs`: do not over-document English labels

BHSA `vt=perf` is natively labelled “perfect”; `vs=qal` is a Hebrew verbal stem. Documentation must not silently turn those labels into universal `PastTense` or a cross-language “basic stem”.

Until R-002 approves an external projection, a generated page may state:

```text
Native concept: BHSA verbal form/stem value
External mapping: native-only / unresolved
Reason: language-specific analysis; no reviewed equivalence
```

That is useful documentation, not a deficiency to hide.

### 13.3 Syriac

For the primary `ETCBC/syriac` 0.9 profile, generated pages should expose `sp`, `gn`, `nu`, `ps`, `st`, `vs`, `vt`, lexical `lex/gloss` and morpheme families from the exact inventory.

A second page for SyrNT demonstrates why profile identity matters: SyrNT `sp=noun`, `nu=p`, `st=emphatic`, roots/stems and separate `lexeme` nodes are native structures with different value vocabularies even when high-level concepts overlap.

The semantic concept page can show both realizations without pretending the schemas are aliases.

### 13.4 CUC editorial and physical semantics

A CUC page for `cert` must document it separately from `emen` and `alt`.

```text
Native selector: sign cert=<observed value>
Semantic family: editorial certainty
Not equivalent to: emendation state; alternative reading
```

The exact observed domains should be generated from the accepted R-005 inventory, not typed manually into this guide.

Physical pages should separately document `tablet`, `column`, `line`, `side` and sign-slot semantics.

### 13.5 TLHdig-TF lexical relation

A generated edge page should make direction and extent semantics explicit:

```text
Native edge: lexeme
Direction: analysis -> lex
Meaning: this analysis resolves to the lexical (lemma, gloss) entity
Semantic attestation extent: use analysis/lexeme relation and occurrence paths
Caution: lex.oslots is a technical anchor, not the lexeme's full occurrence extent
```

This caution should be emitted from profile semantics, not buried only in a tutorial.

### 13.6 TLHdig-TF editorial cluster

For `cluster`, documentation should show range semantics (`startsAt`, `endsAt`, offsets, width, type) and distinguish the cluster entity from derived sign flags such as `missing`.

### 13.7 ExtraBiblical versus BHSA

When both profiles map a shared ETCBC-family relation such as a grammatical feature or `mother` edge to the same external concept, the semantic concept page still shows two separately reviewed assertions and two parent bindings.

Shared feature spelling is evidence for reuse investigation, not proof that one mapping row can silently cover both corpora.

### 13.8 Deliberately local-only example

TLHdig-TF `cu_aligned` is an alignment-evidence mechanism with levels/methods specific to that conversion. It should be visible in the native reference and capability/gap view even if no external ontology term is suitable.

```text
Mapping status: native-only
Why retained: required to assess sign-level cuneiform evidence quality
External projection: none approved
```

This demonstrates that TFont documentation values native distinctions rather than treating unmapped categories as failures.

## 14. Static site versus Markdown versus JSON

Use all three, with one build graph.

### Repository Markdown

Required because:

- works in GitHub/code review;
- versioned with source;
- readable offline;
- no hosting dependency.

### Static site

Recommended because:

- cross-links and search make the generated reference usable;
- concept/native bidirectional navigation is cumbersome in raw directory browsing;
- pages can expose tables, warnings and provenance consistently.

A conventional generator such as MkDocs is sufficient for the POC. Site HTML should be treated as a build product; source Markdown/JSON is the reviewable artifact.

### JSON reference

Required for agents/tooling and to avoid scraping HTML. JSON reference files are generated from the same normalized semantic intermediate representation as Markdown/RDF.

No format is manually synchronized with another.

## 15. Documentation ownership boundaries

| information | authoritative owner | TFont action |
|---|---|---|
| meaning of BHSA/CUC/TLHdig native feature | parent corpus | link and identify exact native selector/version; do not rewrite as authority |
| mapping native selector -> ontology term | TFont | document fully, including strength/evidence/review |
| ontology term definition | ontology project | link URI/release; cache lock metadata, not copied normative definition |
| semantic query/resolution contract | TFont design/runtime | normative TFont architecture + generated API reference |
| native Context-Fabric query syntax | Context-Fabric | link; TFont examples show generated native template but do not fork syntax manual |
| profile discovery/install coordinates | Agora/TFont distribution metadata | link/show compatibility coordinates; do not duplicate marketplace implementation docs |
| corpus data-quality caveat | parent corpus or TFont mapping evidence where relevant | link authoritative source; only record the consequence for a TFont assertion |

## 16. CI drift and release contract

A documentation build is part of semantic validation, not a cosmetic afterthought.

For every profile/mapping PR, CI should eventually perform:

1. validate canonical mapping source against schema;
2. validate profile manifest and ontology lock;
3. validate exact parent corpus binding/schema requirements;
4. compile one deterministic normalized semantic intermediate representation;
5. generate runtime sidecar, RDF/JSON exports and reference Markdown/JSON from that IR;
6. run generation twice or otherwise verify deterministic output/digests;
7. fail if `git diff --exit-code` shows committed generated reference is stale;
8. build the static documentation site in strict mode;
9. fail broken internal links and duplicate/stale stable anchors;
10. verify generated pages carry source/profile/ontology/parent fingerprints;
11. run representative documentation assertions for required examples (`sp=subs`, CUC editorial distinction, TLHdig technical-anchor caution, etc.);
12. produce a **semantic diff** that separately reports mapping relation changes, native selector changes, compatibility changes and prose-only changes;
13. require a release note/review attention when semantic API changes occur even if generated prose still builds;
14. ensure generated files carry a clear generated/do-not-edit marker.

The implementation should follow TDD after the design gate. This research ticket specifies the observable contract only.

## 17. Semantic diff as documentation

Ordinary text diff is not enough for mapping review.

A generated semantic diff should classify at least:

- mapping added/removed;
- relation strengthened/weakened (`close -> exact`, `exact -> close`);
- native selector/path changed;
- external ontology term changed;
- parent compatibility changed;
- ontology lock/release changed;
- review status changed;
- rationale/prose-only change.

This diff should feed both PR review and release notes. A relation-strength change is a public semantic behavior change even if no Python code changes.

## 18. Documentation of unsupported semantics

Unsupported capability must be explicit when the profile has evaluated the concept/domain.

Generated coverage tables should distinguish:

- **not evaluated** — mapping research has not decided;
- **unsupported** — corpus cannot answer the semantic request from available native data;
- **native-only** — relevant native distinction exists but lacks an approved external projection;
- **ambiguous** — several incompatible projections exist;
- **incompatible** — profile cannot activate for this parent version.

This prevents an agent/human from treating absence of a row as evidence of absence in the corpus.

## 19. Documentation versioning

### Profile-scoped reference

Generated semantic reference is versioned with the **TFont profile release**, not only with the parent corpus version.

A stable profile page records both:

```text
TFont profile version  -> semantic assertion set
Parent corpus revision -> native evidence target
Ontology lock           -> external terminology target
```

### Current/latest view

A site may expose a convenient current view, but every page should display and link its immutable profile version. Query provenance must reference immutable identifiers.

### Historical mappings

Do not rewrite old release reference pages when ontology projects deprecate terms. Publish migration/deprecation notices in new profile releases and retain old provenance.

## 20. Documentation review criteria

An independent reviewer should be able to answer:

1. Can I reconstruct every displayed semantic mapping from canonical source?
2. Does every native selector link back to exact corpus/version evidence?
3. Are approximate/native-only/unsupported states visible rather than normalized away?
4. Is mapping review status distinct from ontology standard status and parent corpus status?
5. Are technical TF anchors/implementation details prevented from masquerading as semantic extents?
6. Can both a corpus scholar and ontology user navigate to the same mapping assertion from opposite directions?
7. Does a changed semantic assertion produce an obvious semantic diff/release impact?
8. Is any mutable upstream documentation copied in a way that TFont would have to maintain as a fork?
9. Can the reference be used offline from a released profile bundle?
10. Do generated and runtime artifacts identify the same source/lock/parent digests?

## 21. Rejected alternatives

### Hand-maintain per-corpus mapping tables in Markdown

Rejected. They become a second semantic database and will drift from runtime mappings.

### RDF/Turtle as the documentation source

Rejected as a documentation architecture requirement. RDF remains valuable publication/interchange, but R-003 found it inferior as the sole human mapping-review surface. Generated docs should derive from the canonical mapping source chosen by design.

### Generate everything, including tutorials and research rationale

Rejected. Generated reference is excellent for facts already in mapping/manifest data but poor for scholarly argument, rejected alternatives and pedagogical explanation.

### Put all documentation into the parent corpus repositories

Rejected as default. TFont profiles release independently and may use ontology stacks the parent project does not adopt. Link upstream native docs instead.

### Put semantic mapping documentation in Agora

Rejected. That violates Agora's thin marketplace boundary and would turn registry documentation into a semantic fork.

### One giant generated JSON file containing every mapping and ontology term

Rejected for agent ergonomics and incremental loading. Publish a compact index plus profile/concept/mapping detail resources.

### Version docs only by parent corpus version

Rejected. Mapping semantics and ontology locks can change independently of parent data.

### Use labels/headings as persistent URLs

Rejected because names and preferred labels change. Stable IDs drive anchors/paths.

## 22. Unresolved design questions

The first POC design must still decide:

1. exact canonical mapping serialization/schema (R-003 provisionally recommends YAML + JSON Schema);
2. whether generated reference Markdown is committed or generated only in release/site builds; recommendation here is to commit it during the POC for reviewability, then revisit repository size after measurement;
3. exact static-site generator/configuration;
4. exact stable URI namespace for TFont-local mappings/concepts;
5. how much upstream feature metadata to cache in generated pages versus link dynamically;
6. exact schema for `reference/index.json` and concept/mapping detail JSON;
7. how semantic diff integrates with GitHub review/check summaries;
8. how reviewer identity/provenance is represented without making a forge account part of semantic identity;
9. whether profile release reference is hosted centrally, inside per-profile release bundles, or both;
10. retention policy for generated reference from unsupported historical profile releases.

None of these reopen the source-of-truth hierarchy or generated-reference principle.

## 23. Acceptance-criteria trace

- **Source-of-truth hierarchy:** defined in §4 with explicit conflict rules.
- **Exact POC documentation layout:** defined in §5.
- **Generated versus authored:** defined in §6 and throughout the build contract.
- **Bidirectional navigation:** native -> semantic and semantic -> corpora defined in §7, with stable mapping-detail pages.
- **Mapping strength, unsupported semantics, provenance, licenses and compatibility:** §§9-10, §18-19.
- **TFont versus Context-Fabric/Agora/parent ownership:** §15.
- **Agent and scholar surfaces:** §§11-12; compact JSON plus human static/Markdown reference.
- **Update/release/CI drift:** §§16-17 and §19.
- **Required concrete examples:** BHSA, Syriac, CUC, TLHdig-TF, ExtraBiblical and a local-only case in §13.

## 24. Dependency reconciliation rule

R-004 may be researched in parallel, but final merge must use the accepted conclusions of the other foundation research.

Before final independent review:

- replace provisional mapping-status examples if R-002 changes the supported relation vocabulary;
- reconcile directory/release terminology if accepted R-001 changes profile distribution;
- reconcile agent JSON/progressive-disclosure requirements if accepted R-003 changes its ergonomics contract;
- regenerate/adjust native examples against accepted R-005 inventories and terminology.

Material reconciliation invalidates any earlier review of this draft.

## 25. Sources

Primary sources inspected for this research:

- OLiA documentation architecture and models: <https://acoli-repo.github.io/olia/>, <https://acoli-repo.github.io/olia/models.html>, <https://acoli-repo.github.io/olia/overview.html>
- CIDOC CRM release/status documentation: <https://cidoc-crm.org/versions-of-the-cidoc-crm>
- OntoLex core specification and Lexicog module: <https://ontolex.github.io/ontolex/specification.html>, <https://ontolex.github.io/lexicog/>
- Text-Fabric feature metadata API: <https://annotation.github.io/text-fabric/tf/core/fabric.html>
- BHSA native feature documentation: <https://etcbc.github.io/bhsa/features/0_home/>, individual feature pages cited above
- Context-Fabric MCP at `Context-Fabric/context-fabric@3a38ca80e617d872ce1664e0f0740486d0e7e8ac`
- Agora normative plugin boundary at `alexsosn/Agora` (`wiki/architecture/ref-plugin-boundary.md`)
- TFont R-001 distribution research / PR #8
- TFont R-002 ontology-governance research / PR #9
- TFont R-003 ergonomics research / PR #10
- TFont R-005 empirical corpus census / PR #7
