# R-012: CRMtex 2.0 bridge to current LRMoo and CRMinf

**Status:** research complete; pending fresh logically-independent review  
**Issue:** #46  
**Recorded:** 2026-09-07  
**Depends on:** accepted R-002/R-003/R-005, merged R-006 #52, merged R-007 #53, and merged roadmap guardrail #45

## Decision

TFont should use **version-faithful CRMtex 2.0 plus selective, evidence-backed bridges**, not a rewritten “current-stack CRMtex” and not a blanket old-namespace/new-namespace equivalence layer.

The stable CRMtex 2.0 model remains locked with the dependency set it declares:

- CIDOC CRM 7.1.2;
- CRMinf 0.7(b);
- CRMsci 2.0;
- FRBRoo 2.4.

The current TFont semantic pivot separately locks the currently accepted releases:

- CIDOC CRM 7.1.3;
- LRMoo 1.1.1;
- CRMinf 1.2.1.

A mapping/query may compose those releases only through an explicit reviewed bridge when a CRMtex assertion actually needs a term from the older dependency family. The bridge is **term-scoped, source-release-scoped, target-release-scoped, evidence-bound, and fail-closed**. Local identifiers such as `F28` or `I1`, or even a stable IRI reused across releases, are never sufficient by themselves to import the target release's axioms into the source release.

For the first R-011 pilots this matters less than R-006 initially suggested: the direct FRBRoo/CRMinf dependency surface in CRMtex 2.0 is concentrated around two activity classes:

- `TX2 Writing` → FRBRoo 2.4 `F28 Expression Creation`;
- `TX14 Reading` → CRMinf 0.7(b) `I1 Argumentation`.

The current CUC, TLHdig-TF, ORACC-TF and Pseudepigrapha-TF evidence does **not** require either activity class merely to model written-text segments, signs/glyph candidates, physical document navigation, or textual-critical readings. Therefore the first pilot should keep both bridges inactive unless a reviewed native selector actually denotes the corresponding activity.

## 1. Primary evidence

### 1.1 CRMtex 2.0

Authoritative sources:

- CRMtex 2.0 release page: <https://cidoc-crm.org/crmtex/ModelVersion/version-2.0>
- CRMtex 2.0 class/property declarations: <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>
- CRMtex 2.0 PDF: <https://cidoc-crm.org/sites/default/files/CRMtex_v2.0_June_2023.pdf>

CRMtex 2.0 was approved by the CIDOC CRM SIG in June 2023. Its declaration page explicitly identifies external references to CIDOC CRM 7.1.2, CRMinf 0.7(b), CRMsci 2.0 and FRBRoo 2.4.

The declarations establish two direct old-family superclass dependencies relevant to this ticket:

| CRMtex 2.0 term | formal dependency | meaning relevant to TFont |
|---|---|---|
| `TX2 Writing` | subclass of FRBRoo 2.4 `F28 Expression Creation` | physical/non-mechanical activity that creates a written text |
| `TX14 Reading` | subclass of CRMinf 0.7(b) `I1 Argumentation` | intellectual activity from text recognition to association with linguistic meaning |

Several CRMtex properties depend on those activities through their domain or shortcut definition:

| property | dependency path | implication |
|---|---|---|
| `TXP1 used writing system` | domain `TX2` | activating the property asserts a writing activity, so a consumer that follows superclass semantics reaches old FRBRoo `F28` |
| `TXP5 wrote` | domain `TX2`, range `TX1` | same old `F28` superclass dependency through the writing event |
| `TXP9 is encoded using` | shortcut via `TX1 <-TXP5- TX2 -TXP1-> TX3` | the shortcut can be used without materializing an event, but expanding the path invokes `TX2` and therefore its FRBRoo dependency |
| `TXP18 read` | domain `TX14`, range `TX1` | activating the property asserts a CRMtex reading activity and therefore old CRMinf `I1` superclass semantics |

The rest of the core written-text segmentation layer is not directly dependent on FRBRoo or CRMinf. Examples include `TX1 Written Text` (CIDOC CRM), `TX7 Written Text Segment` (subclass of `TX1`), `TX9 Glyph`, `TX12 Grapheme Sequence`, and `TX5 Text Recognition` (CRMsci/CIDOC CRM). This is why a selective bridge is preferable to rewriting CRMtex wholesale.

