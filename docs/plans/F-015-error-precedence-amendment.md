# F-015 plan amendment — preserve schema-authority error precedence

## Trigger

Implementation self-audit after the first minimal GREEN patch found an unintended diagnostic-order change.

Before F-015, `validate_source()` resolves, reads, parses and self-validates the selected schema before instance validation. Therefore a broken custom schema is reported as `invalid_schema` even if the supplied instance is also malformed.

The first F-015 implementation placed `_plain_json(data, ...)` immediately after schema-name resolution. That satisfies the direct-source boundary but makes instance `decode_error` / `non_json_value` preempt an invalid custom schema. This is unnecessary scope drift and weakens the established distinction between schema authority and instance authority.

## Corrected ordering

Preserve existing schema authority precedence:

1. resolve known schema name;
2. read/decode/parse schema;
3. verify Draft 2020-12 declaration;
4. `Draft202012Validator.check_schema(schema)`;
5. compute effective instance source name and `_plain_json()` preflight the direct instance;
6. construct validator / call `iter_errors(normalized_data)`.

Thus direct values still cannot reach JSON Schema instance validation unchecked, while broken schemas keep the historical `invalid_schema` precedence.

## TDD amendment

Before moving production preflight, add a regression with:
- a custom evidence schema whose `type` keyword is structurally invalid (`42`);
- direct evidence data containing a recursive/non-JSON value that would independently fail F-015 preflight.

Expected result: `invalid_schema`, with the custom schema file as `problem.source_name`.

The first F-015 implementation must fail this new test by returning `non_json_value`; only then move the preflight below successful `check_schema()`.

## Non-changes

No change to:
- depth 128/129 boundary;
- aliases/non-finite/key/value diagnostics once the schema is valid;
- unknown-schema precedence;
- F-016 schema-recursion work;
- schemas or public API.