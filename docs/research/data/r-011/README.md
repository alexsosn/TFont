# R-011 research fixture

This directory contains the non-production ontology-mapped pilot package for R-011.

- `pilots.json` is the source representative mapping/query fixture.
- `mapping-overrides.json` contains machine-readable corrections discovered by fresh adversarial review; all measurements apply these overrides first.
- `raw-schema-policy.json` defines the raw native-schema denominator, including reviewed bounded-value expansions and explicit denominator-quality labels.
- `query-suite.json` extends the source fixture to the complete R-011 query suite and records fail-closed native probes.
- Compact ontology target identifiers are research identifiers; R-013/P-003 own final formal kinds, roles, and production IRIs.
- `native-only`, `unsupported`, and `ambiguous` are first-class reviewed outcomes, not missing data.
- Raw items not yet reviewed remain `unreviewed`; they are not silently reclassified as `native-only`.
- Approximate mappings may demonstrate native-plan compilability, but R-016 owns whether production approximate execution is allowed.

The effective fixture is therefore:

```text
pilots.json
  + mapping-overrides.json
  + raw-schema-policy.json
  + query-suite.json
  -> r011_measure.py
```

Reproduce measurements from repository root with:

```bash
python scripts/research/r011_measure.py
pytest tests/research/test_r011_measure.py
```

The dedicated pull-request workflow `.github/workflows/r011-report-validation.yml` runs both commands as the exact-head validation gate.
