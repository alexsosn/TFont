# R-005 candidate mapping-strength matrix

This is the explicit semantic-classification companion to the representation matrix in
`R-005-corpus-semantic-census.md`. The older table answers **what native evidence is
present**; this table answers **how strong the apparent semantic match is allowed to be
at the census stage**.

These are conservative *candidate* classifications for architecture research, not
approved ontology mappings. A later mapping PR must justify its target ontology term
and may weaken a classification; it may not silently strengthen one.

## Codes

| code | classification | meaning in this census |
|---|---|---|
| `S` | same | native assertion is a defensible instance of the row-level concept at this abstraction level |
| `C` | close | materially similar evidence, but not interchangeable without corpus-specific qualification |
| `B` | broader | native assertion is broader than the row-level concept |
| `N` | narrower | native assertion is narrower than the row-level concept |
| `R` | related | semantically related evidence exists but it is the wrong substitute for the row-level concept |
| `U` | unknown | no adequate native evidence / unsupported / semantics not established at the pinned revision |
| `L` | local-only | a language- or annotation-system-specific category should remain local at this abstraction level |

`S` is deliberately weaker than OWL identity/equivalence. It says that the row-level
cross-corpus concept is defensible for discovery/query planning; it does not license
`owl:sameAs`, `owl:equivalentClass`, or value-level equivalence.

## Matrix

| semantic cluster | BHSA | CUC | Syriac 0.9 | Peshitta 0.2 | SyrNT 0.1 | ExtraBiblical 0.2 | TLHdig-TF | Pseudepigrapha-TF | ORACC-TF target |
|---|---|---|---|---|---|---|---|---|---|
| TF slot role | `S` word slot | `S` sign slot | `S` word slot | `S` word slot | `S` word slot | `S` word slot | `S` sign slot | `S` word slot | `S` sign slot |
| word/token entity | `S` word | `S` word over signs | `S` word | `S` word | `S` word | `S` word | `S` word over signs | `S` word | `S` word over signs |
| written sign / grapheme entity | `U` | `C` alphabetic sign | `U` | `U` | `U` | `U` | `C` cuneiform sign | `U` | `C` semantic GDL sign |
| lexical entry/entity | `S` `lex` node | `U` | `R` lexical identity is a word feature, not an entry node | `U` | `S` `lexeme` node | `R` lexical identity without BHSA-style `lex` node | `S` `lex` node; `oslots` is anchor-only | `R` lexical fields do not by themselves establish a shared entry entity | `S` explicit `lex` target entity |
| lemma/root/gloss information | `C` native lexical families | `U` | `C` `lex/g_lex/gloss/ls` | `U` | `C` SEDRA-derived lexical/root data | `C` lexical features | `C` analysis `lemma/gloss` | `C` source lexical fields where present | `C` `cf/gw/sense` and lexical key |
| part of speech | `C` BHSA `sp/pdp` inventories | `U` | `C` Syriac `sp` inventory | `U` | `C` SyrNT categories | `C` ETCBC POS features | `C` analysis `pos` when field 4 is POS | `C` when supplied by source | `C` source `pos/epos` |
| gender / number / person | `C` grammatical categories | `U` | `C` grammatical categories | `U` | `C` grammatical categories | `C` grammatical categories | `C` only where encoded in parsed morphology | `U` unless the source supplies a corresponding analysis | `C` only where source analysis supplies them |
| verbal stem / tense-aspect category | `L` Hebrew/BHSA value system | `U` | `L` Syriac value system | `U` | `L` SEDRA/Syriac stem system | `L` ETCBC Hebrew-family value system | `L` Hittite analysis tags/stem classes | `U` unless source-specific analysis supplies one | `L` Akkadian/source-specific morphological categories |
| phrase | `S` functional phrase | `U` | `U` | `U` | `U` | `S` ETCBC functional phrase | `U` | `U` unless explicitly sourced as linguistic phrase | `C` explicit `c type=phrase` source chunk only |
| clause | `S` functional clause | `U` | `U` | `U` | `U` | `S` ETCBC functional clause | `U` | `U` | `U` |
| linguistic sentence | `S` functional sentence | `U` | `U` | `U` | `U` | `S` ETCBC functional sentence | `U` | `U` | `U` source `c type=sentence` is implicit chunking, not established linguistic sentence |
| syntactic dependency | `S` `mother` | `U` | `U` | `U` | `U` | `S` `mother` | `U` | `R` source structural `parent` is not automatically linguistic dependency | `U` unless a source relation is independently documented as syntactic |
| hierarchical parent relation | `S` `functional_parent` / `distributional_parent` | `U` | `U` | `U` | `U` | `S` `functional_parent` / `distributional_parent` | `U` | `C` source structural `parent`; semantics differ from ETCBC functional/distributional hierarchy | `U` |
| discourse / text category | `S` `domain/txt` etc. | `U` | `U` | `U` | `U` | `S` ETCBC discourse/text features | `R` project/language/editorial metadata is not BHSA discourse | `R` structural/editorial grouping may be relevant but is not a shared discourse taxonomy | `C` source `discourse`/genre metadata when present |
| biblical book/chapter/verse structure | `S` | `U` | `S` | `S` | `S` | `S` | `U` | `S` where converter source hierarchy is book/chapter/verse | `U` |
| physical document / tablet | `U` textual books are not physical manuscripts | `C` physical `tablet` | `U` | `U` | `U` | `U` | `C` `document` can represent manuscript/tablet records | `R` edition/work/version nodes require source-specific interpretation | `C` corpusjson `document`/object record |
| surface / column / physical line | `U` | `C` column/line plus side feature | `U` | `U` | `U` | `U` | `S` surface/column/line hierarchy | `R` textual loci/lines must be distinguished from physical layout unless source asserts it | `S` face/column/line target hierarchy |
| witness entity / attestation source | `U` | `U` | `U` | `R` `witness=A/B` is book-edition designation, not reading-attestation entity | `U` without an explicit equivalent apparatus entity | `U` | `C` line→fragment witness relation, not reading→manuscript attestation | `S` explicit manuscript/witness entities in apparatus model | `R` exemplars/edition metadata are related but not a critical-reading witness relation |
| reading / textual variant | `C` qere is a specific reading tradition, not a generic critical-apparatus reading graph | `C` sign-level `alt` is an alternative reading | `U` | `U` | `U` | `U` | `U` candidate morphological analyses are not textual variants | `S` explicit reading/variant structure | `R` source editorial alternatives only where explicitly represented; no generic equivalence assumed |
| omission / explicit unattested state | `U` | `R` missing/excised/restored material concerns text/material state, not witness non-attestation | `U` | `U` | `U` | `U` | `R` lacuna/damage is not witness absence | `S` explicit omission/unattested distinctions where source encodes them | `R` missing/break data is not automatically witness non-attestation |
| damage / restoration state | `U` | `C` `emen` restoration/missing/excised/redundant model | `U` | `U` | `U` | `U` | `S` explicit damage-range `cluster` families and induced flags | `R` apparatus omission/restoration can be related but has different evidence model | `C` GDL `damage/missing` and editorial structure |
| uncertainty / confidence | `U` no generic certainty layer established by this census | `C` `cert` is sign-level certainty; observed values are boolean strings in 0.2.8 | `U` | `U` | `U` | `U` | `C` `corr`, parser/alignment evidence and source-specific marks have distinct meanings | `C` reading/editorial uncertainty when explicitly sourced | `C` source-specific uncertainty/qualification where present |
| material / object type | `U` | `R` tablet metadata is limited; do not infer a general material ontology from tablet identity | `U` | `U` | `U` | `U` | `C` inventory/join/document metadata can describe physical witnesses but is not ORACC catalogue schema | `R` manuscript/resource metadata is source-specific | `S` catalogue `material`, `object_type`, exemplars and related fields |
| geographic / archaeological provenance | `U` | `R` tablet metadata may carry relevant identifiers but no shared provenance model established | `U` | `U` | `U` | `U` | `R` CTH/project/source provenance is editorial/source provenance, not necessarily findspot | `R` source/manuscript provenance is not automatically archaeological provenience | `S` catalogue `provenience` plus Pleiades identifiers/coordinates where populated |
| scholarly / editorial event | `R` analyst/encoding provenance exists but is not TLHdig-style event graph | `C` `emen`/alternative/certainty assertions are editorial states rather than event nodes | `U` | `U` | `U` | `R` encoded linguistic analysis provenance is not an event graph | `S` explicit `edit` nodes with event kind/editor/date and `edits` edge | `C` apparatus/editorial structures and anomalies are explicit but source model differs | `C` editorial/source structures and metadata when explicitly represented |