### 1.2 FRBRoo 2.4 → LRMoo 1.1.1

Authoritative sources:

- LRMoo 1.1.1 release: <https://cidoc-crm.org/lrmoo/ModelVersion/version-1.1.1>
- LRMoo 1.1.1 declarations: <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- LRMoo 1.1.1 specification/migration tables: <https://cidoc-crm.org/sites/default/files/LRMoo_V1.1.1.pdf>

The official FRBRoo 2.4 → LRMoo migration table explicitly maps:

```text
FRBRoo 2.4 F28 Expression Creation
    -> LRMoo 1.1.1 F28 Expression Creation
    status: Retained, editorial scope note revision
```

This is positive migration evidence. It is materially stronger than observing that both releases happen to contain the code `F28`.

Current LRMoo `F28 Expression Creation` remains an activity that externalizes/captures an expression and is a subclass of CIDOC CRM creation/production activity classes. The migration table therefore supports a reviewed type-continuity bridge for the limited purpose for which CRMtex `TX2` relies on old `F28`.

The migration table also demonstrates why blanket local-name equivalence is unsafe: numerous other FRBRoo terms were renamed, deprecated, merged into superclasses, or replaced by different paths. R-012 therefore approves only the evidenced `F28` continuity required by CRMtex `TX2`; it does not infer a general FRBRoo→LRMoo equivalence rule.

### 1.3 CRMinf 0.7(b) → CRMinf 1.2.1

Authoritative sources:

- CRMinf version history: <https://cidoc-crm.org/crminf/ModelVersions>
- CRMinf 1.2.1 declarations: <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>
- CIDOC SIG issue 721, “Interfacing CRMinf with CRMsci, CRMbase and CRMtex”: <https://cidoc-crm.org/crminf/Issue/ID-721-interfacing-crminf-with-crmsci-crmbase-and-crmtex>

The identifier/IRI for `I1 Argumentation` persists in current CRMinf, and its core scope remains the activity of making honest inferences or observations. However its formal hierarchy changed across the model's history. Current CRMinf 1.2.1 declares `I1` as a subclass of `E7 Activity` and gives it several specializations, while older CRMinf 0.7 material placed `I1` under a different hierarchy.

CIDOC SIG issue 721, closed in March 2026 during the work leading into current CRMinf documentation, explicitly revisited the interface of CRMinf with CRMsci, CRMbase and CRMtex. That is evidence of active harmonization, but it is **not** a term-by-term migration table saying that CRMtex 2.0 should be re-axiomatized against CRMinf 1.2.1.

Current CRMinf also defines `I16 Meaning Comprehension`, a subclass of `I1`, for interpreting the intended meaning of an information object as propositions. Its scope includes disambiguation, expansion of abbreviations, entity/reference resolution and completion of missing text. This is a useful modern semantic comparison for CRMtex `TX14 Reading`, but CRMtex 2.0 itself does not declare `TX14` as a subclass of `I16`.

Consequences:

1. the reused `I1` IRI does not authorize importing CRMinf 1.2.1's complete axiom set into CRMtex 2.0's CRMinf 0.7(b) closure;
2. no official term-level old-I1→current-I1 migration assertion equivalent to the LRMoo `F28` table was found;
3. any direct CRMtex `TX14` → current CRMinf target is therefore a reviewed TFont compatibility/projection decision, not an upstream CRMtex fact.

### 1.4 CIDOC CRM 7.1.2 → 7.1.3

Authoritative sources:

- CIDOC CRM 7.1.2: <https://cidoc-crm.org/Version/version-7.1.2>
- CIDOC CRM 7.1.3: <https://cidoc-crm.org/Version/version-7.1.3>

CIDOC CRM 7.1.3 is the subsequent official 7.1.x release associated with ISO alignment. R-012 does not replace CRMtex's declared 7.1.2 dependency in-place. The CRMtex closure remains locked to 7.1.2 while the current TFont heritage profile separately locks 7.1.3. R-015 should define how same-family release continuity participates in a bundle identity.

