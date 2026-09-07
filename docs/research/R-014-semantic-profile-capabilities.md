# R-014: controlled semantic profile and capability identifiers

**Status:** research complete; revised against merged R-011/R-013 after skeptical review; pending final logically-independent adversarial review  
**Issue:** #48  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-003/R-005 and merged R-006/R-007/R-008/R-009/R-010/R-011/R-012/R-013

## Decision

TFont should replace free-form `profile.semantic_domains` strings with a controlled three-level discovery contract:

1. **profile** — a stable TFont interoperability domain;
2. **capability** — a controlled, profile-scoped query-ability family;
3. **concept/projection** — the exact reviewed semantic target/native binding that alone can authorize semantic query compilation.

The three levels have deliberately different state semantics.

### Profile operational state

`active | absent | unavailable`

- `active`: at least one capability in the profile has reviewed positive native support and the profile contract/dependencies are inspectable;
- `absent`: the mapping release has no reviewed positive native capability in this profile;
- `unavailable`: positive reviewed profile content exists, but required parent/mapping/ontology/bridge components are currently missing, stale, incompatible, or unloadable.

### Capability operational state

`active | absent | unavailable`

- `active`: at least one reviewed **positive native semantic record** belongs to the capability;
- `absent`: no positive native record advertises the capability in this mapping release;
- `unavailable`: positive reviewed capability records exist, but current compatibility/dependency state prevents safe inspection/execution.

An `unsupported` concept record is useful negative knowledge **inside an otherwise active profile/capability**, but it cannot by itself activate either level.

### Concept/projection state

The accepted R-002 assessment remains authoritative:

`exact | close | broader | narrower | related | ambiguous | native-only | unsupported`

Operational availability/executability is reported separately. No profile or capability state replaces these concept-level assessments.

The governing invariant is:

> **Profile activation means that this corpus has at least one reviewed positive native ability in the domain. Capability activation means that at least one reviewed positive native ability exists in that capability family. Neither implies a shared ontology projection, whole-ontology coverage, or execution of an arbitrary requested concept. Only the exact concept/projection binding can authorize semantic query planning.**

## 1. Why free-form semantic domains are unsafe

Free strings cannot reliably answer whether:

- `linguistics`, `morphology`, and `OLiA` denote the same discovery domain;
- a `crmtex` label means line segmentation, glyphs, writing systems, or reading activity;
- `archaeology` means a physical ancient object or actual excavation/stratigraphic assertions;
- `lexical` means lemma lookup, lexical-entry identity, source senses, shared concepts, or dictionary structure;
- `manuscript` denotes a textual witness identity or a physical carrier.

They also encourage whole-ontology claims: two corpora may both be labelled `OntoLex` while supporting very different lexical capabilities.

## 2. Profile IDs are TFont contracts, not ontology namespaces

A profile ID has stable TFont identity independent of ontology release identity.

Conceptually:

```yaml
profile:
  id: lexical
  contract_version: 1
  ontology_bundle: <separate R-015 bundle identity>
```

The profile says **what interoperability domain is exposed**. The ontology bundle says **which exact standard releases/bridges implement the released mappings**.

Therefore:

- `lexical` may compose OntoLex + SKOS + optional LexInfo/VarTrans/Lexicog;
- `textology` may use LRMoo/CRM/CRMtex/CRMinf plus native-only apparatus roles;
- `heritage` may use CRM plus external authority resources;
- `written-text` may use CRMtex while preserving R-012 release/bridge constraints;
- `structural` primarily exposes reviewed native TF/Context-Fabric graph semantics rather than pretending all structure has one ontology relation.

Profile activation is flat. Dependencies are explicit and versioned; they never auto-activate another profile.

Examples:

- `textology` does not imply `written-text`;
- `heritage` does not imply `archaeology`;
- `lexical` does not imply `lexicography`;
- `written-text` does not imply `scholarly-inference`.

## 3. Controlled profile catalog

The first catalog contains seven recurring profiles and three optional evidence-gated profiles.

### 3.1 `structural`

Purpose: reviewed native graph mechanics needed to compose queries across TF-family corpora.

Representative capabilities:

- `structural.entity-kind`
- `structural.slot-coverage`
- `structural.edge-traversal`
- `structural.section-navigation`

R-007 remains authoritative: `oslots` is storage/coverage machinery and does not automatically mean constituency, dependency, containment, or physical parthood.

### 3.2 `linguistic`

Purpose: linguistic annotation categories and relations.

Representative capabilities:

- `linguistic.part-of-speech`
- `linguistic.morphology`
- `linguistic.syntax`
- `linguistic.discourse`

