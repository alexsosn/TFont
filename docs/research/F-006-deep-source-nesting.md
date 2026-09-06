# F-006 research: fail closed on deeply nested source input

**Issue:** #32  
**Recorded:** 2026-09-06  
**Baseline:** `main` at `2dc7ab12781226566d0ec1eb49c99872990902c7`

## Question

Can I-001's public source-loading APIs leak a raw recursion/runtime exception for deeply nested JSON/YAML, and if so what is the smallest repair that preserves the accepted source language and stable error contract?

## Accepted TFont contract

`docs/plans/I-001-structural-validator-plan.md` defines:

- `loads_source(text, *, format, source_name)` and `load_source(path)` as strict JSON/YAML loading boundaries;
- a recursively plain JSON-compatible return model;
- stable `SourceValidationError` categories including `decode_error`, `duplicate_key`, and `non_json_value`;
- exact third-party exception prose as diagnostic-only rather than part of the stable API;
- no semantic canonicalization or digest behavior in I-001.

The implementation on the baseline has two independent recursion surfaces:

1. JSON/YAML parser construction of a deeply nested Python value.
2. `_plain_json()` recursively copying lists/mappings into the plain JSON-compatible model.

`_plain_json()` has active-container cycle detection, but no nesting guard and no `RecursionError` translation. A sufficiently deep acyclic value can therefore exhaust the Python call stack while still consisting only of otherwise supported list/dict/scalar types.

## Python JSON behavior

Python 3.12 `json` documentation states that deserializer implementations may impose limits such as maximum nesting, while the stdlib module itself imposes no limits beyond Python datatype/interpreter limits. The documented invalid-document exception is `JSONDecodeError`, but runtime/interpreter resource limits are a separate implementation boundary.

Primary source:
- https://docs.python.org/3.12/library/json.html#implementation-limitations
- https://docs.python.org/3.12/library/json.html#json.loads

Implication for TFont: code that only catches `JSONDecodeError`/`ValueError` cannot assume every excessive-nesting failure is normalized into the I-001 error contract.

## ruamel.yaml 0.19.x behavior

TFont pins `ruamel.yaml>=0.19.1,<0.20` and uses `YAML(typ="safe", pure=True)`.

ruamel.yaml 0.19 introduced a `YAML.max_depth` control which, when explicitly set, raises `MaxDepthExceededError` after the configured depth. The project documentation presents this as a control for unchecked input.

Primary sources:
- https://yaml.dev/doc/ruamel.yaml/
- https://yaml.dev/doc/ruamel.yaml/api/
- https://pypi.org/project/ruamel.yaml/0.19.1/

However, I-001 never defined a maximum source depth. Enabling `max_depth` in F-006 would therefore create a new accepted-language restriction rather than merely repairing exception normalization.

## Reproduction mechanism

The current `_plain_json()` implementation recursively calls itself once per nested list/mapping layer. Python's recursion limit is finite and runtime-dependent. Therefore an acyclic value nested beyond the available Python stack can raise raw `RecursionError` during normalization even if the parser successfully produced it.

The same class of raw exception may originate earlier in a parser for sufficiently deep input. Both locations are part of the public source-loading boundary and should be normalized consistently.

## Category decision

Use **`decode_error`** for excessive-nesting recursion failures.

Reasons:

- the input is not rejected because a parsed scalar/container has an unsupported JSON type; therefore `non_json_value` would misdescribe the failure;
- the failure occurs while turning serialized source into the accepted source value;
- `decode_error` already owns parser/configuration/source-decoding failures;
- this keeps the existing stable category set unchanged.

The diagnostic message may include the underlying `RecursionError` text because I-001 explicitly treats third-party/runtime prose as diagnostic-only.

## Minimal repair

Do **not** add an explicit maximum nesting constant in F-006.

Instead:

1. JSON parser boundary: catch `RecursionError` alongside JSON decode/value failures and raise `SourceValidationError(category="decode_error", source_name=...)`.
2. YAML parser boundary: catch `RecursionError` alongside `YAMLError` and raise the same stable category.
3. Plain-model normalization boundary: catch `RecursionError` around `_plain_json()` and translate it to `decode_error` while allowing existing `SourceValidationError` (`non_json_value`, etc.) to pass through unchanged.

Important implementation detail: do **not** simply move `_plain_json()` into the existing JSON `try` that catches `ValueError`, because `SourceValidationError` subclasses `ValueError`; doing so would incorrectly convert existing `non_json_value` errors into `decode_error`.

A small helper such as `_normalize_loaded(value, source_name=...)` can isolate the `RecursionError` translation safely.

## TDD matrix

RED regressions should use nesting derived from `sys.getrecursionlimit()` rather than a magic fixed depth so they reliably exceed the active interpreter stack on Python 3.10/3.12.

Required failures before production repair:

- deeply nested JSON through `loads_source(..., format="json", source_name="deep.json")` must currently leak `RecursionError`, while the test expects `SourceValidationError/decode_error` with source name preserved;
- deeply nested YAML through `loads_source(..., format="yaml", source_name="deep.yaml")` must likewise not leak a raw recursion failure after repair.

Controls:

- moderately nested ordinary JSON/YAML still round-trip to the same plain value;
- duplicate JSON/YAML keys retain `duplicate_key`;
- non-finite YAML retains `non_json_value`;
- non-finite JSON retains `decode_error`;
- custom source names remain preserved.

If one parser independently rejects the chosen deep fixture with a parser-specific `YAMLError` instead of `RecursionError`, that path is already normalized and should be treated as a control, not forced into an artificial RED. The RED requirement is satisfied by a demonstrated raw recursion escape at an actual public loading boundary.

## Non-goals / deferred policy

- no fixed source-depth ceiling;
- no parser replacement;
- no iterative rewrite of the whole normalizer;
- no memory/size/alias-expansion quota policy;
- no schema changes;
- no I-002 digest/canonicalization changes;
- no I-003/I-004+ behavior.

A deterministic explicit resource budget (depth, bytes, aliases) would be a separate security/policy ticket because it intentionally changes what formerly valid sources are accepted.

## Conclusion

F-006 is a narrow exception-boundary repair. The accepted source data model stays unchanged; only an interpreter/parser recursion failure that currently can escape the I-001 public API becomes a stable `SourceValidationError(category="decode_error")` with source provenance preserved.