This keeps the general rule uniform: a newer release does not alter the meaning of an already-published mapping merely because it shares a namespace.

## 2. Bridge policy

### 2.1 Preserve the native CRMtex closure

A CRMtex 2.0 ontology lock must identify the release/snapshot and the external dependency releases against which its declarations were reviewed. TFont must not generate a patched copy that silently substitutes:

- CRM 7.1.3 for CRM 7.1.2;
- LRMoo 1.1.1 for FRBRoo 2.4;
- CRMinf 1.2.1 for CRMinf 0.7(b).

A separately published compatibility view could be useful later, but it would be a generated/reviewed TFont artifact with its own identity, evidence and digest, not “CRMtex 2.0”.

### 2.2 Bridge only assertions needed by an active mapping/query

A bridge is activated only when an approved semantic projection or an explicitly expanded CRMtex path requires the old external term.

For example:

```text
native writing-activity selector
  -> CRMtex 2.0 TX2 Writing
  -> [requires bridge] FRBRoo 2.4 F28
  -> LRMoo 1.1.1 F28
```

By contrast:

```text
native line selector
  -> CRMtex 2.0 TX7 Written Text Segment
```

has no reason to load or apply an F28/I1 bridge merely because those other classes occur elsewhere in CRMtex.

### 2.3 Missing bridge fails closed

If a resolution requires a bridge and any of these conditions fails, the cross-version semantic route is non-resolvable:

- source ontology release/digest does not match the reviewed bridge;
- target ontology release/digest does not match;
- bridge artifact is absent;
- bridge evidence/review is absent or invalid;
- a required intermediate dependency is not locked;
- the requested execution mode demands stronger semantic continuity than the bridge establishes.

The resolver may still use unaffected CRMtex projections whose dependency closure does not require that bridge.

### 2.4 Do not infer bridges from codes, names, or stable IRIs

Required negative rules:

- `F28` in two models is not sufficient evidence of continuity;
- `I1` in two releases is not sufficient evidence of unchanged formal semantics;
- identical English labels are not sufficient;
- a stable IRI does not mean release-specific superclasses/properties are identical;
- an ontology importer must not union old/new releases and reason over the result as though upstream published that composition.

## 3. Explicit bridge table

The table separates upstream evidence from TFont-local decisions. The `execution` column concerns use of the bridge in TFont's exact common-pivot resolution; it does not assert an RDF/OWL publication predicate.

| source in CRMtex 2.0 dependency closure | proposed current target | upstream evidence | TFont decision | exact execution |
|---|---|---|---|---|
| FRBRoo 2.4 `F28 Expression Creation` reached from `TX2 Writing` | LRMoo 1.1.1 `F28 Expression Creation` | official LRMoo migration table: **retained, editorial scope note revision** | accept a reviewed, release-locked continuity bridge for this term | allowed once the exact bridge artifact/locks are present |
| CRMinf 0.7(b) `I1 Argumentation` reached from `TX14 Reading` | CRMinf 1.2.1 `I1 Argumentation` | same maintained IRI and substantially continuous core scope, but hierarchy changed and no equivalent term-level migration table was found | do **not** treat current `I1` axioms as automatically substitutable; require a separately reviewed compatibility assertion if this route is needed | fail closed in exact mode until that assertion is accepted |
| CRMtex 2.0 `TX14 Reading` | CRMinf 1.2.1 `I16 Meaning Comprehension` | current `I16` is a specialization of `I1` for meaning interpretation; no CRMtex 2.0 upstream assertion links TX14 to I16 | TFont-local candidate only; target is semantically broader than the CRMtex written-text-specific activity and must be reviewed in R-009/R-011 | not exact-executable from R-012 alone |

R-012 deliberately does **not** publish `owl:equivalentClass` for either bridge. The runtime compatibility conclusion and RDF publication relation are independent under R-002. Even the migration-backed F28 continuity does not require TFont to mint an OWL equivalence assertion.

## 4. Pilot-use inventory

R-012 must identify every old-family CRMtex dependency term expected by the four pilots. The empirical result is that **none is required by the current first-pilot native contracts**.

### 4.1 CUC