A capability may be active from reviewed native linguistic semantics even when all current common-pivot projections in that capability are `native-only` or absent.

### 3.3 `lexical`

Purpose: lexical identity and lexical-semantic interoperability.

Representative capabilities:

- `lexical.entry`
- `lexical.form`
- `lexical.sense`
- `lexical.concept`
- `lexical.relation`

`lexical.entry` does not imply sense or concept support.

### 3.4 `written-text`

Purpose: physical writing and written-text segmentation where native evidence warrants CRMtex-like semantics.

Representative capabilities:

- `written-text.segment`
- `written-text.sign`
- `written-text.writing-system`
- `written-text.transcription-recognition`

A TF `sign`, `line`, or `surface` node never activates one of these capabilities from storage shape alone.

### 3.5 `textology`

Purpose: textual realizations, witness/transmission relations, fragments, critical apparatus, omission/attestation semantics.

Representative capabilities:

- `textology.textual-version`
- `textology.witness`
- `textology.fragment-transmission`
- `textology.apparatus-reading`
- `textology.witness-attestation`
- `textology.explicit-omission`

A textology capability may be active entirely through native-only records when no accepted common target exists.

### 3.6 `heritage`

Purpose: physical objects, parts, identifiers, materials, places, custody/provenance and related heritage semantics.

Representative capabilities:

- `heritage.physical-object`
- `heritage.physical-part`
- `heritage.identifier`
- `heritage.material`
- `heritage.place-provenance`
- `heritage.custody-location`

Authority-reference semantics remain separate under R-017.

### 3.7 `scholarly-inference`

Purpose: attributed propositions, beliefs, interpretation, argumentation and provenance assessment.

Representative capabilities:

- `scholarly-inference.claim`
- `scholarly-inference.inference`
- `scholarly-inference.meaning-comprehension`
- `scholarly-inference.provenance-assessment`

A source fact, damage flag, catalogue field, or editor code does not activate this profile without an attributed proposition/process assertion shape.

### 3.8 Optional `archaeology`

Capabilities:

- `archaeology.excavation`
- `archaeology.stratigraphy`
- `archaeology.embedding-find-context`

Activation requires actual excavation/stratigraphic/find-context assertions. Ancient-object identity or a `provenience` string is insufficient.

### 3.9 Optional `scientific-analysis`

Capabilities:

- `scientific-analysis.observation`
- `scientific-analysis.measurement`
- `scientific-analysis.sampling`
- `scientific-analysis.position-determination`

Activation requires explicit observation/measurement/sampling/analysis process/result semantics. Material labels, catalogue coordinates, damage state, or converter-derived Unicode values are insufficient.

### 3.10 Optional `lexicography`

Capabilities:

- `lexicography.entry-structure`
- `lexicography.sense-order`
- `lexicography.dictionary-component`

Activation requires reviewed dictionary-specific organization beyond lexical identity. Lemma/gloss strings or a lexical-entry mapping alone are insufficient.

## 4. Capability IDs are discovery buckets, not execution predicates

Capability IDs let an agent ask questions such as:

```text
Which loaded corpora have lexical-sense support?
Which corpora expose physical written-text segments?
Which corpora expose witness-attestation semantics?
```

They do not replace ontology targets or R-013 semantic roles.

The concept execution key remains concept-specific:

```text
(profile-id
 + capability-id
 + target
 + formal-kind
 + semantic-role)
 -> reviewed corpus-native binding
```

A single active capability can contain mixed concept assessments:

```text
linguistic.morphology
  olia:Plural                  exact
  olia:Masculine               exact
  native verbal-stem category  native-only
  requested absent category    unsupported
```

The last `unsupported` record is negative evidence; it does not activate the capability.

## 5. Activation rules

### 5.1 Positive support set

For activation, a **positive native semantic record** is one whose native semantics actually exist and have been reviewed. This includes records assessed:

- `exact`
- `close`
- `broader`
- `narrower`
- `related`
- `ambiguous` when the native semantic assertion exists but the common projection is unresolved
- `native-only`

It excludes `unsupported`, which means the requested semantic capability/concept is not provided by the reviewed corpus contract.

### 5.2 Capability activation

A capability is `active` only when:

1. the capability ID is recognized by the profile contract;
2. at least one positive native semantic record belongs to it;
3. required parent/profile components are compatible enough for inspection;
4. required mapping/ontology artifacts for the advertised summary can be loaded or, for purely native-only capability content, the native record remains inspectable without fabricating a common target.

