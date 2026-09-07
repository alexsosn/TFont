# R-014: controlled semantic profile and capability identifiers

**Status:** research complete; pending fresh logically-independent adversarial review  
**Issue:** #48  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-003/R-005, merged R-006/R-007/R-008/R-009/R-010/R-012; consumes R-013's formal-kind/semantic-role separation but does not require its production enum spellings

## Decision

TFont should replace free-form `semantic_domains` with a **two-level controlled discovery contract**:

1. a small set of stable **TFont semantic profile IDs** that describe interoperability domains;
2. profile-scoped **capability IDs** that summarize query abilities for agent discovery without implying support for every ontology term.

Execution is still authorized only by reviewed **concept/target bindings**. Profile or capability activation is never sufficient by itself to compile a query.

The first profile families are:

- `structural`
- `linguistic`
- `lexical`
- `written-text`
- `textology`
- `heritage`
- `scholarly-inference`

Optional profiles, activated only when native evidence warrants them, are:

- `archaeology`
- `scientific-analysis`
- `lexicography`

These are TFont interoperability contracts, **not aliases for ontology namespaces**. A profile may compose several ontology models and a single ontology may participate in several profiles.

The governing invariant is:

> **Profile activation means “this corpus has a reviewed mapping contract in this semantic domain,” not “this corpus supports every term in the profile's ontologies.” Capability activation means “at least one reviewed query ability in this capability family exists,” not “all concepts in that family are executable.” Per-concept support remains authoritative.**

## 1. Why free-form `semantic_domains` is unsafe

Free strings cannot reliably answer any of these agent questions:

- Does `linguistics`, `linguistic`, `morphology`, and `OLiA` denote the same profile?
- Does a corpus marked `crmtex` support glyphs, writing systems, written segments, or only lines?
- Does `archaeology` mean physical ancient objects, or actual excavation/stratigraphic semantics?
- Does `lexical` mean lemma strings, lexical-entry identity, source senses, shared concepts, or a full dictionary?
- Does `manuscript` imply physical codicology, textual witness identity, or critical apparatus?

Free strings also make comparison brittle: two profiles can describe the same domain with different labels, while one overly broad label can falsely suggest complete ontology coverage.

## 2. Profile IDs are TFont contracts, not ontology IDs

### 2.1 Independent profile identity

A profile ID should have stable TFont identity independent of ontology release identity.

Conceptually:

```yaml
profile:
  id: linguistic
  contract_version: 1
  ontology_bundle: <separate locked bundle identity>
```

The profile ID answers **what interoperability contract is being exposed**. The ontology bundle answers **which exact standards/releases/bridges implement that contract in this mapping release**.

This separation is required because:

- `lexical` can compose OntoLex core + SKOS + optional LexInfo/VarTrans/Lexicog;
- `textology` can compose LRMoo + CIDOC CRM + CRMtex + CRMinf plus profile-local apparatus roles;
- `heritage` uses CIDOC CRM plus optional authority resources;
- `written-text` uses CRMtex but must respect CRM/R-012 composition;
- `structural` intentionally keeps native TF mechanics primary and only uses a tiny aligned structural vocabulary where justified.

### 2.2 No profile inheritance semantics

Profile IDs should be **flat** in activation semantics. Composition/dependency can be explicit, but activation does not inherit.

Examples:

- `textology` does **not** imply `written-text`: a digital critical apparatus can model textual witnesses/readings without physical-writing semantics;
- `heritage` does **not** imply `archaeology`: a tablet or manuscript is a heritage object without excavation/stratigraphy data;
- `lexical` does **not** imply `lexicography`: lemma/lexeme identity does not make the corpus a dictionary;
- `written-text` does **not** imply `scholarly-inference`: damage/editorial states are not automatically argumentation graphs.

If a profile requires another profile for a particular released contract, that dependency is an explicit versioned dependency, not a taxonomy rule.

## 3. First controlled profile catalog

### 3.1 `structural`

Purpose: recurring TF/Context-Fabric graph mechanics needed to compose semantic queries.

Primary basis: R-007.

Representative capabilities:

- `structural.entity-kind`
- `structural.slot-coverage`
- `structural.edge-traversal`
- `structural.section-navigation`

Activation does not assert that `oslots` means constituency or containment.

### 3.2 `linguistic`

Purpose: linguistic annotation categories and relations.

Primary basis: OLiA + accepted linguistic mappings.

Representative capabilities:

- `linguistic.part-of-speech`
- `linguistic.morphology`
- `linguistic.syntax`
- `linguistic.discourse` (only when present)

