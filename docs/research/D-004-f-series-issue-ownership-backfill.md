# D-004 research — backfill F-series research issue ownership metadata

**Issue:** #104  
**Baseline:** `main` `6934649ae64c1df60032240d1a82a350c509e77a`  
**Type:** repository metadata / F-021 prerequisite

## Question

Which accepted `docs/research/F-NNN-*.md` artifacts on current `main` still lack the machine-readable `**Issue:** #N` ownership header required by F-021's proposed current-tree feature-ID uniqueness invariant, and can those owners be backfilled without changing research conclusions or introducing a hand-maintained registry?

## Prior evidence

F-021 research PR #100 independently re-audited the repository after its first review was challenged. Its accepted review recorded that F-001 through F-011 and F-013 already had explicit issue ownership, while four accepted primary feature research documents were headerless at that point:

- F-012 -> #80;
- F-014 -> #84;
- F-016 -> #88;
- F-017 -> #91.

That review also verified those four mappings from GitHub rather than inferring them from filenames.

However, F-021's accepted post-migration invariant is broader than one primary file per feature: **every** `docs/research/F-NNN-*.md` must carry exactly one explicit owner, and multiple research/evidence/amendment files for the same F ID are legal only when they declare the same issue. D-004 therefore has to re-audit the complete current F-series research namespace, including supporting evidence added after the F-021 inventory.

## Current-tree audit

### Headerless artifacts on current main

Five current F-series research artifacts have no `**Issue:**` header:

1. `docs/research/F-012-file-hash-object-binding.md`
2. `docs/research/F-014-windows-exact-file-paths.md`
3. `docs/research/F-016-custom-schema-recursion-boundary.md`
4. `docs/research/F-017-inplace-file-mutation.md`
5. `docs/research/F-019-cpython-path-conversion-evidence.md`

The fifth file is current-tree drift relative to the older F-021 inventory. It was added as supporting evidence under F-019 after that inventory and must carry the same owner as the primary F-019 research for F-021's accepted every-artifact invariant to pass.

### Authoritative ownership

The owners are recoverable from merged/reviewed GitHub history and current explicitly owned companion research:

- F-012 implementation PR #82 closes issue #80;
- F-014 implementation PR #85 closes issue #84;
- F-016 accepted research/implementation is issue #88 (research PR #89; implementation PR #107 closes #88);
- F-017 research-decision PR #92 closes issue #91;
- primary `F-019-invalid-source-filesystem-paths.md` explicitly declares `**Issue:** #94`, and its CPython note states that it is follow-up evidence for that F-019 boundary.

The mappings therefore do not depend on sequential feature numbering, branch names, or issue ordering.

### Explicitly owned neighboring/current artifacts

The independently reviewed F-021 inventory already established explicit ownership for F-001..F-011 and F-013. Current post-inventory primary research was checked directly:

- F-015 declares `**Issue:** #87`;
- F-018 declares `**Issue:** #90`;
- F-019 primary declares `**Issue:** #94`;
- F-020 declares `**Issue:** #95`;
- F-021 declares `**Issue:** #99`;
- F-022 declares `**Issue:** #103`.

The current directory contains no other same-ID F-series evidence/amendment file beyond the F-019 CPython note identified above. The complete migration set on this baseline is therefore five files.

## Decision

D-004 should perform a five-file metadata-only migration:

| Feature | Research artifact | Authoritative owner |
| --- | --- | --- |
| F-012 | `F-012-file-hash-object-binding.md` | `#80` |
| F-014 | `F-014-windows-exact-file-paths.md` | `#84` |
| F-016 | `F-016-custom-schema-recursion-boundary.md` | `#88` |
| F-017 | `F-017-inplace-file-mutation.md` | `#91` |
| F-019 | `F-019-cpython-path-conversion-evidence.md` | `#94` |

For each artifact, insert only the canonical ownership line immediately below the title, with normal Markdown spacing:

```markdown
**Issue:** #N
```

F-019's evidence note does not allocate another feature or another issue. The backfill simply makes its already-shared F-019 ownership explicit, as required by F-021's same-ID consistency rule.

Do not rewrite titles, prose, conclusions, historical baseline SHAs, citations, feature identifiers, or filenames.

## Why a direct metadata backfill is sufficient

F-021's accepted v1 invariant is current-tree based. Once every current F-series research artifact has an explicit issue owner, a future checker can require ownership metadata, permit same-ID artifacts with one consistent owner, and reject one F identifier mapping to multiple issue numbers without maintaining a permanent legacy allowlist.

D-004 does not make owner headers immutable. A pure current-tree check cannot detect a branch that edits the sole historical owner header in place without a prior-state authority; F-021 research explicitly excludes that guarantee. This migration establishes complete current-tree metadata, not historical tamper detection.

## RED contract

Before editing the five research artifacts, add a repository-state migration test that scans **all** `docs/research/F-[0-9][0-9][0-9]-*.md` files and demonstrates the present ownership gap.

The RED should prove at least:

1. current F-series research ownership is incomplete;
2. the exact missing artifact set on the reviewed baseline is the five files listed above;
3. no currently explicit F ID maps to multiple issue numbers;
4. the expected backfill mappings are explicit migration expectations, not inferred by sequential numbering;
5. multiple files sharing one F ID are allowed only when their declared owners agree;
6. after GREEN every scanned F-series research/evidence/amendment artifact has exactly one well-formed owner declaration.

The test may be D-004-specific rather than the eventual reusable F-021 checker. It should fail on the tests-only RED head because those five existing files lack headers. After GREEN it should verify the five inserted values exactly and verify complete current-tree ownership.

## Scope and implementation gate

Research must be independently reviewed before a plan. The plan should then freeze:

- enumeration of every `docs/research/F-NNN-*.md` artifact;
- exact parsing of one `**Issue:** #N` declaration from a bounded header region;
- same-F-ID/same-owner consistency;
- tests-only RED evidence before metadata edits;
- five-file-only metadata GREEN;
- focused documentation/repository-state CI plus authoritative full suite;
- exact-head independent review of all five mappings and absence of prose drift.

No runtime, schema, digest, ontology, semantic-validator, packaging behavior, dependency, or public Python API is in scope.

## Non-goals

- no F-021 uniqueness checker implementation;
- no permanent feature registry or allowlist;
- no GitHub API dependency in normal CI;
- no automatic ticket renumbering;
- no historical rewrite or filename normalization;
- no owner-header immutability claim;
- no ownership changes for already correctly annotated artifacts.

## Exit condition

D-004 is research-complete when independent review confirms that the current migration set is exactly F-012/#80, F-014/#84, F-016/#88, F-017/#91, and the F-019 CPython evidence note/#94; that all other current F-series research artifacts already declare ownership; and that a five-file metadata-only RED/GREEN migration is sufficient to unblock F-021's accepted current-tree invariant.
