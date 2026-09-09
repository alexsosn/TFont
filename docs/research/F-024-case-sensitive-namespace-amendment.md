# F-024 research amendment — case-sensitive ownership namespaces

**Issue:** #121

## Review finding

The initial F-024 plan proposes replacing one-level `Path.glob()` discovery with explicit `iterdir()` plus lexical F-series matching so scan failures cannot be silently suppressed.

Independent plan review found a cross-platform semantic detail that must be decided at research level first.

Python `Path.glob()` normally follows platform filename-case rules. On Windows this is typically case-insensitive, while the accepted F-021/F-023 ownership namespace is defined by exact case-sensitive regular expressions such as:

- research/plan: `F-NNN-*.md`;
- workflow: `fNNN-*.yml|yaml`;
- test package: `fNNN`.

The current research/plan discovery code can therefore discover a differently-cased path on Windows even though later regex-based ownership parsing does not accept that path as an F-series artifact. That is an implementation artifact, not an intended allocation rule.

## Amended semantic contract

F-024 must preserve the **accepted F-023 namespace semantics**, not platform-specific `Path.glob()` case matching.

After GREEN:

- ownership namespace membership is decided lexically and case-sensitively by the existing F-series filename/name regexes;
- lowercase/uppercase near-misses outside those exact forms are unrelated entries;
- unrelated case variants are filtered before filesystem entry classification for ownership purposes;
- behavior is identical on POSIX and Windows regardless of host filesystem case rules.

Examples outside the research/plan namespace:

- `docs/research/f-024-example.md`;
- `docs/research/f-024-example.MD`;
- `docs/plans/f-024-plan.md`.

Examples outside the workflow namespace:

- `.github/workflows/F024-example.yml`;
- `.github/workflows/f024-example.YML`.

Examples outside the test-package namespace:

- `tests/F024`;
- `tests/f24`.

This does not allocate new names and does not broaden F-024 into general filename normalization. It makes the previously accepted regular-expression namespace authoritative across platforms.

## RED implication

Add stable controls proving at least:

1. a differently-cased research near-miss is ignored as unrelated when a valid research authority artifact is also present;
2. a differently-cased plan/workflow/test near-miss is ignored and is not filesystem-classified for ownership;
3. these controls do not depend on host filesystem case sensitivity because the tests exercise lexical matching directly through temporary paths/mocked classification seams.

The focused implementation can remain Ubuntu Python 3.10/3.12 because the case contract is implemented and tested lexically rather than by relying on Windows filesystem behavior.

## Effect on previous research

All previous F-024 conclusions remain in force:

- `(OSError, ValueError)` scan boundary;
- `scan_error` diagnostics;
- research scan failure global, downstream scan failure local;
- explicit one-level enumeration;
- public checker compatibility;
- symlink policy out of scope.