A corpus may activate `linguistic.morphology` while particular categories remain `native-only` or unsupported.

### 3.3 `lexical`

Purpose: lexical identity and lexical-semantic interoperability.

Primary basis: R-008, OntoLex/SKOS.

Representative capabilities:

- `lexical.entry`
- `lexical.form`
- `lexical.sense`
- `lexical.concept`
- `lexical.relation`

Activation of `lexical.entry` does not imply `lexical.sense` or `lexical.concept`.

### 3.4 `written-text`

Purpose: physical writing and written-text segmentation where source semantics warrant CRMtex-style interpretation.

Representative capabilities:

- `written-text.segment`
- `written-text.sign`
- `written-text.writing-system`
- `written-text.transcription-recognition` (only when explicit activities exist)

A TF `sign` or `line` node does not activate these capabilities from storage shape alone.

### 3.5 `textology`

Purpose: intellectual textual realizations, witness/transmission relations, fragments and critical-apparatus semantics.

Representative capabilities:

- `textology.textual-version`
- `textology.witness`
- `textology.fragment-transmission`
- `textology.apparatus-reading`
- `textology.witness-attestation`
- `textology.explicit-omission`

R-009 permits profile-local/native-only apparatus roles while no accepted common target exists. Therefore the profile may be active even when some capabilities have no common-pivot target.

### 3.6 `heritage`

Purpose: physical objects, parts, identifiers, materials, places, custody/provenance and related heritage semantics.

Representative capabilities:

- `heritage.physical-object`
- `heritage.physical-part`
- `heritage.identifier`
- `heritage.material`
- `heritage.place-provenance`
- `heritage.custody-location`

External authority references remain distinct from common semantic targets under R-017.

### 3.7 `scholarly-inference`

Purpose: attributed propositions, beliefs, interpretation, argumentation and provenance assessment.

Representative capabilities:

- `scholarly-inference.claim`
- `scholarly-inference.inference`
- `scholarly-inference.meaning-comprehension`
- `scholarly-inference.provenance-assessment`

A flat source fact or editor code does not activate this profile.

### 3.8 Optional `archaeology`

Purpose: excavation/stratigraphic/find-context semantics.

Representative capabilities:

- `archaeology.excavation`
- `archaeology.stratigraphy`
- `archaeology.embedding-find-context`

Activation gate: actual CRMarchaeo-like excavation/stratigraphic assertion shape. Ancient object + provenience string is insufficient.

### 3.9 Optional `scientific-analysis`

Purpose: observation, measurement, sampling and scientific-analysis processes/results.

Representative capabilities:

- `scientific-analysis.observation`
- `scientific-analysis.measurement`
- `scientific-analysis.sampling`
- `scientific-analysis.position-determination`

Activation gate: source records actual observation/measurement process/result semantics. Material labels and catalogue coordinates alone are insufficient.

### 3.10 Optional `lexicography`

Purpose: dictionary-specific organization beyond lexical identity.

Representative capabilities:

- `lexicography.entry-structure`
- `lexicography.sense-order`
- `lexicography.dictionary-component`

Activation gate: genuine dictionary structure such as ordered senses/entry components. Repeated lemma/gloss strings are insufficient.

## 4. Capability IDs are discovery buckets, not execution predicates

Capability IDs exist to let an agent ask compact questions such as:

```text
Which loaded corpora have lexical sense support?
Which corpora can navigate physical written-text segments?
Which corpora expose witness-attestation semantics?
```

They do **not** replace semantic target identities.

Execution key remains concept/target-specific:

```text
(profile ID
 + capability ID
 + semantic target IRI
 + formal kind
 + semantic role)
   -> reviewed corpus-native binding
```

A capability can therefore contain mixed concept-level states:

```text
linguistic.morphology
  Number/Plural       exact
  Gender/Feminine     exact
  language-specific stem category  native-only
  another requested category       unsupported
```

## 5. Profile-level states

The profile lifecycle needs only three operational states:

- `active` — a reviewed profile contract is loaded and parent/ontology compatibility permits inspection; concept execution still depends on concept-level status;
- `absent` — the mapping release does not declare this profile for the corpus;
- `unavailable` — the profile is declared but cannot currently be used because required mapping/ontology/bridge/parent components are missing, stale, incompatible or unloadable.

Do not create `partial`, `exact`, `close`, or `unsupported` as profile-level mapping states. Those meanings belong to concepts/capabilities.

`unavailable` is operational and must not be confused with R-002 `unsupported`.

