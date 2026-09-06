# F-006 plan: normalize deep source recursion failures

**Issue:** #32  
**Research:** `docs/research/F-006-deep-source-nesting.md` at `00c41f5c1159cd95dc6af228ffd5845f70181f60`

## Scope

Repair the I-001 public source-loading boundary so excessive nesting cannot leak raw `RecursionError` from JSON parsing, YAML parsing, or plain-model normalization.

No schema, canonicalization, digest, or semantic behavior changes.

## Public contract

For a recursion/depth failure encountered while loading serialized source:

- exception type: `SourceValidationError`;
- `problem.category`: `decode_error`;
- `problem.source_name`: the caller/path-owned source name;
- `instance_path` and `schema_path`: unchanged defaults `()`.

Existing error precedence remains unchanged:

- duplicate keys -> `duplicate_key`;
- unsupported parsed values / non-string keys / non-finite YAML -> `non_json_value`;
- invalid JSON numeric constants -> `decode_error`;
- schema validation is untouched.

## Implementation design

### Parser boundaries

JSON:

- keep `_JSONDuplicateKey` as the first dedicated handler;
- add `RecursionError` to the generic parser/decode failure boundary;
- preserve current JSON decode/value handling.

YAML:

- add `RecursionError` to the parser failure boundary alongside `YAMLError`;
- do not configure a new `YAML.max_depth` limit in this ticket.

### Plain-model boundary

Add a private helper:

```python
def _normalize_loaded(value: Any, *, source_name: str) -> JSONValue:
    try:
        return _plain_json(value, source_name=source_name)
    except RecursionError as exc:
        _raise("decode_error", str(exc), source_name)
```

Both JSON and YAML branches call this helper after successful parse.

Do not include `_plain_json()` inside a `try` that catches `ValueError`: `SourceValidationError` is a `ValueError` subclass and must retain its existing category.

## RED tests

Create `tests/i001/test_deep_source_nesting.py` before production changes.

Fixtures:

- JSON: nested arrays at a depth greater than `sys.getrecursionlimit()`;
- YAML: nested block sequences at a depth greater than `sys.getrecursionlimit()`;
- a moderate nested value (e.g. depth 32) for successful JSON/YAML controls.

The deep tests assert only the public contract (`SourceValidationError`, `decode_error`, source name), not exact runtime prose.

For YAML, if the parser already reports a `YAMLError` at the chosen depth and current production therefore already satisfies the public contract, record that as an already-green parser control. At least one deep public input must demonstrate the current raw `RecursionError` escape for the RED gate; JSON/plain normalization is expected to do so.

Regression controls in the same test module:

- duplicate JSON key remains `duplicate_key`;
- duplicate YAML key remains `duplicate_key`;
- YAML `.nan` remains `non_json_value`;
- JSON `NaN` remains `decode_error`.

## CI

Add `.github/workflows/f006-deep-source-nesting.yml` before production repair.

Matrix: Python 3.10 and 3.12.

Steps:

1. checkout exact head;
2. install package;
3. run `tests.i001.test_deep_source_nesting`;
4. run full `tests.i001` discovery;
5. run full repository discovery.

RED head must fail in the focused F-006 step for the expected raw-recursion contract mismatch.

GREEN head must pass all matrix jobs and all three test levels.

## Non-goals

- fixed nesting/resource quotas;
- memory/byte/alias limits;
- iterative normalizer rewrite;
- parser replacement;
- schema changes;
- source-value normalization beyond existing `_plain_json` behavior;
- I-002/I-003/I-004+ changes.

## Review gate

After exact-head GREEN, open a PR and require a fresh logically-independent adversarial review of the exact head. The authoring context does not count. Any material head change restarts CI and review.
