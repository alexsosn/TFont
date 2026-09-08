# F-016 research — custom schema recursion boundary

**Issue:** #88  
**Baseline:** `main` `11eabc3dd26e6c5a83a2e1ebbca85eb13b4a56ca`

## Question

How should `validate_source(..., schema_root=...)` fail when caller-supplied schema JSON is deeply nested or causes recursive JSON Schema meta-validation, without leaking interpreter-dependent `RecursionError` or misclassifying schema failures as source failures?

## Current boundary

`_read_schema_bytes()` reads the selected custom schema file. `validate_source()` then:

1. decodes UTF-8;
2. calls `json.loads()`;
3. checks the declared Draft 2020-12 marker;
4. calls `Draft202012Validator.check_schema(schema)`;
5. validates the source instance.

Decode/JSON syntax problems and `SchemaError` are translated to `SourceValidationError(category="invalid_schema")`, but `RecursionError` is not translated at either the schema JSON parser or `check_schema()` boundary.

F-015 intentionally does not catch those errors because source-instance admissibility and schema-authority admissibility are separate contracts.

## External evidence

Python documents its recursion limit as protection for the interpreter/C stack and states that the highest safe limit is platform-dependent. Raising it is therefore not a portable validation policy:
https://docs.python.org/3/library/sys.html#sys.setrecursionlimit

`jsonschema` 4.26 documents `Draft202012Validator.check_schema(schema)` as validation of a schema against the validator meta-schema. `iter_errors()` recursively yields validation failures through validator descent:
https://python-jsonschema.readthedocs.io/en/stable/

Upstream issue #847 records a real raw `RecursionError` escaping validator/meta-schema traversal:
https://github.com/python-jsonschema/jsonschema/issues/847

The JSON Schema core specification also warns that implementations must guard against infinite recursion and describes behavior for infinitely recursive schema nesting as undefined:
https://github.com/json-schema-org/json-schema-spec/blob/main/specs/jsonschema-core.md

## Decision: deterministic schema-source nesting boundary

Do not make acceptance depend on Python's current recursion limit and do not merely wrap arbitrary `RecursionError` after it occurs.

Custom schema source should be preflighted as JSON before `check_schema()` with a deterministic maximum container nesting depth. For the first contract, use the existing TFont value `MAX_SOURCE_NESTING = 128` unless RED research demonstrates that canonical Draft 2020-12 schema constructs require a different ceiling. There is no evidence that TFont's compact source schemas approach this depth, and sharing the numeric ceiling minimizes separate implementation-defined resource domains.

This is numeric-policy reuse only; source and schema diagnostics remain distinct.

Schema preflight must:
- require JSON-compatible plain values;
- reject recursive aliases if a programmatic schema representation is ever introduced later;
- reject depth >128 before `Draft202012Validator.check_schema()`;
- preserve custom schema file identity in the diagnostic;
- classify every preflight/schema recursion failure as `invalid_schema`, never `decode_error` / `non_json_value` from the instance contract.

## Error contract

For custom schema files:
- UTF-8/JSON syntax failure: existing `invalid_schema`;
- schema-source nesting >128: `invalid_schema`, message names the schema nesting ceiling;
- `check_schema()` `SchemaError`: existing `invalid_schema` with existing paths;
- a narrow residual `RecursionError` from `check_schema()` after bounded schema preflight: translate to `invalid_schema` with a stable message such as `schema validation recursion failure`.

The residual catch is still useful because `$ref`/applicator evaluation can recurse independently of physical JSON container depth. It must surround only schema self-validation, not source-instance validation, so authority is not misreported.

## Packaged vs custom schemas

Packaged TFont schemas are trusted shipped resources but should execute through the same schema parsing/self-validation path. Tests must pin that every canonical schema still self-validates and ordinary source validation is unchanged.

Do not silently exempt packaged schemas from correctness checks merely for performance. Caching validated packaged schemas would be a separate performance ticket if later justified.

## RED strategy

A plan may proceed with deterministic tests only after this research lands.

Required RED categories:
1. custom Draft 2020-12 schema nested to exactly 128 containers remains admissible if otherwise valid;
2. equivalent schema at 129 containers must yield `invalid_schema`, not raw `RecursionError` / interpreter-dependent behavior;
3. deep schema JSON that makes `json.loads()` recurse must also be normalized to `invalid_schema` if it crosses before post-parse preflight;
4. inject `RecursionError` from `Draft202012Validator.check_schema()` and require stable `invalid_schema` translation;
5. ordinary invalid schema still preserves `SchemaError` paths/message authority;
6. canonical packaged schemas and shallow custom schemas remain unchanged;
7. F-015 direct-instance depth diagnostics remain instance-side and unchanged.

A synthetic schema should place inert nested metadata under a legal extension/annotation location where possible, so the depth test measures source shape rather than complex recursive `$ref` semantics.

## Implementation shape for later plan

Likely minimal implementation:
- one private schema JSON preflight helper with explicit `invalid_schema` errors and depth accounting;
- narrow `except RecursionError` around custom schema JSON parse where the parser fails before preflight;
- narrow `except RecursionError` around `Draft202012Validator.check_schema(schema)`;
- no catch around ordinary `validator.iter_errors(instance)` in this ticket.

Do not reuse `_plain_json()` directly if doing so would expose source categories. Structural traversal logic may be factored into a category-parameterized private helper only if tests prove source error behavior remains byte-for-byte stable.

## Non-goals

- no JSON Schema draft/version change;
- no schema semantic redesign;
- no change to I-004 semantic validation;
- no F-015 source-instance policy change;
- no global Python recursion-limit mutation;
- no broad `except Exception`;
- no attempt to make intentionally infinitely recursive schemas executable.

## Conclusion

F-016 is implementable. TFont should give custom schema source a deterministic nesting boundary before meta-schema validation and retain a narrow `invalid_schema` recursion translation for residual schema-side recursion. The future plan must keep schema authority and source-instance authority diagnostically separate.