A capability with only `unsupported` records is `absent`, while requested unsupported concepts may still be reported as explicit negative concept knowledge.

If positive records exist but required components are currently incompatible or unloadable, capability state is `unavailable`.

### 5.3 Profile activation

A profile is `active` only when at least one capability is `active`.

A profile with no active capability is `absent` unless positive reviewed capability records exist but are operationally blocked, in which case it is `unavailable`.

This prevents a single negative control such as “BHSA archaeology unsupported” from falsely activating the archaeology profile.

## 6. Capability summaries

Capability state is reported explicitly and separately from aggregate concept counts:

```yaml
capability: lexical.sense
state: active
records: 12
shared_projections: 8
exact: 5
approximate: 3
ambiguous: 0
native_only: 4
unsupported: 2
executable_exact: true
```

Definitions:

- `state` is `active|absent|unavailable` under §5;
- `shared_projections` counts approved target-bearing records only;
- `approximate` is a discovery aggregate over `close|broader|narrower|related`; detailed assessment remains per concept;
- `native_only` is legitimate native support but never shared-target coverage;
- `unsupported` counts explicit negative concept records and never contributes to activation;
- `executable_exact` means at least one exact binding is currently executable, not that the capability as a whole is exact.

No profile- or capability-level `exact`, `close`, `unsupported`, or `partial` state is introduced.

## 7. Concept-level support remains authoritative

For a requested common target, return separately:

- profile state;
- capability state and ID;
- target identity, R-013 formal kind and semantic role;
- R-002 mapping assessment;
- operational availability/compatibility;
- executable/non-executable state under the requested semantic mode;
- compact native binding summary;
- profile contract/catalog version and relevant parent/ontology provenance fingerprints.

If the profile or capability is active only through `native-only` records, a common-target request still fails closed unless the requested target has its own reviewed projection.

## 8. Compact `semantic_capabilities` contract

R-003 requires progressive disclosure. Default discovery output should show summaries, not mapping rows.

Conceptual response:

```json
{
  "catalog_version": 1,
  "corpora": {
    "oracc": {
      "profiles": {
        "lexical": {
          "state": "active",
          "capabilities": {
            "lexical.entry": {
              "state": "active",
              "shared_projections": 1,
              "native_only": 0
            },
            "lexical.sense": {
              "state": "active",
              "shared_projections": 0,
              "native_only": 1
            }
          }
        },
        "heritage": {
          "state": "active",
          "capabilities": {
            "heritage.physical-object": {
              "state": "active",
              "shared_projections": 0,
              "native_only": 1
            }
          }
        }
      }
    }
  }
}
```

The ORACC example is intentional: the heritage profile can be active from reviewed native object/material/authority semantics while generic `otype=document -> crm:E22` remains fail-closed under accepted R-011.

Optional filters:

```text
corpora
profiles
capabilities
concepts
compare
verbosity=compact|full
```

When `concepts=[...]` is supplied, return only requested concept rows. `compare=true` produces a compact profile/capability/concept matrix. Full mapping rationale remains an explicit drill-down/explain operation.

## 9. Comparison semantics

### 9.1 Profile comparison

Report exactly:

```text
active | absent | unavailable
```

Do not infer profile coverage from ontology namespace size or sibling profiles.

### 9.2 Capability comparison

Report capability state plus aggregate counts.

Example:

```text
lexical.sense
  ORACC   capability active; native source-sense support; no shared LexicalSense projection in R-011
  BHSA    lexical profile active; capability absent in current reviewed pilot
  Syriac  lexical profile active; capability absent in current reviewed pilot
  CUC     lexical profile absent
```

A requested concept may still return explicit `unsupported` even when its capability is absent; that is concept-level negative knowledge, not a capability state.

### 9.3 Concept comparison

Only concept-level comparison can justify cross-corpus semantic query planning. Return each corpus's exact assessment and execution state.

## 10. Accepted seven-pilot evidence

The catalog is tested against merged R-005 and R-011 evidence. The table below is deliberately conservative. `active/shared` means at least one accepted R-011 common projection is present; `active/native` means reviewed native semantics justify the profile but the cited capability is not established as a shared pivot in R-011. `absent` means no positive reviewed profile ability is claimed by this R-014 pilot classification. These annotations explain evidence; production profile state remains simply `active|absent|unavailable`.