R-005/R-007 evidence provides sign slots and `tablet → column → line` structure plus editorial sign features. Candidate CRMtex use is concentrated in written-text structure such as:

- `TX1 Written Text`;
- `TX7 Written Text Segment` for reviewed line/column/text portions;
- `TX9 Glyph` / `TX8 Grapheme` only after R-009/R-011 establishes whether the native sign semantics fit the physical/abstract distinction;
- `TX12 Grapheme Sequence` where a reviewed abstract sequence exists.

CUC does not expose a native writing-production activity or scholarly-reading activity. Therefore no first-pilot CUC mapping should activate `TX2`/`F28` or `TX14`/`I1` merely to model the tablet's text.

### 4.2 TLHdig-TF

R-005/R-007 provides sign slots, document/surface/column/line structures, fragments, explicit editorial objects and morphological analyses. Candidate written-text segmentation can use CRMtex where source semantics fit.

No inspected native object is automatically a `TX2 Writing` event. `edit` nodes are editorial events, not ancient writing-production events. `TX5 Text Recognition` is also not justified merely because a converter has produced sign data; an explicit scholarly recognition activity would require source evidence.

No native node is automatically a `TX14 Reading` activity. Morphological alternatives are analyses, not textual reading/comprehension events.

Old-family dependency terms expected in the first TLH pilot: **none**.

### 4.3 ORACC-TF

The ORACC-TF stress target contains document/surface/column/line/sign structures, lexical data, catalogue/object metadata and editorial/damage information. These support candidate CRM/CIDOC/CRMtex segmentation and heritage mappings.

Conversion from ORACC source data is not itself evidence for an ancient `TX2 Writing` activity. Likewise a source textual form, reading string or scholarly normalization is not automatically `TX14 Reading`.

Old-family dependency terms expected in the first ORACC pilot: **none**.

### 4.4 Pseudepigrapha-TF

The Pseudepigrapha-TF converter has explicit `unit`, `reading`, `variant_word`, `manuscript` and apparatus edges such as `reading_of` and `witness`. Its `reading` node denotes **one textual-critical reading/alternative at an apparatus locus**.

That object is not the CRMtex `TX14 Reading` class, which denotes an intellectual activity leading from text recognition toward linguistic meaning. Mapping the two solely because both use the English word “reading” would violate native-authority and no-label-inference rules.

The apparatus belongs primarily to R-009's LRMoo/CRMinf/textology analysis. A future source may separately record a scholar's act of reading/comprehending a manuscript, but that would be a distinct activity node/assertion.

Pseudepigrapha-TF also does not currently expose a native physical writing-production event for `TX2`.

Old-family dependency terms expected in the first Pseudepigrapha pilot: **none**.

### 4.5 Pilot dependency table

| pilot | candidate CRMtex layer | `TX2/F28` needed? | `TX14/I1` needed? | rule |
|---|---|---:|---:|---|
| CUC | written text / segment / glyph-grapheme candidates | no | no | physical/text segmentation does not imply production or reading activity |
| TLHdig-TF | written text / segment / glyph-grapheme; recognition only with explicit evidence | no | no | editorial/conversion activity is not ancient writing or CRMtex reading |
| ORACC-TF | written text/sign segmentation alongside CRM object metadata | no | no | source strings/normalizations are not activity assertions |
| Pseudepigrapha-TF | apparatus primarily through R-009; CRMtex only where a real physical-written-text assertion exists | no | no | apparatus `reading` is not TX14 |

This is not a declaration that the bridges are unnecessary to TFont. It means they are **available but dormant** for the first empirical pilots. A later corpus profile may legitimately activate them when native evidence contains a writing event or meaning-comprehension/reading activity.

## 5. Modern CRMinf mapping for reading semantics

Current `I16 Meaning Comprehension` is a better semantic comparison for CRMtex `TX14` than generic current `I1`, because its explicit subject is interpretation of the intended meaning of an information object. However there are still important differences:

- `TX14` is specific to reading written text and explicitly begins from CRMtex text-recognition semantics;
- `I16` applies to meaning comprehension of information objects generally;
- `I16` can cover interpretive work such as disambiguation and completing missing text;
- CRMtex 2.0 did not publish `TX14 ⊑ I16` because that current class was not part of its declared dependency model.

