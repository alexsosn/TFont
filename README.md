# TFont

TFont is an experimental semantic interoperability layer for Text-Fabric / Context-Fabric corpora. It projects corpus-native node types, features, edge relations, and controlled values toward shared open semantic standards while keeping the native corpus and its scholarly analysis authoritative.

## Current status

TFont is an active proof-of-concept implementation. The foundational research and P-001 architecture are merged, together with two production foundations on `main`:

- structural source validation (I-001);
- deterministic canonicalization and digest primitives (I-002).

Parent-component identity, cross-artifact semantic validation, compatibility evaluation, compiler/runtime resolution, and corpus-specific mappings are later implementation stages and should not be treated as shipped capabilities yet.

## Implemented capabilities

### Structural source validation

TFont currently provides:

- strict UTF-8 YAML and JSON loading;
- duplicate-key rejection and conversion to a plain JSON-compatible value model;
- rejection of non-JSON values such as non-finite numbers or non-string mapping keys;
- seven local JSON Schema Draft 2020-12 structural contracts;
- stable `SourceValidationError` diagnostics for decode, source-model, schema, and structural-validation failures.

This layer performs structural validation only. Cross-artifact references, ontology terms, evidence bindings, review bindings, and compatibility state are not validated by I-001.

### Canonicalization and digests

TFont also provides deterministic identity primitives for:

- RFC 8785/JCS canonical JSON bytes;
- normalized source-file and source-bundle digests;
- exact evidence-payload and normalized evidence-record digests;
- mapping semantic digests;
- profile semantic digests for an already assembled semantic projection;
- stable `DigestError` diagnostics for canonicalization and projection failures.

These helpers compute deterministic projections and digests; they do not resolve or verify cross-artifact semantic relationships.

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
- [`docs/research/`](docs/research/) contains the research record.
- [`docs/plans/`](docs/plans/) contains accepted and active implementation plans.
- [GitHub Issues](https://github.com/alexsosn/TFont/issues) tracks implementation and follow-up work.