| corpus | structural | linguistic | lexical | written-text | textology | heritage | scholarly-inference |
|---|---|---|---|---|---|---|---|
| BHSA | active/native | active/shared | active/shared | absent | absent | absent | absent |
| ETCBC Syriac | active/native | active/shared | active/shared | absent | absent | absent | absent |
| ETCBC ExtraBiblical | active/native | active/shared | active/shared | absent | absent | absent | absent |
| CUC 0.2.8 | active/native | absent | absent | active/shared | absent | active/shared | absent |
| Pseudepigrapha-TF | active/native | absent for current R-011 profile | absent for current R-011 profile | absent | active/shared+native | absent without carrier evidence | absent |
| ORACC-TF | active/native | active/native from reviewed R-005 POS/morphology, no R-011 OLiA projection | active/shared+native | active/shared | absent for current R-011 transmission profile | active/native; generic E22 projection fails closed | absent |
| TLHdig-TF | active/native | active/native from reviewed R-005 analysis/POS/morphology, no R-011 OLiA projection | active/shared+native | active/shared | active/native for witness/fragment/editorial subset | active/shared | absent |

Evidence boundaries carried forward from R-011:

- OLiA shared query reuse is demonstrated for BHSA, Syriac and ExtraBiblical, not ORACC/TLH;
- OntoLex lexical-entry reuse is demonstrated for BHSA, Syriac, ExtraBiblical, ORACC and TLH;
- CRMtex TX7 line reuse is demonstrated for CUC, ORACC and TLH;
- CRM E22 physical-object projection is demonstrated for CUC and TLH only;
- ORACC generic `otype=document` is `native-only` for physical-object capability until a reviewed object-bearing selector exists;
- Pseudepigrapha manuscript identity does not activate physical heritage without carrier evidence;
- Pseudepigrapha textology includes native apparatus/witness semantics and a conservative LRMoo F2 textual-version candidate;
- TLH surface remains native physical support, not TX7;
- no current pilot activates scholarly-inference merely from source/editorial facts.

This classification does not require every active profile to have a common target. Native-only capability is first-class discovery information.

## 11. Optional-profile activation

### Archaeology

Do not activate from object age, tablet/manuscript type, `provenience` string, or generic catalogue metadata. Current seven-pilot R-011 evidence does not activate archaeology.

### Scientific analysis

Do not activate from material labels, coordinates, damage states, or converter computations. Current seven-pilot R-011 evidence does not activate scientific-analysis.

### Lexicography

Do not activate merely from lemma/gloss/entry/sense existence. ORACC's glossary structure is evidence that deserves a later explicit lexicography-profile review, but R-011 did not establish this optional profile contract, so R-014 does not activate it retrospectively.

## 12. Fail-closed rules

1. Unknown profile ID -> contract error; no free-string fallback.
2. Unknown capability ID -> contract error or explicit unsupported-extension diagnostic; no fuzzy matching.
3. Profile `absent` -> required profile query non-executable; no native-label search fallback.
4. Profile `unavailable` -> non-executable even if stale cached bindings exist.
5. Capability `absent` -> required capability query non-executable; no sibling capability fallback.
6. Capability `unavailable` -> non-executable even if its concept was previously executable.
7. Profile/capability activation never follows from `unsupported` records alone.
8. Active profile never implies every capability active.
9. Active capability never implies every concept executable.
10. Missing target binding never falls back to ontology hierarchy or label similarity.
11. `native-only` never contributes to shared semantic target coverage.
12. `ambiguous` never becomes executable shared support without the appropriate reviewed resolution/mode.
13. Optional profiles never auto-activate from domain labels or corpus age/type.
14. Profile dependency/hierarchy never auto-activates another profile.
15. Same profile/capability in two corpora never authorizes a cross-corpus plan without matching requested concept bindings.

## 13. Versioning

The controlled vocabulary has three separate identity/version layers:

1. `catalog_version` — profile/capability identifier catalog;
2. per-profile `contract_version` — meaning/requirements of that profile and its capability IDs;
3. R-015 ontology bundle identity — exact ontology releases/bridges used by mappings.

Corpus mapping release and parent component identity remain separate again.

Do not encode ontology versions into profile IDs such as `written-text-crmtex-2.0`.

Adding/removing/changing a profile/capability identifier requires catalog or profile-contract versioning. Released mappings retain their original vocabulary interpretation.

## 14. RED-style contract cases for P-003/TDD

The following must fail in the future production contract:

