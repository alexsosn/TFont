# F-016 plan — deterministic custom-schema recursion boundary

**Issue:** #88  
**Research:** `docs/research/F-016-custom-schema-recursion-boundary.md`

## Integration precondition

F-016 overlaps `src/tfont/source_validation.py` with F-015. Do not start RED or production from this research branch. First let F-015 merge, then create/rebuild the implementation branch from that exact current `main` and preserve F-015's instance preflight/error precedence.

## Public contract

Custom and packaged schema files remain JSON Schema Draft 2020-12 resources. No schema semantics or public function signatures change.

Schema-authority failures use `SourceValidationError(category="invalid_schema")` and name the schema resource/file, never the instance source.

Set `MAX_SCHEMA_NESTING = 128` as an explicit version-1 resource boundary independent in meaning from `MAX_SOURCE_NESTING`, even though both initially equal 128. Separate constants prevent a later source-policy change from silently changing schema admissibility.

Container accounting matches the source convention: root object/list is depth 1; depth 128 accepted; 129 rejected.

## Production design

In `src/tfont/source_validation.py` after F-015 is merged:

1. add `MAX_SCHEMA_NESTING = 128`;
2. add a private schema-JSON nesting checker whose errors are always `invalid_schema` and whose traversal cannot itself leak raw recursion for values near the boundary;
3. around schema `json.loads(...)`, translate a narrow `RecursionError` to `invalid_schema` with the schema resource identity;
4. after parsing and before Draft declaration/self-validation, enforce schema nesting <=128;
5. retain the existing Draft 2020-12 declaration check;
6. around `Draft202012Validator.check_schema(schema)`, retain existing `SchemaError` handling and add a narrow `RecursionError -> invalid_schema` translation;
7. do not catch `RecursionError` around instance `validator.iter_errors()` in F-016.

Prefer an iterative schema nesting walk over a recursive helper so the error boundary itself is independent of interpreter recursion. Parsed JSON already guarantees key/string/basic JSON shape; the helper's job is resource-depth accounting, not a second JSON parser.

## Error messages

Pin stable messages:
- over-depth: `schema nesting exceeds maximum depth 128`;
- parser recursion before post-parse preflight: same over-depth message, because the schema source exceeded the safely parseable recursive representation before TFont could count it;
- residual `check_schema()` recursion: `schema validation recursion failure`.

All use `invalid_schema` and `schema_source_name`.

## RED tests

Add `tests/f016/test_custom_schema_recursion_boundary.py` before production edits on the post-F-015 branch.

Required cases:
1. custom schema with an unknown extension keyword containing nested objects and total container depth exactly 128 self-validates and can validate a shallow instance;
2. same shape at depth 129 -> `invalid_schema`, schema path identity preserved;
3. very deep schema JSON that drives `json.loads()` to `RecursionError` -> stable `invalid_schema` rather than raw recursion;
4. injected `Draft202012Validator.check_schema()` `RecursionError` -> stable `invalid_schema`;
5. ordinary invalid schema still returns existing `SchemaError` message/path fields;
6. all packaged schemas still self-validate and validate their minimal fixtures;
7. F-015 direct instance depth 128/129 and non-JSON diagnostics remain unchanged.

The 128/129 fixture should use an unknown `x-tfont-depth-probe` keyword so the test measures physical schema-source nesting rather than `$ref` recursion semantics.

## CI

Add `.github/workflows/f016-custom-schema-recursion-boundary.yml`:
- exact-head checkout;
- checkout@v5/setup-python@v6;
- Python 3.10/3.12;
- editable install + `build`;
- focused `tests/f016`;
- focused `tests/f015`;
- `tests/i001` schema/validator regressions;
- no duplicate generic full-suite command; authoritative `full-suite.yml` remains sole owner.

## GREEN / review gate

Before PR finalization:
- focused matrix GREEN on 3.10/3.12;
- central full suite GREEN;
- compare against current main contains only F-016-owned files plus the minimal source-validation delta;
- fresh logically-independent adversarial review attacks depth accounting, `json.loads` vs `check_schema` classification, invalid-schema provenance, SchemaError path preservation, unknown-keyword fixture validity, F-015 precedence, and over-broad exception catching.

Any material head change invalidates the final review.