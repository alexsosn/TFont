# R-001 / R-005 reconciliation: byte identity versus semantic dependency evidence

**Status:** normative clarification for PR #8  
**Recorded:** 2026-09-05

R-005's reproducible census exposed dense Text-Fabric feature records whose loaded value is `""`/no semantic value. This clarifies, but does not change, R-001's split between exact parent-artifact identity and reusable profile dependency evidence.

## 1. Exact artifact identity hashes bytes, not interpreted semantics

`verified-exact` proves that the loaded parent TF artifact is byte-identical, under the canonical TFont artifact-identity algorithm, to a tested target.

Therefore the exact parent digest includes every regular native `*.tf` file and its exact bytes, including:

- empty dense records;
- comments/metadata present in those feature files;
- values not used by a particular profile;
- formatting/storage details covered by the chosen canonical file-byte manifest.

The digest must **not** normalize away empty records merely because they are semantically “no value”. Exact identity is intentionally stricter than semantic compatibility.

R-005's research `tf_files_sha256` is evidence for this architecture decision; the design ticket may version/refine the digest-manifest algorithm but must preserve deterministic byte-level identity across acquisition transports.

## 2. Dependency compatibility uses semantic assertions, not storage empties

`verified-compatible` answers a different question: does a non-exact parent artifact still satisfy every native dependency required by this profile?

For dependency validation:

- `""`/`None` dense records are not members of a semantic feature domain unless the parent corpus explicitly defines such a literal as meaningful;
- they do not establish that a feature semantically applies to a node type;
- they cannot satisfy a required mapped native value;
- they do not become `Absent`, `Unknown`, `Omitted`, `Unattested`, or another ontology concept automatically;
- diagnostic raw/empty record counts may still be included in compatibility evidence.

Thus a compatibility validator may conclude that two byte-different artifacts are semantically compatible for a profile even if storage-level empty-record layout differs, provided the complete declared semantic dependency closure and invariants still validate.

## 3. Dependency manifests distinguish observation from contract

R-005 also distinguishes `observed_small_domain` from a documented closed categorical vocabulary. R-001 dependency manifests must preserve that distinction.

A profile can depend on:

- one or more explicitly used native values in an open/observed domain;
- the full documented bounded vocabulary, if the mapping semantics genuinely depend on closure;
- a structural/applicability invariant;
- absence/presence semantics only when the parent corpus contract actually defines them.

A finite set of values observed in one release is not automatically a promise that later compatible releases cannot add another value.

Example: the pinned CUC 0.2.8 `emen` artifact empirically exposes non-empty values `excised`, `missing`, `redundant`, `remark`, `restored`. A mapping that uses only `restored` declares that value dependency; it need not reject a later corpus merely because an additional unrelated `emen` state is introduced, unless the profile explicitly depends on the domain being closed.

## 4. TDD consequences for later compatibility implementation

The design/implementation suite should include at least:

1. byte-level parent digest changes when an otherwise irrelevant native TF byte changes;
2. `verified-exact` fails when the byte digest changes;
3. a non-exact artifact can still become `verified-compatible` after complete dependency validation;
4. empty-string/`None` records never satisfy mapped-value dependencies;
5. empty records do not expand semantic `applies_to` node types;
6. an added value to an observed-but-not-declared-closed domain does not automatically invalidate a profile that does not depend on domain closure;
7. removal/reinterpretation of a value actually referenced by the profile does invalidate compatibility;
8. explicit absence/non-attestation dependencies require source-level assertion semantics, not missing/empty storage.

## 5. Review consequence

A final independent reviewer of R-001 should verify that the architecture keeps these proof objects separate:

- **artifact identity:** deterministic evidence about exact parent bytes;
- **dependency evidence:** deterministic evidence that all semantic selectors/values/relations/invariants required by a profile remain valid.

Neither proof can substitute for the other.