1. free-form `semantic_domains=["whatever"]` accepted;
2. profile inferred from ontology namespace;
3. `heritage` auto-activates `archaeology`;
4. `lexical` auto-activates `lexicography`;
5. `textology` auto-activates `written-text`;
6. `written-text` auto-activates scholarly-inference from editorial flags;
7. active profile with zero active capabilities;
8. active capability with zero positive native semantic records;
9. a profile/capability activated only by `unsupported` records;
10. active profile treated as whole-ontology support;
11. active capability treated as every target executable;
12. `native-only` included in shared projection count;
13. `unsupported` concept silently omitted from requested comparison;
14. `unsupported` concept used as capability state;
15. profile `absent` falls back to similarly named native feature;
16. capability `absent` falls back to a sibling capability;
17. profile/capability `unavailable` executes cached old binding;
18. unknown capability fuzzy-matched to nearest known capability;
19. archaeology activated from `provenience` literal alone;
20. scientific-analysis activated from material/coordinate literals alone;
21. lexicography activated from lemma+gloss alone;
22. Pseudepigrapha `manuscript` automatically activates physical heritage;
23. ORACC generic `otype=document` advertised as shared E22 physical-object support;
24. TLH `surface` advertised as CRMtex TX7;
25. TLH edit/damage nodes activate CRMinf scholarly-inference without attributed proposition/process evidence;
26. profile-level `exact|close|unsupported|partial` mapping state introduced;
27. capability-level `exact|close|unsupported|partial` mapping state introduced;
28. cross-corpus plan executes merely because both corpora advertise the same profile/capability;
29. compact capability discovery dumps all mapping rows by default;
30. ontology release silently changes profile identity.

## 15. P-003 profile/IR inputs

Conceptual declaration:

```yaml
profile_catalog_version: 1
profiles:
  - id: lexical
    contract_version: 1
    state: active
    ontology_bundle: <bundle-id>
    capabilities:
      - id: lexical.entry
        state: active
        records: [<mapping/native-role IDs>]
      - id: lexical.sense
        state: absent
        records: []
```

Indexes:

```text
(corpus, profile-id)
  -> profile operational state + active capability IDs

(corpus, profile-id, capability-id)
  -> capability operational state + summary counts + record IDs

(corpus, profile-id, capability-id, target, formal-kind, semantic-role)
  -> reviewed concept binding(s)
```

The third index is authoritative for execution. The first two exist for compact discovery/comparison.

For `native-only` records, capability summaries include native support but target-keyed reverse indexes never fabricate a semantic key.

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

Compact output returns:

- profile state;
- capability state;
- catalog/profile contract versions;
- shared/exact/approximate/ambiguous/native-only/unsupported counts;
- parent/ontology operational compatibility summary;
- requested concept rows only when requested.

Full mode may expose mapping IDs, native selectors, ontology locks and review evidence.

No default call should enumerate all ontology terms or mapping rows.

## 17. Rejected alternatives

### Ontology-name profiles

Rejected because ontology boundaries do not match agent tasks and several profiles compose multiple models.

### Deep inherited taxonomy

Rejected because semantic-domain inclusion does not imply corpus capability inclusion. Explicit dependencies are safer.

### Capability == ontology target URI

Rejected because an agent often needs to discover “lexical sense support” before knowing a particular target URI. Target remains the execution key, not the sole discovery vocabulary.

### Capability == native feature name

Rejected because it destroys cross-corpus discovery portability.

### One profile/capability state summarizing mapping quality

Rejected because exact/approximate/native-only/unsupported vary per concept. Operational state and mapping assessment are orthogonal.

## 18. Acceptance-criteria closure

- **Controlled vocabulary:** seven recurring profile IDs plus three optional evidence-gated profiles; capability IDs are controlled and profile-scoped.
- **Three levels separated:** profile operational state, capability operational state, concept mapping assessment.
- **All seven R-011 pilots covered:** current evidence matrix consumes merged R-005/R-011 instead of deferring activation back to unfinished research.
- **No forced empty profiles:** negative controls do not activate a profile; optional archaeology/science/lexicography remain absent until positive reviewed evidence establishes their contracts.
- **Agent comparison/fail-closed behavior:** compact summaries preserve `active|absent|unavailable`, capability state, native-only support, requested concept assessment and no fuzzy fallback.
- **P-003 inputs:** catalog/profile versioning, activation rules, discovery indexes, concept execution index and RED cases are explicit.

## 19. Remaining boundaries

R-014 intentionally leaves these decisions elsewhere:

- final public URI/namespace spelling of profile/capability IDs — P-003/public vocabulary packaging;
- target formal-kind/semantic-role spellings — accepted R-013/P-003;
- ontology bundle/bridge identity — R-015;
- approximate execution authorization — R-016;
- external-authority query semantics — R-017;
- production schema/runtime/API implementation — P-003 and later implementation tickets.

Future profile/capability additions require demonstrated recurring agent-query semantics, not labels copied from an ontology or corpus schema.