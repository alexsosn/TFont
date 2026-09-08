# P-003 normative vocabulary freeze

**Issue:** #44  
**Status:** normative companion to `P-003-common-ontology-semantic-adapter.md`

This file resolves the naming boundary explicitly delegated to P-003 by R-013/R-014/R-017. These spellings are canonical production identifiers for contract version 1. They are not examples or aliases.

## 1. Formal target kinds

Exactly:

```text
class
property
skos-concept
named-resource
```

## 2. Semantic roles

Exactly:

```text
entity-type
annotation-category
annotation-value
relation
attribute
lexical-entry-identity
lexical-form-identity
lexical-sense-identity
lexical-concept-identity
authority-reference
claim-proposition
inference-activity
```

## 3. Target-bearing reference kinds and query roles

Exactly:

```text
reference_kind:
  semantic-pivot
  authority-value

query_role:
  semantic-constraint
  authority-value-filter
```

Valid routing pairs are exactly:

```text
semantic-pivot  + semantic-constraint
authority-value + authority-value-filter
```

Cross-pairing is invalid in v1.

## 4. Non-projection external-reference kinds

Exactly:

```text
entity-identity
catalogue-identifier
provenance-source
locator
```

Their first query roles are exactly:

```text
identity-filter
identifier-filter
metadata-filter
explanation-only
```

Allowed v1 routing is:

```text
entity-identity       -> identity-filter
catalogue-identifier  -> identifier-filter
provenance-source     -> metadata-filter | explanation-only
locator               -> explanation-only
```

`metadata-filter` requires an explicitly reviewed native metadata binding and the same derived upstream execution prerequisite as every other executable plan. It is not URI querying or dereferencing.

## 5. Entity identity strength

Exactly:

```text
same-entity
probable-same-entity
related-record
ambiguous-identity
```

No R-002 broader/narrower/close assessment is accepted as entity-identity strength.

## 6. Mapping/projection assessment

The accepted eight meanings remain exactly:

```text
exact
close
broader
narrower
related
ambiguous
native-only
unsupported
```

Approved target-bearing projections use only:

```text
exact | close | broader | narrower | related
```

Native-record unresolved/no-target states use only:

```text
ambiguous | native-only | unsupported
```

Ambiguous candidate `assessment_candidate` uses only the five target-bearing assessment spellings.

## 7. Profile operational state

Exactly:

```text
active
absent
unavailable
```

No mapping-strength token is valid as a profile/capability operational state.

## 8. Core profile IDs

Exactly:

```text
structural
linguistic
lexical
written-text
textology
heritage
scholarly-inference
archaeology
scientific-analysis
lexicography
```

The last three remain optional/evidence-gated; canonical ID existence does not imply activation.

## 9. Core capability IDs

Exactly the R-014 first catalog:

```text
structural.entity-kind
structural.slot-coverage
structural.edge-traversal
structural.section-navigation

linguistic.part-of-speech
linguistic.morphology
linguistic.syntax
linguistic.discourse

lexical.entry
lexical.form
lexical.sense
lexical.concept
lexical.relation

written-text.segment
written-text.sign
written-text.writing-system
written-text.transcription-recognition

textology.textual-version
textology.witness
textology.fragment-transmission
textology.apparatus-reading
textology.witness-attestation
textology.explicit-omission

heritage.physical-object
heritage.physical-part
heritage.identifier
heritage.material
heritage.place-provenance
heritage.custody-location

scholarly-inference.claim
scholarly-inference.inference
scholarly-inference.meaning-comprehension
scholarly-inference.provenance-assessment
```

P-003 does not invent optional-profile capability IDs before an accepted profile contract demonstrates their recurring query semantics. Unknown capability IDs fail closed until introduced by a versioned catalog amendment.

## 10. Approximation vocabulary

Exactly:

```text
semantic_mode:
  exact
  approximate

loss tokens:
  undercoverage
  overcoverage
```

Bidirectional loss is represented by both tokens, not a third alias.

## 11. Alias and versioning rule

Canonical identifiers above participate in schema and semantic identity.

- aliases are not silently accepted;
- case variants are not aliases;
- URI/local-name inference does not canonicalize unknown values;
- adding or renaming a formal kind, role, profile, capability, routing kind, query role, identity strength, assessment or loss token requires a versioned contract/catalog amendment;
- released mappings retain their original contract vocabulary and are never reinterpreted under newer spellings automatically.

Public RDF/URI packaging may assign stable IRIs to these identifiers later, but the v1 machine contract uses the exact canonical strings above. An RDF packaging IRI must map one-to-one to a canonical token and must not create a second accepted runtime spelling.