### 5.1 Activation minimum

A profile may be declared `active` only if:

1. the profile contract/version is recognized;
2. its declared ontology bundle/dependencies are reviewable;
3. parent compatibility allows the profile to load for inspection;
4. the release contains at least one reviewed mapping/native-role record belonging to the profile.

A profile with zero records is omitted/`absent`, not advertised as an empty active profile.

## 6. Capability-level summary states

A capability summary should not invent another mapping-assessment taxonomy. It aggregates existing records into counts/booleans:

```yaml
capability: lexical.sense
records: 12
shared_projections: 8
exact: 5
approximate: 3
ambiguous: 0
native_only: 4
unsupported: 0
executable_exact: true
```

Where:

- `shared_projections` counts records with approved common semantic targets;
- `approximate` aggregates `close|broader|narrower|related` for discovery only; detailed assessment remains available per concept;
- `native_only` remains a legitimate no-target state and is never added to shared coverage;
- `unsupported` records represent known negative support within an active profile;
- `executable_exact` means at least one exact concept binding in the capability is operationally executable, not that every concept is exact.

For a requested concept, return the exact R-002 assessment rather than only aggregate counts.

## 7. Concept-level support is authoritative

For a requested common semantic target, the agent-facing result must report separately:

- profile state;
- capability ID;
- target identity + formal kind + semantic role;
- mapping assessment (`exact`, `close`, `broader`, `narrower`, `related`, `ambiguous`, `native-only`, `unsupported` as applicable to the underlying record);
- operational availability/compatibility;
- executable/non-executable under requested semantic mode;
- compact native binding summary;
- profile contract version and ontology/parent provenance fingerprints.

For a common-target request, a corpus with only relevant `native-only` records still returns **non-resolvable for that target**. Native-only records are discoverable in native capability inspection but do not masquerade as common semantic support.

## 8. Compact agent discovery contract

R-003 requires progressive disclosure. The default `semantic_capabilities` response should therefore show summary information, not mapping rows.

Conceptual response:

```json
{
  "catalog_version": 1,
  "corpora": {
    "bhsa": {
      "compatibility": "verified-exact",
      "profiles": {
        "structural": {"state": "active"},
        "linguistic": {
          "state": "active",
          "capabilities": {
            "linguistic.part-of-speech": {"shared": 8, "native_only": 0},
            "linguistic.morphology": {"shared": 19, "native_only": 6}
          }
        },
        "lexical": {"state": "active"}
      }
    },
    "cuc": {
      "profiles": {
        "structural": {"state": "active"},
        "written-text": {"state": "active"},
        "heritage": {"state": "active"}
      }
    }
  }
}
```

When `concepts=[...]` is supplied, add only those concept support rows. When `compare=true`, provide a matrix keyed by requested profile/capability/concept rather than repeating full mapping provenance.

Full mapping rationale remains an explicit drill-down/explain operation.

## 9. Comparison semantics

### 9.1 Profile comparison

For each profile:

```text
corpus A: active
corpus B: active
corpus C: absent
corpus D: unavailable
```

`absent` and `unavailable` are intentionally different:

- absent = profile not claimed by this mapping release;
- unavailable = profile is claimed but cannot safely be used now.

### 9.2 Capability comparison

Compare capability presence plus counts, not ontology size.

Good output:

```text
lexical.sense
  ORACC          active, 2 exact shared sense bindings in requested fixture
  BHSA           active lexical profile, capability absent/unsupported
  Syriac         active lexical profile, capability unsupported
  CUC            lexical profile absent
```

Bad output:

```text
ORACC supports OntoLex
BHSA supports OntoLex
```

because that implies whole-ontology support.

### 9.3 Concept comparison

For requested semantic concepts, show per-corpus assessment and execution state directly. This is the only level that can justify cross-corpus query planning.

## 10. Fail-closed rules

1. Unknown profile ID -> schema/contract error; do not treat as user-defined domain string.
2. Unknown capability ID -> schema/contract error or explicit unsupported-extension diagnostic; no fuzzy matching.
3. Profile `absent` -> common query requiring it is non-executable; do not search native features for similar labels.
4. Profile `unavailable` -> non-executable even if concept mappings are known from an older cached profile.
5. Active profile + missing capability -> non-executable for that capability; no sibling capability fallback.
6. Active capability + missing target binding -> concept `unsupported`/non-resolvable; no label/ontology inference.
7. `native-only` -> never counted as shared semantic target coverage.
8. `ambiguous` -> never counted as executable shared support until resolved/explicit mode permits a reviewed alternative.
9. Optional profile is never activated by age/domain heuristics (`ancient`, `tablet`, `manuscript`, `excavated`, etc.).
10. Profile hierarchy/dependency never auto-activates another profile.

