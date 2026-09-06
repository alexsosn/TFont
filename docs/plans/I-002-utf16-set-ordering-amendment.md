# I-002 plan amendment: semantic set ordering

**Issue:** #16  
**Parent plan:** `docs/plans/I-002-canonicalization-digest-plan.md`  
**Review trigger:** blocking adversarial review `5123220354` on `c0b3e2f05e0737f12dfdc95aaa0739dff75d2935`.  
**RED:** `132562bf7cb87b95c41400abfb5629f779222d29`, I-002 run `33995433751`.

This amendment is normative for the unreleased v1 digest algorithms and is recorded before the production fix.

## Decision

Every **semantic set-like string or identifier collection** normalized by I-002 uses lexicographic ordering of the string's UTF-16 code units, represented in the Python implementation by `value.encode("utf-16be")`.

This matches the ordering basis used by RFC 8785/JCS for JSON object property names and makes the v1 normalization rule language-neutral for BMP and non-BMP strings.

The rule applies to:

- `semantic_domains`;
- `native_dependencies` and other unique-string semantic sets;
- dependency records sorted by `dependency_id`;
- ontology-lock records sorted by `lock_id`;
- ontology-lock `terms_used`;
- mapping identity records sorted by `mapping_id`;
- review-readiness records sorted by `mapping_id`;
- evidence bindings sorted first by `evidence_id`, then by `content_digest` using the same UTF-16 code-unit comparator.

Candidate projections retain their already-specified ordering by complete JCS canonical bytes.

Source-bundle records retain lexical `logical_path` sorting because I-002 explicitly restricts those paths to portable ASCII; UTF-16 and Unicode code-point ordering are identical for that domain.

## Regression vector

U+E000 and U+1F600 intentionally distinguish Python Unicode code-point order from UTF-16 code-unit order:

- Python code-point order: U+E000, U+1F600;
- v1 UTF-16 code-unit order: U+1F600, U+E000.

The focused regression applies this pair to every semantic string-set/ID normalizer named above.

## Boundary

This change defines deterministic ordering only. It does not validate whether identifiers resolve, whether ontology terms exist, or whether referenced records are semantically compatible. Those remain I-004+ responsibilities.