Therefore a future TFont projection from TX14 to current I16 is at most a reviewed **broader-target candidate** under the R-002 direction convention (the target is broader than the source). R-009 must decide whether the textology profile needs it; R-011 must test actual corpus cases; R-016 owns whether such a non-exact projection may execute in approximate mode.

R-012 does not make it executable.

## 6. CRMsci 2.0 remains a separate version-composition dependency

CRMtex `TX5 Text Recognition` is a subclass of CRMsci `S4 Observation` as well as CIDOC CRM `E65 Creation`, and several CRMtex recognition properties refer to CRMsci observation semantics.

R-012's explicit question is the CRMtex↔LRMoo/CRMinf bridge. It would be unsafe to solve that question while silently replacing CRMtex's CRMsci 2.0 dependency with a newer CRMsci release. Therefore:

- CRMtex 2.0's native lock must retain CRMsci 2.0;
- if P-003/R-010 wants a current CRMsci profile in the same bundle, R-015 must treat its compatibility as another explicit composition edge;
- no first-pilot `TX5` mapping is accepted merely because a corpus has a transcription or converter output.

This is a required guardrail, not a new broad CRMsci migration study inside R-012.

## 7. Bridge artifact and provenance requirements

R-015 owns the final bundle schema. R-012 establishes minimum semantic requirements for any bridge artifact:

```text
bridge identity
source ontology/profile id
source release/snapshot + content digest
source term IRI

target ontology/profile id
target release/snapshot + content digest
target term IRI

bridge purpose / allowed semantic use
evidence references + immutable evidence digests where archived
review decision + reviewer identity/date
runtime strength/limitations
optional publication relation, independently justified
bridge artifact digest
```

A semantic resolution that depends on a bridge must expose the bridge identity in its explanation/provenance chain. The effective semantic-bundle identity must change when the bridge artifact or either endpoint lock changes.

Updating LRMoo/CRMinf later does not mutate an existing bridge. It creates a new bridge review and therefore a new bundle identity.

## 8. Negative tests required by P-003/R-015

The following should become contract/regression tests when the bridge/bundle schema is implemented:

1. **same-code trap:** FRBRoo `F28` and LRMoo `F28` without the reviewed migration-backed bridge → fail closed;
2. **same-IRI trap:** CRMinf old/current `I1` with different release locks but no reviewed compatibility assertion → no release-axiom substitution;
3. **wrong target release:** bridge approved for LRMoo 1.1.1 presented with another LRMoo digest → fail closed;
4. **missing source lock:** CRMtex TX2 mapping without exact CRMtex/FRBRoo source locks → fail closed;
5. **blanket migration:** presence of an F28 bridge must not authorize unrelated FRBRoo→LRMoo term rewrites;
6. **apparatus reading collision:** Pseudepigrapha `reading` → CRMtex TX14 based on label alone → rejected;
7. **editorial-event collision:** TLHdig `edit` → CRMtex TX2 based on generic creation/editing vocabulary → rejected;
8. **converter-as-recognition:** generated sign/transcription data → TX5 without a native scholarly recognition activity → rejected;
9. **old/new union reasoning:** loading both dependency releases must not generate mappings not explicitly present in reviewed TFont indexes;
10. **bridge mutation:** changing target ontology digest or bridge evidence while retaining prior semantic-bundle identity → validation failure.

## 9. Inputs to P-003

P-003 should incorporate these reviewed R-012 constraints unless later research supersedes them:

1. CRMtex 2.0 remains a versioned profile with its declared dependency closure; current ontologies do not replace dependencies in place.
2. Cross-version compatibility is represented through explicit bridge artifacts, not implicit import graph substitution.
3. Bridge activation is term/query scoped.
4. FRBRoo 2.4 `F28` → LRMoo 1.1.1 `F28` has official migration evidence sufficient for a reviewed continuity bridge.
5. CRMinf old `I1` → current `I1` requires an explicit compatibility decision because hierarchy/axioms changed; stable IRI alone is insufficient.
6. CRMtex `TX14` → current CRMinf `I16` is a TFont-local broader-target candidate, not an upstream migration assertion and not exact-executable from this research.
7. Bridge identity/evidence/digests participate in the effective ontology-bundle identity and explanation chain.
8. The first R-011 pilots can use CRMtex written-text/segment semantics without activating TX2/F28 or TX14/I1 bridges unless new native evidence demonstrates those activities.
9. Pseudepigrapha textual-critical `reading` must not be mapped to CRMtex TX14 by label similarity.
10. CRMsci 2.0 remains part of CRMtex's native closure and must not be silently upgraded when TX5/recognition semantics are used.