## Critical non-equivalences pinned by the matrix

1. **ORACC `sentence` stays `U` for linguistic sentence.** Its implicit source chunks do not become BHSA sentences because the source label happens to be `sentence`.
2. **Witness is not one predicate.** Peshitta A/B designation is `R`, TLHdig line→fragment is `C`, and Pseudepigrapha reading/witness apparatus is `S` for the row-level critical-attestation concept.
3. **TLHdig lexical containment is not occurrence extent.** The lexical entity itself can be `S`, while its `oslots` is explicitly anchor-only; occurrence queries must use `analysis -> lexeme -> lex`.
4. **Verbal systems remain `L`.** Shared English labels such as “stem” or historical relationships between Hebrew/Syriac categories do not license value equivalence.
5. **Damage, omission and uncertainty remain separate rows.** CUC `emen`, CUC `cert`, TLHdig clusters, ORACC break/damage, and Pseudepigrapha omission/attestation states cannot be collapsed into one generic boolean.
6. **Dependency and hierarchy remain separate rows.** ETCBC `mother` is the native linguistic-dependency edge; `functional_parent` and `distributional_parent` are hierarchical parent relations. Pseudepigrapha structural `parent` is related to hierarchy but is not silently reclassified as syntactic dependency.

This matrix is the required initial classification. Final ontology mappings belong to later design/implementation tickets and require term-level evidence and independent review.