## 11. Seven-pilot stress matrix

This matrix records **profile candidates supported by merged research**, not production mapping releases. R-011 owns empirical final fixture activation/counts.

| corpus | structural | linguistic | lexical | written-text | textology | heritage | scholarly-inference | optional notes |
|---|---|---|---|---|---|---|---|---|
| BHSA | active | active | active | absent | absent | absent | absent | verbal-stem concepts may remain native-only |
| ETCBC Syriac | active | active | active | absent | absent | absent | absent | lexical sense/concept depth can be unsupported despite lexical entry support |
| ETCBC extrabiblical | active | active | active | absent | absent | absent | absent | high-similarity control; do not infer exact mappings from shared ETCBC names |
| CUC 0.2.8 | active | limited/absent until reviewed linguistic targets | absent for released lexical layer | active candidate | absent | active candidate | absent | archaeology/scientific-analysis absent on current evidence |
| Pseudepigrapha-TF | active | not required | not required | absent by default | active | absent unless manuscript physical-carrier evidence exists | absent unless attributed claims are modeled | apparatus capabilities can be native-only while profile remains active |
| ORACC-TF | active | active candidate where POS/morphology is mapped | active | active | limited transmission only if reviewed | active | absent by default | lexicography candidate for explicit glossary structure; archaeology/science not activated by catalogue data alone |
| TLHdig-TF | active | active | active | active | active candidate for witness/fragment transmission subset | active | absent by default | edit/damage facts do not activate CRMinf; archaeology/science absent on current evidence |

`active candidate` / `limited` in this research matrix means R-014 recognizes the profile family as appropriate for reviewed mappings evidenced by prior research, but R-011 must still decide the exact fixture activation and counts. Production API states remain only `active|absent|unavailable`.

## 12. Optional-profile activation tests

### 12.1 Archaeology

Do **not** activate because:

- object is ancient;
- source has `provenience` or `findspot` string;
- corpus is ORACC/TLH/CUC;
- physical object is a tablet/fragment.

Activate only when reviewed native semantics expose excavation/stratigraphic/find-context assertion shapes required by the profile.

### 12.2 Scientific analysis

Do **not** activate because:

- material is known;
- coordinates exist;
- damage state exists;
- converter computes sign or Unicode properties.

Activate only for explicit observation/measurement/sampling/analysis semantics.

### 12.3 Lexicography

Do **not** activate because:

- lemma/gloss strings exist;
- lexical entries exist;
- a corpus has an OntoLex mapping.

Activate when dictionary-specific organization (entry components, ordered senses, lexicographic structure) is represented and reviewed.

## 13. Profile/catalog versioning

### 13.1 Catalog version

The controlled set of profile/capability IDs has a `catalog_version`. Adding/removing/changing the meaning of an identifier requires a catalog version change.

### 13.2 Profile contract version

Each profile has an independent `contract_version` because its required roles/capability definitions may evolve without changing unrelated profiles.

### 13.3 Ontology bundle is separate

Do not encode ontology versions into profile IDs such as:

```text
written-text-crmtex-2.0
lexical-ontolex-2016
```

The same TFont profile can be implemented by a version-locked bundle whose identity is governed separately by R-015. A profile contract change and ontology release change are different events.

### 13.4 Mapping release remains separate

Corpus-specific mapping/profile release version remains independent again. Therefore reproducible capability identity is conceptually:

```text
profile catalog version
+ profile ID / contract version
+ ontology bundle identity
+ corpus mapping release
+ parent component manifest
```

## 14. RED-style contract cases for P-003/TDD

