# F-001: source diagnostic provenance plan

**Issue:** #18  
**Depends on:** merged I-001 (`f7d358fe7e90680b6216ed6cb4b6f624dd2bcdd2`)  
**Scope:** preserve user-source identity in structural validation diagnostics

## API change

Extend:

```python
validate_source(data, schema_name, *, schema_root=None, source_name=None)
```

Behavior:

- when `source_name is None`, instance-validation errors keep the current default identity `schema_name`;
- when supplied, `source_name` is converted to `str` by the caller boundary and used only for `schema_validation` problems;
- schema loading/meta-validation errors continue to name the concrete schema file path and ignore the user-source identity.

`load_and_validate(path, schema_name, ...)` computes one `source_path = Path(path)`, loads from that path, then calls:

```python
validate_source(
    data,
    schema_name,
    schema_root=schema_root,
    source_name=str(source_path),
)
```

No return type or exception type changes.

## TDD sequence

### RED

Add `tests/i001/test_source_diagnostic_provenance.py` with a file-backed invalid profile fixture:

- write valid JSON whose `schema_version` has the wrong type;
- call `load_and_validate(path, "profile", schema_root=SCHEMA_ROOT)`;
- assert `schema_validation`;
- assert `problem.source_name == str(path)`;
- assert `schema_version` remains in `instance_path` and `schema_path` remains non-empty.

On merged I-001 this must fail only on `problem.source_name` (`"profile" != <path>`).

Controls in the same test module:

1. direct `validate_source()` failure keeps `source_name == "profile"`;
2. invalid custom schema continues to name the schema file path;
3. malformed file decode/parse error continues to name the source path.

### GREEN

Add the optional keyword-only `source_name` to `validate_source()`. Resolve the instance identity once near the start of validation:

```python
instance_source_name = schema_name if source_name is None else source_name
```

Use it only in the final `schema_validation` `ValidationProblem`.

Update `load_and_validate()` to pass `str(Path(path))`.

No changes to `_raise`, loader parsing, schemas, dependency versions or exports are required.

## Invariants

- `SourceValidationError` remains the sole public error type.
- Existing stable categories remain unchanged.
- In-memory callers remain source-compatible.
- Parse/decode diagnostics remain file-aware.
- Invalid-schema diagnostics remain schema-file-aware.
- Instance/schema paths and messages remain library-derived as before.
- No semantic validation or I-002 functionality is introduced.

## Test gates

1. RED exact head: focused I-001 suite fails only on the new file-backed provenance assertion; full suite has no unrelated regressions.
2. GREEN exact head: focused I-001 suite green.
3. Full repository `unittest` suite green.
4. PR CI green on the exact final head.
5. Fresh logically-independent adversarial review checks API compatibility, diagnostic ownership separation, path fidelity and scope containment.

## Review attack surface

The reviewer should specifically try to falsify:

- direct `validate_source()` compatibility;
- schema errors accidentally being relabeled with the user file;
- path normalization changing caller-visible identity;
- regressions to `instance_path`/`schema_path`;
- accidental dependence on I-002 branch code;
- over-generalization into semantic validation.