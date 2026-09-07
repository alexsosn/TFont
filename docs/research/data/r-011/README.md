# R-011 research fixture

This directory contains non-production ontology-mapped pilot data for R-011.

- `pilots.json` is the reviewed representative mapping/query fixture.
- It intentionally uses compact research target identifiers; R-013/P-003 own final formal kinds, roles, and production IRIs.
- `native-only`, `unsupported`, and `ambiguous` are first-class results, not missing data.
- Approximate mapping rows may demonstrate query-plan compilability, but R-016 owns whether production approximate execution is allowed.

Reproduce measurements from repository root with:

```bash
python scripts/research/r011_measure.py
pytest tests/research/test_r011_measure.py
```
