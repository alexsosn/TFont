# TFont

TFont is an experimental semantic interoperability layer for Text-Fabric / Context-Fabric corpora. It projects corpus-native node types, features, edge relations, and controlled values toward shared open semantic standards while keeping the native corpus and its scholarly analysis authoritative.

## Current status

TFont is an active proof-of-concept implementation. The foundational research and accepted architecture are merged, together with three production foundations on `main`:

- structural source validation;
- deterministic canonicalization and digest primitives;
- parent/component identity for files, directories, Text-Fabric payloads, and expected-parent manifests.

The common ontology semantic-adapter is now accepted architecture: reviewed corpus-native semantic records can carry typed semantic-pivot or authority-value projections while identity, catalogue, provenance, and locator references remain separate. Ambiguous, native-only, and unsupported states remain explicit and fail closed rather than being guessed into shared targets.

Cross-artifact semantic validation, compatibility evaluation, semantic IR/compiler and runtime resolution, and corpus-specific mappings are not yet shipped capabilities. The accepted semantic architecture defines those later stages; it does not mean the validator or resolver is already implemented on `main`.

## Implemented capabilities

### Structural source validation

TFont currently provides:

- strict UTF-8 YAML and JSON loading;
- duplicate-key rejection and conversion to a plain JSON-compatible value model;
- rejection of non-JSON values such as non-finite numbers or non-string mapping keys;
- local JSON Schema Draft 2020-12 structural contracts;
- stable `SourceValidationError` diagnostics for decode, source-model, schema, and structural-validation failures.

This layer performs structural validation only. Cross-artifact references, ontology terms, evidence bindings, review bindings, and compatibility state are not validated by the structural loader.

### Canonicalization and digests

TFont also provides deterministic identity primitives for:

- RFC 8785/JCS canonical JSON bytes;
- normalized source-file and source-bundle digests;
- exact evidence-payload and normalized evidence-record digests;
- mapping semantic digests;
- profile semantic digests for an already assembled semantic projection;
- stable `DigestError` diagnostics for canonicalization and projection failures.

These helpers compute deterministic projections and digests; they do not resolve or verify cross-artifact semantic relationships.

### Parent/component identity

TFont can compute stable identities for the materialized corpus components that semantic metadata is expected to describe:

- exact file content identity;
- recursive directory file-set identity with symlinks and unsupported entries rejected;
- Text-Fabric payload identity;
- deterministic expected-parent manifest projections and digests;
- stable `IdentityError` diagnostics for invalid paths, filesystem failures, and unsupported filesystem objects.

These functions establish what corpus material a profile or mapping is meant to apply to. They do not by themselves declare that the parent is semantically compatible with a profile or ontology mapping.

## Accepted semantic architecture

The accepted common ontology semantic-adapter architecture keeps native Text-Fabric / Context-Fabric semantics authoritative and adds reviewed, explicit interoperability metadata around them.

In that model:

- one native semantic record may have zero or more approved typed target-bearing projections;
- shared semantic-pivot targets and authority-value targets are routed separately;
- entity identity, catalogue identifiers, provenance sources, and locators are typed external references rather than semantic targets;
- ambiguous candidates are recorded but are not approved or executable;
- native-only and unsupported records remain legitimate reviewed no-target states;
- ontology locks, bundle/bridge closure, evidence/review binding, and approximation policy are explicit prerequisites for later semantic execution;
- TFont does not silently infer mappings from feature names, URI spelling, observed values, or ontology labels.

This is accepted architecture, not yet shipped cross-artifact semantic validation or runtime resolution.

## Development install

TFont currently targets Python 3.10 or newer. From a repository checkout:

```bash
python -m pip install -e .
```

The project does not currently document a published package release as the supported installation path.

## Minimal usage

Strict source parsing:

```python
from tfont import loads_source

data = loads_source("a: [1, true, null, text]\n", format="yaml")
```

Load and structurally validate a caller-owned profile source:

```python
from tfont import load_and_validate

profile = load_and_validate("path/to/profile.yaml", "profile")
```

Canonicalization and source digests:

```python
from tfont import canonical_json_bytes, source_file_digest

canonical = canonical_json_bytes({"b": 2, "a": 1})
digest = source_file_digest(b"a: 1\r\n")
```

Parent/component identity:

```python
from tfont import directory_component_digest, parent_manifest_digest

directory = directory_component_digest("path/to/materialized-corpus")
manifest = parent_manifest_digest({
    "schema_version": 1,
    "components": [
        {
            "component_id": "corpus",
            "component_type": "directory",
            "algorithm": directory["algorithm"],
            "digest": directory["digest"],
        }
    ],
})
```

## Interoperability targets

Initial interoperability targets include:

- ETCBC BHSA;
- DT-UCPH CUC;
- ETCBC Syriac corpora, including `syriac`, `peshitta`, and `syrnt` where applicable;
- ETCBC `extrabiblical`;
- TLHdig-TF.

These are target corpora for the interoperability work, not a claim that finished TFont profiles or mappings already exist for each corpus.

## Project contracts and contributing

- [`AGENTS.md`](AGENTS.md) defines the automated research/design/TDD/review development loop.
- [`docs/plans/P-001-foundation-poc-design.md`](docs/plans/P-001-foundation-poc-design.md) is the accepted foundation POC design.
- [`docs/plans/P-003-common-ontology-semantic-adapter-plan.md`](docs/plans/P-003-common-ontology-semantic-adapter-plan.md) defines the accepted common ontology semantic-adapter architecture.
- [`docs/research/`](docs/research/) contains the research record.
- [`docs/plans/`](docs/plans/) contains accepted and active implementation plans.
- [GitHub Issues](https://github.com/alexsosn/TFont/issues) tracks implementation and follow-up work.