1. Free-form `semantic_domains=["whatever"]` accepted -> reject under new schema version.
2. Profile ID inferred from ontology namespace (`crmtex` -> written-text) -> reject.
3. `heritage` auto-activates `archaeology` -> reject.
4. `lexical` auto-activates `lexicography` -> reject.
5. `textology` auto-activates `written-text` -> reject.
6. `written-text` auto-activates `scholarly-inference` from editorial flags -> reject.
7. Active profile with zero mapping/native-role records -> reject/omit profile.
8. Active profile treated as whole-ontology support -> reject capability response/test expectation.
9. Active capability treated as every target executable -> reject.
10. `native-only` included in shared projection count -> reject.
11. `unsupported` concept silently omitted from comparison -> reject.
12. Profile `absent` falls back to similarly named native feature -> reject.
13. Profile `unavailable` executes cached old binding -> reject.
14. Unknown capability fuzzy-matched to nearest known capability -> reject.
15. Optional archaeology activates from `provenience` literal alone -> reject.
16. Optional scientific-analysis activates from material/coordinate literals alone -> reject.
17. Optional lexicography activates from lemma+gloss alone -> reject.
18. Pseudepigrapha `manuscript` node automatically activates physical heritage profile -> reject without carrier evidence.
19. TLH edit/damage nodes automatically activate CRMinf scholarly-inference -> reject without attributed proposition/process evidence.
20. Profile ID includes live ontology version and silently changes identity after ontology update -> reject.
21. Capability comparison dumps all mapping rows by default -> fail ergonomics/token-budget gate.
22. `absent` and `unavailable` collapsed into one state -> reject because operational diagnosis/execution differs.
23. Profile-level `exact/close` state introduced -> reject; mapping assessment belongs to concept/projection records.
24. Cross-corpus plan executes because both corpora advertise the same profile while the requested concept differs/unsupported -> reject.

## 15. P-003 profile/IR inputs

Conceptual profile declaration:

```yaml
profile_catalog_version: 1
profiles:
  - id: lexical
    contract_version: 1
    state: active
    ontology_bundle: <bundle-id>
    capabilities:
      - id: lexical.entry
        records: [<mapping/native-role IDs>]
      - id: lexical.sense
        records: [<mapping/native-role IDs>]
```

Conceptual capability index:

```text
(corpus, profile-id, capability-id)
  -> summary counts + record IDs + operational state

(corpus, profile-id, target, formal-kind, semantic-role)
  -> reviewed concept binding(s)
```

The second/concept index is authoritative for execution. The first is an agent-discovery acceleration index.

For `native-only` profile records, the first index includes them in `native_only` counts; the target-keyed reverse index does not fabricate a semantic key.

## 16. Agent-facing API inputs

`semantic_capabilities` should accept optional filters:

```text
corpora
profiles
capabilities
concepts
compare
verbosity=compact|full
```

Compact default returns:

- profile state;
- contract/catalog versions;
- capability counts;
- exact/approximate/native-only/unsupported summary counts;
- parent compatibility state;
- requested concept rows only when requested.

Full mode may expose mapping IDs, native selectors, ontology locks and review evidence.

No default call should enumerate all ontology terms or all mapping rows.

## 17. Rejected alternatives

### Ontology-name profiles

Rejected because ontology boundaries do not match agent tasks and many profiles compose several ontologies.

### Deep inherited taxonomy

Rejected because semantic-domain inclusion does not imply data/capability inclusion. Explicit dependencies are safer and auditable.

### Capability == ontology target URI

Rejected for discovery ergonomics. Agents often need to ask “which corpora have lexical senses?” before knowing a particular target URI. Target URI remains the execution key, not the sole discovery vocabulary.

### Capability == native feature name

Rejected because it recreates corpus-specific discovery and prevents cross-corpus comparison.

### One profile state summarizing mapping quality

Rejected because mapping strengths vary per concept; a profile can contain exact, approximate, native-only and unsupported records simultaneously.

## 18. Acceptance-criteria closure

- **Controlled vocabulary:** seven core profile IDs plus three optional evidence-gated profiles; capability IDs are profile-scoped and controlled.
- **Activation vs concept assessment separated:** profile state is operational; R-002 assessment remains concept/projection-level.
- **All seven R-011 pilots covered:** matrix includes BHSA, CUC, Syriac, ExtraBiblical, Pseudepigrapha-TF, ORACC-TF and TLHdig-TF without forcing archaeology/science/physical-codicology claims.
- **Agent comparison/fail-closed behavior:** compact summary, requested-concept matrix, `active|absent|unavailable`, no fuzzy/native fallback.
- **P-003 inputs:** catalog/profile versioning, activation record, capability summary index, concept execution index and RED cases are explicit.

## 19. Remaining boundaries

R-014 intentionally leaves these decisions elsewhere:

- final URI/namespace spelling of profile/capability IDs — P-003/public vocabulary packaging;
- target formal-kind/semantic-role enum spellings — R-013/P-003;
- ontology bundle/bridge identity — R-015;
- approximate execution policy — R-016;
- external-authority query role — R-017;
- final empirical activation/counts for seven pilots — R-011.

Future research may add profile/capability IDs, but additions require demonstrated recurring agent-query semantics rather than labels copied from an ontology or corpus schema.
