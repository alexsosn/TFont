# R-003: agentic and human ergonomics for semantic interoperability

**Status:** research complete as a draft; merge is blocked on independent acceptance of R-005 (#7)  
**Issue:** #3  
**Recorded:** 2026-09-05

## Decision

TFont should expose a **hybrid semantic workflow**:

- semantic discovery and resolution are explicit, inspectable operations;
- a convenience semantic-search operation may execute the same deterministic resolution plan;
- ordinary Context-Fabric `search()` remains a native-corpus tool and must not silently reinterpret ontology terms;
- every semantic execution returns the native constraints, mapping strength, provenance and any semantic losses together with the results.

The POC should add a very small semantic tool surface on top of Context-Fabric MCP rather than duplicate the corpus API:

1. `semantic_capabilities` — compact discovery of available TFont profiles/concepts for one or more loaded corpora;
2. `semantic_resolve` — turn a corpus-neutral concept expression into a per-corpus native query plan without executing it;
3. `semantic_search` — resolve and execute through the existing Context-Fabric search engine, returning both the resolution plan and results.

`semantic_resolve` should also serve detailed explanation through a `detail`/`explain` option. A fourth `semantic_explain` tool is not justified for the POC unless later testing shows that the combined resolver response becomes too large or awkward.

The default semantic mode is **fail closed**:

- no dropping unsupported conjuncts;
- no automatic use of `close`, `broader`, `narrower` or `related` mappings in a query that requested exact semantics;
- no automatic cross-language equivalence based on labels;
- no stale mapping execution;
- no guessed corpus feature names;
- no conversion of “no value” into “explicit absence” unless the source asserts absence.

An agent can explicitly request approximate mappings, but the response must identify which parts were widened or narrowed and require that choice to be visible in the final execution plan.

For human authors, TFont should use **one canonical declarative source format, YAML validated by JSON Schema**, with generated RDF/Turtle, JSON and browsable tables as derived artifacts. Generated formats are not independently editable and are never round-tripped back into YAML. This keeps code review readable while preserving standards-oriented publication.

## 1. Research basis

### 1.1 Current Context-Fabric MCP

The inspected implementation is:

- repository: `Context-Fabric/context-fabric`
- revision: `3a38ca80e617d872ce1664e0f0740486d0e7e8ac`
- `cfabric-mcp`: `0.1.7`
- Context-Fabric core at the same revision: `0.5.7`

The MCP server exposes eleven tools in three layers.

**Discovery**

- `list_corpora`
- `describe_corpus`
- `list_features`
- `describe_feature`
- `get_text_formats`

**Search**

- `search`
- `search_continue`
- `search_csv`
- `search_syntax_guide`

**Data access**

- `get_passages`
- `get_node_features`

The server instructions already recommend progressive disclosure: inspect corpus structure, browse relevant features, inspect sample values, then search. `search(return_type="count")` and `statistics` provide token-efficient alternatives to retrieving full result sets.

This architecture is a good base for TFont. Semantic support should remove repeated schema-discovery work when the user requests a known semantic concept while preserving the ability to inspect the native feature layer.

### 1.2 MCP protocol behavior relevant to the design

The current MCP specification family supports structured tool results and output schemas. The 2026-07-28 protocol release expanded JSON Schema support and formalized a more stateless/cachable core. Tool-level domain failures are intended to be returned as tool errors (`isError=true`) so an agent can self-correct, rather than as successful results whose text merely says something failed.

Tool annotations remain hints rather than security contracts. TFont's semantic tools should be advertised as read-only and idempotent where the client/protocol version supports these annotations, but correctness must be enforced inside the resolver rather than delegated to model instructions or annotation hints.

MCP server instructions are useful for concise cross-tool workflow guidance. They should explain relationships such as “resolve before executing approximate cross-corpus semantics,” but must not contain the ontology manual or be relied on to enforce semantic safety.

### 1.3 R-001 and R-002 constraints

R-001 recommends a version-bound semantic sidecar over native TF/Context-Fabric data. R-002 recommends explicit mapping relations and stable ontology locks.

The ergonomic API therefore has to expose three layers without confusing them:

1. native corpus facts;
2. TFont mapping assertions and their strength/provenance;
3. the resolved query plan that combines those assertions for a particular request.

The API must never present layer 3 as though it were a native feature of the parent corpus.

Compatibility uses R-001's evidence-bearing states: `verified-exact`, `verified-compatible`, `incompatible`, and `unverified`. Only the first two are executable in the normal semantic API. `unverified` is diagnostic and **non-executable**; there is no normal execution escape hatch. Capability/explanation output should expose the parent artifact identity and dependency evidence that produced the state.

R-005 `S/C/B/N/R/U/L` values are research-stage **candidate** relations, not approved runtime mappings. A candidate `S` **cannot** activate runtime `exact`. Runtime strengths such as `exact`, `close`, `broader`, or `narrower` exist only for an **approved** profile mapping after ontology-term selection and review under R-002.

## 2. Agent workflow

### 2.1 Minimum workflow

For a semantic request against one corpus:

```text
semantic_capabilities(corpus, concepts=optional)
        ↓
semantic_resolve(expression, corpus)
        ↓
semantic_search(expression, corpus)
```

The first call may be skipped when the agent already has a fresh capability summary for the exact corpus/profile revision. The third call may be replaced by native `search(template=resolved_template)` when the agent deliberately wants direct control over the final Context-Fabric query.

For a multi-corpus request:

```text
semantic_capabilities(corpora=[...], compare=true)
        ↓
semantic_resolve(expression, corpora=[...], semantic_mode="exact")
        ↓
inspect per-corpus statuses/losses
        ↓
semantic_search(...) or native search per accepted plan
```

The resolver, not the LLM, decides whether each requested concept can be expressed by the active mapping.

### 2.2 Discovery

`semantic_capabilities` answers questions such as:

- does this loaded corpus have a compatible TFont profile?
- which ontology profiles are active?
- which concept families can be queried?
- which requested concepts are exact, approximate, ambiguous or unsupported?
- which native node types are involved?
- is the mapping compatible with the currently loaded corpus revision?

It should not dump every mapping row by default.

Conceptual request:

```json
{
  "corpora": ["bhsa", "syriac"],
  "concepts": [
    "olia:Noun",
    "olia:Feminine",
    "olia:Plural"
  ],
  "compare": true
}
```

Conceptual compact response:

```json
{
  "corpora": {
    "bhsa": {
      "profile": "tfont-bhsa@0.1.0",
      "compatibility": "verified-exact",
      "concepts": {
        "olia:Noun": {"status": "exact"},
        "olia:Feminine": {"status": "exact"},
        "olia:Plural": {"status": "exact"}
      }
    },
    "syriac": {
      "profile": "tfont-syriac@0.1.0",
      "compatibility": "verified-exact",
      "concepts": {
        "olia:Noun": {"status": "exact"},
        "olia:Feminine": {"status": "exact"},
        "olia:Plural": {"status": "exact"}
      }
    }
  }
}
```

The actual URIs are determined by R-002/design work; labels above are illustrative.

### 2.3 Resolution

`semantic_resolve` accepts a semantic expression and returns a **plan**, not corpus results.

The POC expression model should remain intentionally small. At minimum it needs:

- concept/category constraints;
- conjunction (`AND`);
- optional disjunction where each branch is explicit;
- target object kind where necessary (`Word`, `LexicalEntry`, `Sign`, etc.);
- corpus selection;
- semantic mode (`exact`, `allow-close`, `allow-broader`, or explicit relation allowlist).

Do not build a second general query language before the POC demonstrates a need. Structural ordering/containment remains Context-Fabric search syntax; semantic resolution supplies the native nodes/features/values that participate in that syntax.

Conceptual response:

```json
{
  "resolution_id": "r_01...",
  "requested": ["olia:Noun", "olia:Feminine", "olia:Plural"],
  "semantic_mode": "exact",
  "corpora": {
    "bhsa": {
      "status": "resolvable",
      "native_target": "word",
      "native_constraints": [
        {"feature": "sp", "operator": "=", "value": "subs"},
        {"feature": "gn", "operator": "=", "value": "f"},
        {"feature": "nu", "operator": "=", "value": "pl"}
      ],
      "template": "word sp=subs gn=f nu=pl",
      "losses": []
    }
  }
}
```

The mapping must determine the native constraints. The agent must not invent `gender=feminine` merely because those English names seem plausible.

### 2.4 Resolution statuses

Every requested semantic unit has one of these statuses:

- `exact` — selected mapping is exact under TFont's reviewed mapping policy;
- `close` — selected `skos:closeMatch`-like relation;
- `broader` — query target is broader than requested;
- `narrower` — query target is narrower than requested;
- `related` — semantic relation exists but is not suitable as a substitute constraint;
- `ambiguous` — more than one incompatible mapping candidate is available;
- `unsupported` — no usable mapping exists;
- `unavailable` — profile/corpus/ontology lock is not loadable or compatible;
- `native-only` — corpus records a relevant native distinction with no approved external projection.

`related` is informational and never executable as substitution by default.

A full query plan also has one aggregate status:

- `resolvable` — every required constraint is usable under requested semantic mode;
- `partial` — at least one required constraint cannot be applied; **not executable by default**;
- `ambiguous` — multiple plans remain; not executable until one is selected;
- `incompatible` — mapping/corpus version contract failed;
- `unsupported` — the corpus cannot answer the requested semantics.

### 2.5 Dense storage records are not semantic values

R-005 shows that dense Text-Fabric features may expose empty-string/`None` records. These are storage/API records with **no semantic value** unless a source explicitly defines the literal as meaningful. They must not appear in semantic capability domains and must not make a feature look **applicable** to a node type by themselves.

Capability/coverage reporting therefore distinguishes `nodes_with_value` from raw records encountered. `semantic_resolve` cannot map an empty-string/`None` record to `Absent`, `Unknown`, `Omitted`, `Unattested`, damage, uncertainty, or another **explicit absence** concept without a reviewed native source assertion. Diagnostic output may report empty-record counts separately.

### 2.6 No silent widening

If the user requests `Noun AND Feminine AND Plural` and a corpus supports only `Noun AND Plural`, TFont must not execute the two supported constraints and omit gender.

The response should say, structurally:

```json
{
  "status": "partial",
  "unsupported": ["olia:Feminine"],
  "would_match_if_relaxed": ["olia:Noun", "olia:Plural"],
  "execution_allowed": false
}
```

If a caller intentionally wants the relaxed query, it submits a new expression or an explicit relaxation policy. The resulting plan records that relaxation.

### 2.7 Ambiguity

When a corpus-native category maps to multiple candidates without a reviewed preference, TFont returns the alternatives with rationale/provenance. It does not choose the candidate that happens to yield more results.

Ambiguity is a planning state, not a search statistic.

## 3. Hybrid execution model

### 3.1 Why not implicit resolution inside ordinary `search()`

Ordinary Context-Fabric search syntax is intentionally native:

```text
word sp=verb vt=perf
```

Allowing arbitrary ontology labels to appear in the same feature/value grammar would create several problems:

- it becomes unclear whether `sp`/`verb` are native or semantic aliases;
- stale mappings could change the meaning of an otherwise native template;
- error messages would mix corpus syntax errors and ontology resolution failures;
- an agent could believe a semantic alias was a real corpus feature;
- exact and approximate mappings would be hard to expose before execution.

Therefore native `search()` remains semantically transparent.

### 3.2 Why not explicit resolution only

Requiring every ordinary semantic question to call a resolver, manually copy a native template and then call `search()` creates avoidable tool-call overhead and opportunities for the agent to alter the plan incorrectly.

A convenience `semantic_search` is justified if it:

1. calls the same deterministic resolver;
2. refuses a non-executable plan under the requested semantic mode;
3. returns the plan together with results;
4. exposes the generated native search template;
5. offers the same result modes as Context-Fabric where feasible (`count`, `results`, `statistics`, `passages`).

This yields the hybrid recommendation.

### 3.3 No hidden second implementation

`semantic_search` must not contain a separate mapping engine. Tests should prove that, for the same inputs/profile revision:

```text
semantic_search(...).resolution
== semantic_resolve(...)
```

except for ephemeral identifiers/timestamps.

The native query executed by semantic search must be byte-for-byte or structurally identical to the plan it returns.

## 4. Capability reporting contract

### 4.1 Corpus-level summary

A capability summary contains:

- corpus ID;
- loaded parent corpus revision/version/schema fingerprint;
- TFont mapping/profile ID and version;
- compatibility state;
- active ontology locks/profile IDs;
- supported semantic domains (`morphology`, `lexical`, `syntax`, `graphemic`, `text-critical`, `material`, etc.);
- counts of exact/approximate/native-only/unsupported mapping assertions;
- optional warning flags;
- a cache/provenance fingerprint.

It does not need all individual mappings unless requested.

### 4.2 Concept-level lookup

A concept lookup contains:

- ontology URI and human label;
- mapping relation/strength;
- native target node type;
- native feature/value or edge/path description;
- applicability conditions;
- ambiguity state;
- mapping review status;
- profile version;
- ontology lock/release;
- parent corpus binding;
- source/rationale references when detail is requested.

### 4.3 Cross-corpus comparison

Comparison should align **capabilities**, not merely feature names.

Example conceptual table generated from structured results:

| semantic request | BHSA | Syriac | Peshitta |
|---|---|---|---|
| noun | exact | exact | unsupported in this TF version |
| feminine | exact | exact | unsupported |
| plural | exact | exact | unsupported |
| witness metadata | unsupported | unsupported | native-only A/B witness designation |

The absence of morphology in Peshitta 0.2 is a useful answer. TFont should not fill the gap from another Syriac corpus.

## 5. Explainability and provenance

Every successful semantic resolution must be explainable without reading source code.

### 5.1 Minimum provenance on compact responses

A compact resolved plan includes stable identifiers for:

- parent corpus identity/version/revision;
- TFont profile and mapping version;
- ontology term URI;
- tested ontology lock/release;
- mapping relation/strength;
- native feature/value/edge path used;
- resolution ID/fingerprint.

This should be enough to reproduce the request later.

### 5.2 Full explanation

With `detail="full"` or equivalent, expose:

- mapping assertion ID;
- human rationale;
- source evidence/documentation link;
- review status;
- mapping author/reviewer provenance where recorded;
- applicability conditions;
- transformation chain from semantic expression to native template;
- any approximation or loss;
- mapping/ontology/corpus digests.

### 5.3 Results do not erase the plan

A semantic search returning 10,000 results must still report how the query was resolved. Pagination cursors may refer back to a stable resolution ID so the full plan is not repeated on every page.

A later page must never continue against a different profile revision from the first page.

## 6. Human authoring strategy

### 6.1 Canonical source: YAML

Turtle alone is not the preferred authoring UI for the POC. Mapping reviews routinely need to inspect corpus IDs, native feature/value constraints, mapping strengths, applicability, rationale, provenance and tests. YAML gives concise diffs and comments while remaining machine-readable.

The canonical file is validated by JSON Schema and uses stable mapping IDs.

Conceptual example:

```yaml
id: bhsa.word.sp.subs
corpus: bhsa
native:
  node_type: word
  feature: sp
  value: subs
semantic:
  term: http://purl.org/olia/olia.owl#CommonNoun
  relation: exact
applicability:
  parent_version: "2021"
review:
  status: reviewed
rationale: >-
  BHSA documents sp=subs as substantive/common noun in this mapping context.
sources:
  - docs/features/sp.md
```

This is illustrative; exact schema belongs to later design work.

### 6.2 Generated formats

From canonical YAML, tooling may generate:

- RDF/Turtle publication;
- compact runtime sidecar/index;
- JSON API fixtures;
- Markdown/HTML reference tables;
- coverage/gap reports;
- optional materialized TF features where R-001 permits them.

Generated artifacts carry a source digest and a visible `generated; do not edit` marker.

### 6.3 One-way generation only

Do not support YAML ↔ Turtle bidirectional editing in the POC.

Reasons:

- comments/rationale formatting cannot round-trip cleanly;
- RDF graph serialization order is not meaningful and causes noisy diffs;
- two editable sources create merge/conflict ambiguity;
- a generated RDF graph can contain inferred/normalized statements that should not be reverse-engineered into authoring syntax.

A contributor proposing an RDF-only mapping can use an import/conversion utility later, but the converted YAML is reviewed as a new canonical source before merge.

## 7. Human inspection and CLI ergonomics

The later implementation should provide conceptual commands equivalent to:

```text
tfont validate

tfont coverage bhsa

tfont explain bhsa native:word.sp=subs

tfont explain bhsa ontology:http://purl.org/olia/...

tfont diff --from tfont-bhsa@0.1.0 --to tfont-bhsa@0.2.0
```

Exact CLI spelling is deferred, but required behaviors are not.

### 7.1 `validate`

Reports:

- schema errors;
- missing ontology-lock terms;
- invalid mapping relations;
- parent corpus incompatibility;
- duplicate/conflicting mapping IDs;
- undeclared ambiguities;
- generated-artifact drift;
- stale tests/fixtures if mapping source changed without expected snapshot changes.

The exit code is non-zero on any release-blocking error.

### 7.2 `coverage`

Shows:

- mapped native features/values/nodes/edges;
- exact vs approximate mapping counts;
- native-only semantics;
- known gaps;
- optional profile coverage;
- unreviewed assertions.

Coverage percentages must state their denominator. “90% mapped” is meaningless unless the report says 90% of which native values or assertions.

### 7.3 `explain`

Supports both directions:

- native → external concepts;
- external concept → native realizations in one or several corpora.

The same explanation data should power CLI output, generated docs and MCP detailed responses.

### 7.4 `diff`

A semantic diff distinguishes:

- added/removed mapping;
- relation changed (`exact` → `close`, etc.);
- native constraint changed;
- ontology term/release changed;
- parent corpus compatibility changed;
- rationale-only/documentation change.

Relation or native-constraint changes are material and invalidate prior independent review of that mapping PR.

## 8. Error model

Errors need stable machine codes plus concise human text.

Suggested conceptual categories:

| code | meaning | default behavior |
|---|---|---|
| `TFONT_PROFILE_NOT_FOUND` | corpus has no TFont profile | tool error; suggest capability/native discovery |
| `TFONT_PARENT_MISMATCH` | loaded corpus revision/schema does not match profile | tool error; do not resolve |
| `TFONT_ONTOLOGY_LOCK_MISSING` | required pinned ontology snapshot unavailable | tool error |
| `TFONT_TERM_UNKNOWN` | requested ontology term not known in active locks | tool error or capability miss |
| `TFONT_UNSUPPORTED` | corpus cannot express required semantics | non-executable resolution result; semantic_search raises tool error |
| `TFONT_AMBIGUOUS` | multiple unresolved mappings | non-executable resolution result |
| `TFONT_APPROXIMATION_REQUIRED` | only non-exact mapping can satisfy request | non-executable in exact mode |
| `TFONT_UNSAFE_RELAXATION` | execution would need dropping/widening required constraint | tool error |
| `TFONT_NATIVE_QUERY_INVALID` | generated native template rejected by Context-Fabric | internal/profile defect; tool error with mapping ID |
| `TFONT_INTERNAL_INCONSISTENCY` | semantic_search plan differs from resolver plan | hard error; never return results |

For MCP, expected tool failures should use the protocol's error result signaling rather than a normal successful response containing a string beginning with “Error”.

Protocol-level errors remain reserved for malformed/unsupported MCP requests rather than semantic domain failures.

## 9. Token and tool-call efficiency

Semantic interoperability is only useful to agents if discovery does not flood context.

### 9.1 Progressive disclosure

Default `semantic_capabilities` responses include profile/domain summaries and only requested concept statuses. Full mapping tables require explicit filtering/pagination.

Default `semantic_resolve` responses include executable constraints, mapping strength and compact provenance; full rationale/source records require `detail="full"`.

`semantic_search` reuses Context-Fabric's efficient return modes:

- use `count` to establish cardinality;
- use `statistics` for distributions;
- paginate results;
- do not inline thousands of matches.

### 9.2 Measurable targets

The later implementation tests should target:

- one-corpus capability summary ≤ **8 KiB serialized JSON** by default;
- requested concept lookup returns ≤ **20 candidate mappings** per concept unless paginated/explicitly expanded;
- an exact single-corpus semantic query with a known loaded profile requires **at most two semantic tool calls** (`semantic_resolve` + `semantic_search`) after corpus selection; capability discovery may be an earlier cached call;
- a typical multi-corpus comparison requires **one capabilities call + one resolver call** before execution;
- pagination results reference a resolution ID rather than repeating full rationale/ontology metadata on every page;
- server instructions describing the semantic workflow should remain short enough to function as workflow guidance, not a mapping manual;
- no tool response includes a complete ontology or complete corpus mapping unless explicitly requested through a bounded export/debug path.

These limits are POC targets and should be benchmarked with real profiles; material deviations require an explicit ergonomics decision rather than unbounded payload growth.

### 9.3 Structured output

TFont MCP tools should declare output schemas and return structured results suitable for both model consumption and deterministic client/UI rendering.

Stable fields such as `status`, `relation`, `native_constraints`, `profile`, `provenance` and `errors` must not need to be parsed from prose.

The text content, when present for compatibility, should summarize rather than duplicate enormous structured payloads.

### 9.4 Tool annotations

Where supported by the negotiated MCP version:

- `readOnlyHint=true`;
- `destructiveHint=false`;
- `idempotentHint=true` for pure capability/resolution calls;
- `openWorldHint=false` when resolution uses only locally pinned corpus/profile/ontology data.

If a future tool reaches external ontology services dynamically, that tool has a different open-world trust profile and must be advertised accordingly. The R-001/R-002 offline-lock design should make such network access unnecessary for ordinary query resolution.

## 10. Adversarial agent cases

### 10.1 Plausible but wrong feature names

Request: “Find feminine plural nouns in BHSA.”

Bad agent behavior:

```text
word part_of_speech=noun gender=feminine number=plural
```

Required TFont behavior:

- resolve semantic concepts against mapping;
- return actual native features/values (`sp`, `gn`, `nu` and reviewed values);
- expose generated template;
- never claim the English feature names exist in BHSA.

### 10.2 False stem equivalence

Request: compare Hebrew `qal` and Syriac `peal` as “the same stem.”

Required behavior:

- preserve the two native categories;
- return the reviewed relation, which may be broader/related/close rather than exact;
- exact mode refuses to substitute one for the other unless R-002 mapping review explicitly established exactness;
- agent receives a warning suitable for final scholarly reporting.

### 10.3 Silent constraint dropping

Request: `Noun AND Feminine AND Plural` across BHSA and Peshitta 0.2.

R-005 shows Peshitta 0.2 lacks the required morphology.

Required behavior:

- BHSA: resolvable if mapping supports all categories;
- Peshitta: unsupported/partial;
- do not search “all Peshitta words” or silently search only a surviving subset of constraints.

### 10.4 Stale parent corpus

A profile was validated against BHSA 2021 at parent revision X; loaded corpus has revision Y with a changed schema fingerprint.

Required behavior:

- compatibility state `unverified`/`mismatch`;
- resolver refuses normal execution;
- response reports expected and observed parent identity/version/digest;
- an explicit developer override may exist later, but must be visible and must not produce a normal `verified` provenance record.

### 10.5 Missing ontology term

A mapping lock references a term removed from the locally pinned ontology snapshot.

Required behavior:

- profile validation fails before normal query use;
- resolver does not dynamically fetch a newer ontology and continue;
- error names mapping assertion and ontology lock.

### 10.6 `sentence` label trap

Request a cross-corpus “sentence” query over BHSA and ORACC-TF.

R-005 shows ORACC `c type=sentence` chunks are implicit source chunks and are not equivalent to BHSA linguistic sentences.

Required behavior:

- exact comparison is rejected unless a separate reviewed semantic mapping says otherwise;
- capability view exposes ORACC's native chunk semantics;
- no feature-name/otype-name matching heuristic is allowed.

### 10.7 Lexeme extent trap

Request corpus-wide lexeme occurrences in BHSA and TLHdig-TF.

R-005 shows BHSA `lex` `oslots` can express occurrence extent, whereas TLHdig `lex` uses a technical one-slot anchor and occurrence relation via `analysis -> lexeme -> lex`.

Required behavior:

- resolver chooses the corpus-specific relation path;
- does not implement the TLHdig query as slot containment under the `lex` node;
- explanation exposes the path difference.

### 10.8 Witness trap

Request: “Which manuscripts attest this reading?”

- Pseudepigrapha-TF can model reading-to-manuscript witness semantics;
- Peshitta `witness=A/B` is a different assertion;
- TLHdig line-to-fragment `witness` is another relation.

Required behavior:

- Pseudepigrapha may resolve the text-critical request;
- Peshitta/TLHdig report native witness-related capabilities but do not claim the same query semantics;
- absence of a reading-witness mapping remains unsupported rather than inferred.

## 11. Evaluation tasks over the required corpora

### 11.1 BHSA vs ExtraBiblical Hebrew

Task: query an exact high-level morphological category available in both, then inspect whether the generated native feature/value constraints coincide.

Acceptance focus:

- reuse is based on reviewed mappings, not shared ETCBC ancestry;
- differences in lexical-node structure remain visible;
- semantic results report each parent corpus/profile independently.

### 11.2 BHSA vs Syriac

Task: `Noun + Feminine + Plural` and a lexical-entry query.

Acceptance focus:

- high-level morphology may resolve exactly where definitions fit;
- language-specific verbal stems do not inherit equivalence;
- SyrNT explicit lexeme structure and ETCBC Syriac word-level lexical features may produce different native plans for the same high-level lexical concept.

### 11.3 CUC vs TLHdig-TF

Task: locate sign-level textual entities inside physical line/document structure and inspect editorial/damage capabilities.

Acceptance focus:

- both use sign slots but their higher-level structures and editorial models remain distinct;
- `Sign`/`Line` mappings do not imply that `tablet` and `document` are equivalent;
- damage/emendation uncertainty cannot be flattened into one boolean.

### 11.4 ORACC-TF vs TLHdig-TF vs biblical corpus lexical layer

Task: ask for lexical entries/attestations.

Acceptance focus:

- same semantic goal can resolve to different node/edge paths;
- technical `oslots` anchors are never mistaken for corpus-wide attestation extents;
- native form/gloss/language information is reportable alongside the projection.

### 11.5 No exact cross-linguistic mapping

Task: request a language-specific Hebrew stem and apply it to Syriac.

Acceptance focus:

- resolver returns `unsupported` or reviewed approximate relationship;
- exact mode has zero executable Syriac plan;
- approximate mode records the relation and user/agent choice.

### 11.6 Pseudepigrapha text-critical metadata

Task: retrieve readings and their witness attestations, then ask the same semantic capability of Peshitta/TLHdig.

Acceptance focus:

- source-specific apparatus graph is preserved;
- explicit witness absence is distinguished from unknown/no record;
- similarly named witness fields/edges in other corpora are not substituted.

## 12. Human documentation and visual inspection

Generated documentation should offer at least four views:

1. **native → semantic** — corpus feature/value/node/edge to external/local concepts;
2. **semantic → corpora** — a concept and how each corpus realizes or fails to realize it;
3. **coverage/gaps** — exact, approximate, native-only, unsupported and ambiguous counts;
4. **mapping detail** — rationale, provenance, compatibility, tests and change history.

Mapping strength should be represented both textually and visually, but color alone must not carry meaning. Tables should say `exact`, `close`, `broader`, etc.

An unresolved gap is a first-class documentation state, not an empty table cell.

Examples should always show the generated/native feature constraints. A tutorial that says “query Feminine” without showing `gn=f` (or the corresponding corpus-specific realization) would hide the evidence layer that TFont is meant to make inspectable.

## 13. Contribution and review workflow

A mapping change PR should include:

1. research/source evidence if the semantic interpretation is new or contested;
2. canonical YAML change;
3. a regression test or characterization fixture showing native resolution;
4. generated artifact update/check;
5. coverage/semantic diff;
6. author-side validation;
7. independent skeptical review of the final head.

The reviewer should check both directions:

- does the external concept actually fit the native corpus assertion?
- does the mapping cause a semantic query to match native cases it should not?

Changes from `exact` to `close` or vice versa are semantic API changes even if no runtime Python code changes.

## 14. Measurable POC criteria

The following criteria should become implementation acceptance tests.

### Discovery

1. Given a loaded corpus with a compatible TFont profile, one capability call reports corpus/profile/parent/ontology-lock identity and semantic domains.
2. Given a loaded corpus without a TFont profile, discovery reports `profile_not_found` without inventing mappings.
3. Given multiple corpora, concept comparison reports one independent status per corpus.
4. Default capability response is ≤ 8 KiB serialized JSON for one corpus profile summary.

### Resolution

5. An exact `Noun + Feminine + Plural` test fixture resolves to the expected native feature/value constraints and query template.
6. A plausible wrong native feature name is never generated when the profile contains the correct mapping.
7. Unsupported required constraints make the plan non-executable.
8. Approximate mappings are not executable in `exact` mode.
9. `related` mappings are never used as substitution constraints automatically.
10. Ambiguous mappings return alternatives and no executable plan.
11. Resolver output is deterministic for the same corpus/profile/ontology lock and request.

### Execution

12. `semantic_search` executes exactly the plan returned by `semantic_resolve` for the same inputs/revision.
13. Results include compact resolution provenance.
14. Count/statistics/result modes preserve resolution identity.
15. Pagination cannot switch profile/parent revision mid-result.
16. Native Context-Fabric `search()` behavior remains unchanged by installing TFont.

### Safety and failure behavior

17. Parent schema/revision mismatch prevents normal semantic execution.
18. Missing ontology-lock term prevents profile activation or resolution.
19. A Peshitta morphology request fails as unsupported rather than widening to unconstrained words.
20. ORACC `c type=sentence` is not automatically mapped as a BHSA linguistic sentence.
21. TLHdig lexical occurrence queries do not use technical `lex.oslots` as semantic occurrence extent.
22. Peshitta/TLHdig witness-like assertions cannot satisfy a Pseudepigrapha reading-attestation request without an explicit reviewed mapping.
23. Expected semantic tool failures set MCP tool-error state rather than returning a successful error string.

### Explainability/provenance

24. Every executable plan exposes parent corpus revision, TFont mapping version, ontology term/lock, mapping strength and native constraint path.
25. Full explanation can retrieve rationale/source/review metadata for each mapping assertion.
26. A semantic diff identifies mapping-strength and native-constraint changes separately from prose-only edits.

### Human authoring

27. Canonical mapping YAML validates against a schema.
28. Generated RDF/JSON/docs are reproducible from canonical YAML and carry its source digest.
29. Editing a generated artifact without updating source fails the generation/check gate.
30. No reverse-generation path silently modifies canonical YAML from RDF/Turtle.
31. Coverage reports state explicit denominators and count native-only/unsupported mappings.

### Agent efficiency

32. Exact one-corpus query can be planned and executed in at most two semantic tool calls after corpus selection/profile discovery.
33. Typical multi-corpus comparison needs one capability call and one resolution call before execution.
34. Default concept lookup is bounded to 20 candidates per requested concept.
35. Paginated result pages do not repeat full mapping rationale unless requested.
36. No default tool returns an entire ontology or whole mapping bundle.

### MCP interface

37. Semantic tools expose structured output with stable machine fields rather than prose-only contracts.
38. Pure semantic discovery/resolution tools are marked read-only/idempotent where supported by MCP version.
39. Server instructions explain the cross-tool workflow concisely but no safety invariant depends on instruction compliance.
40. Tool/schema validation errors and semantic domain errors are distinguishable.

## 15. Rejected interface alternatives

### Make ontology aliases work invisibly inside native `search()`

Rejected. It obscures whether a query is native or projected, makes provenance harder to inspect and creates unsafe silent behavior when mappings change.

### Require agents to inspect raw corpus features for every semantic query

Rejected as the primary workflow. That repeats schema-discovery work TFont is meant to centralize. Native inspection remains available for explanation/debugging.

### Resolver only, no convenience execution

Rejected for the POC because copying generated templates between tools adds tool calls and gives the agent an opportunity to mutate a reviewed plan. Keep explicit resolver plus convenience semantic execution using exactly the same engine.

### Semantic search only, no explicit resolver

Rejected. Cross-corpus comparison and approximate mappings need a planning stage that can be inspected before execution.

### Turtle as the sole human authoring format

Rejected. Turtle is a good publication format but produces a worse mapping-review surface for native constraints, rationale, applicability and tests than schema-validated YAML.

### YAML and Turtle as co-equal editable sources

Rejected because semantic round-trip, comments and graph serialization make conflict resolution unreliable. One canonical source is required.

### Return full provenance on every page/result

Rejected for token efficiency. Return compact provenance/fingerprint plus explicit detail expansion.

## 16. Unresolved implementation questions

Later design work still needs to determine:

1. exact expression syntax accepted by `semantic_resolve`;
2. whether `semantic_search` is implemented inside Context-Fabric MCP, as a TFont MCP extension/server composed with it, or through an adapter layer;
3. exact JSON schemas and error-code namespace;
4. resolution-ID lifetime/caching behavior under stateless MCP transports;
5. how multi-corpus execution results are grouped/paginated;
6. whether a dedicated `semantic_explain` tool becomes justified after payload benchmarking;
7. exact YAML schema and file granularity;
8. how reviewer provenance is represented without coupling to one forge/account identity;
9. accessibility/UI design of mapping-strength visualizations;
10. final payload/token limits after testing with full BHSA/TLHdig/ORACC profiles.

These implementation questions do not reopen the hybrid workflow, fail-closed semantics, one-way authoring-source strategy or mandatory explainability decisions.

## 17. Acceptance-criteria trace

- **Minimum agent workflow:** capability discovery → explicit resolution → execution, with cached discovery optional.
- **Implicit vs explicit:** hybrid; native `search()` remains native, semantic resolver is explicit, semantic search is a convenience execution of the exact resolver plan.
- **Capability contract:** corpus/profile/domain summary plus bounded concept-level mapping status and cross-corpus comparison.
- **Mapping strength:** exact/close/broader/narrower/related/ambiguous/unsupported/native-only surfaced structurally and in human docs.
- **Provenance:** every plan includes parent, mapping, ontology lock, relation and native path; full rationale available on demand.
- **Human authoring:** schema-validated YAML is canonical; RDF/Turtle/JSON/docs are one-way generated artifacts.
- **Token/tool efficiency:** progressive disclosure, ≤8 KiB default corpus summary target, bounded candidate lists, ≤2 semantic calls for normal one-corpus execution after discovery.
- **Adversarial failures:** wrong feature names, false equivalence, silent widening, stale mappings, absent capabilities, sentence/lexeme/witness traps are specified with safe behavior.
- **Measurable tests:** forty concrete criteria above are intended to seed later implementation/TDD tickets.

## 18. Sources

Primary inspected sources:

- Context-Fabric MCP README, tool reference and server implementation at `Context-Fabric/context-fabric@3a38ca80e617d872ce1664e0f0740486d0e7e8ac`
- `cfabric-mcp` package version `0.1.7` at that revision
- MCP 2026-07-28 specification/release material: `https://modelcontextprotocol.io/` and `https://blog.modelcontextprotocol.io/posts/2026-07-28/`
- MCP tools structured-output/error behavior: `https://modelcontextprotocol.io/specification/`
- MCP server-instructions guidance: `https://blog.modelcontextprotocol.io/posts/2025-11-03-using-server-instructions/`
- R-001 distribution research / PR #8
- R-002 ontology-governance research / PR #9
- R-005 empirical corpus census / PR #7

R-005 remains the empirical dependency. If its accepted independent review changes relevant corpus semantics, this document must be reconciled before R-003 can merge.