## 10. Rejected alternatives

### A. Rewrite CRMtex 2.0 against current namespaces

Rejected. It would create a TFont-modified ontology whose semantics differ from the upstream release while retaining an upstream-looking identity.

### B. Import old and current models together and let OWL reasoning reconcile them

Rejected. The upstream specifications do not publish one coherent import closure across these release generations, and migration is not term-for-term identity.

### C. Bridge every retained local code automatically

Rejected. The official FRBRoo→LRMoo migration table itself contains retained, renamed, deprecated, merged and path-replaced cases. Code reuse is evidence to investigate, not a mapping decision.

### D. Treat stable IRI as release-independent axiom identity

Rejected. R-002 already separates stable term URI from tested release/snapshot. CRMinf `I1` demonstrates why the distinction is operationally necessary.

### E. Map all corpus “reading” objects to CRMtex TX14

Rejected. Pseudepigrapha's `reading` is a textual-critical alternative, while TX14 is an intellectual reading/comprehension activity.

### F. Defer CRMtex entirely until a future release

Rejected. The stable 2.0 written-text/segment layer is already useful, and the problematic old-family dependency surface is narrow enough to isolate safely.

## 11. Acceptance-criteria trace

- [x] Enumerated the relevant CRMtex 2.0 cross-version dependencies and the CRMtex properties that activate them.
- [x] Inspected official FRBRoo 2.4 → LRMoo migration evidence for the required `F28` term.
- [x] Inspected old/current CRMinf `I1` semantics and current `I16 Meaning Comprehension`, including the 2026 CIDOC SIG CRMtex/CRMinf harmonization work.
- [x] Distinguished official migration evidence from TFont-local compatibility/projection decisions.
- [x] Provided an explicit pilot table for Pseudepigrapha-TF, CUC, ORACC-TF and TLHdig-TF; none currently requires the old F28/I1 bridge terms.
- [x] Defined a selective fail-closed bridge policy and negative tests for code/IRI equivalence mistakes.
- [x] Defined minimum bridge-lock/provenance requirements for R-015/P-003.
- [x] Preserved the native CRMtex 2.0 closure rather than silently upgrading its dependencies.

## 12. Authoritative references

- CRMtex 2.0 release: <https://cidoc-crm.org/crmtex/ModelVersion/version-2.0>
- CRMtex 2.0 declarations: <https://cidoc-crm.org/extensions/crmtex/html/CRMtex_v2.0.html>
- CRMtex 2.0 specification PDF: <https://cidoc-crm.org/sites/default/files/CRMtex_v2.0_June_2023.pdf>
- LRMoo 1.1.1 release: <https://cidoc-crm.org/lrmoo/ModelVersion/version-1.1.1>
- LRMoo 1.1.1 declarations: <https://cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.1.1.html>
- LRMoo 1.1.1 specification/migration tables: <https://cidoc-crm.org/sites/default/files/LRMoo_V1.1.1.pdf>
- CRMinf releases: <https://cidoc-crm.org/crminf/ModelVersions>
- CRMinf 1.2.1 declarations: <https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html>
- CIDOC SIG issue 721: <https://cidoc-crm.org/crminf/Issue/ID-721-interfacing-crminf-with-crmsci-crmbase-and-crmtex>
- CIDOC CRM 7.1.2: <https://cidoc-crm.org/Version/version-7.1.2>
- CIDOC CRM 7.1.3: <https://cidoc-crm.org/Version/version-7.1.3>

Internal corpus evidence is pinned in [R-005](R-005-corpus-semantic-census.md), and the structural carrier/extent guardrails are in [R-007](R-007-tf-structural-semantics.md).