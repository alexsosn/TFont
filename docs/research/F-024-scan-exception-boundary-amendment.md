# F-024 research amendment — scan exception boundary

**Issue:** #121

## Reason for amendment

Independent review of the initial F-024 research found that it described namespace/enumeration/classification failures mainly as `OSError`, while the repository checker already treats `ValueError` as part of stable filesystem/path failure handling for content reads.

The scan boundary needs an explicit exception contract before planning.

## Amended contract

Filesystem namespace discovery and entry classification must catch exactly:

```python
(OSError, ValueError)
```

and report:

```text
scan_error: <repository-relative-path>: <ExceptionType>
```

Rationale:

- `OSError` covers permission, inaccessible-directory, stat/classification, and ordinary filesystem failures;
- `ValueError` covers invalid path representations reaching filesystem enumeration/classification APIs, including cases such as embedded NUL path components;
- exception messages remain excluded because they may contain platform-dependent details;
- `UnicodeError` remains part of the **content** `read_error` boundary, not the namespace-scan boundary;
- no broad `except Exception` is permitted.

## RED implication

At least one tests-only RED case must inject `ValueError` at an enumeration/classification seam and require the same stable `scan_error` shape as the corresponding `OSError` case.

The RED suite does not need to create a literal embedded-NUL repository path; deterministic injection is preferred so Python/OS differences cannot change the expected failure mechanism.

## Scope

All other conclusions in `F-024-ownership-namespace-scan-failures.md` remain unchanged, including:

- research scan failures are global authority failures;
- downstream scan failures are local;
- explicit one-level enumeration replaces `glob()` where complete failure visibility matters;
- existing public checker call shapes remain compatible;
- symlink policy stays out of scope.
