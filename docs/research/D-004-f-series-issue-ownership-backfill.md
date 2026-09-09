# D-004 research — backfill F-series research issue ownership metadata

**Issue:** #104  
**Baseline:** `main` `6934649ae64c1df60032240d1a82a350c509e77a`  
**Type:** repository metadata / F-021 prerequisite

## Question

Which accepted F-series primary research documents on current `main` still lack the machine-readable `**Issue:** #N` ownership header required by F-021's proposed current-tree feature-ID uniqueness invariant, and can those owners be backfilled without changing research conclusions or introducing a hand-maintained registry?

## Prior evidence

F-021 research PR #100 independently re-audited the repository after its first review was challenged. Its accepted review records that F-001 through F-011 and F-013 already have explicit issue ownership, while exactly four accepted primary feature research documents were headerless at that point:

- F-012 -> #80;
- F-014 -> #84;
- F-016 -> #88;
- F-017 -> #91.

That review also verified the issue mappings from GitHub rather than inferring them from filenames.

D-004 must nevertheless recheck current `main` because F-015 and F-018 through F-022 were added after or around that inventory and could have introduced new headerless primary research.

## Current-tree audit

### Confirmed legacy omissions

The following current files still have no `**Issue:**` header:

1. `docs/research/F-012-file-hash-object-binding.md`
2. `docs/research/F-014-windows-exact-file-paths.md`
3. `docs/research/F-016-custom-schema-recursion-boundary.md`
4. `docs/research/F-017-inplace-file-mutation.md`

Their authoritative issue ownership is independently recoverable from merged/reviewed GitHub history:

- F-012 implementation PR #82 closes issue #80;
- F-014 implementation PR #85 closes issue #84;
- F-016 accepted research/implementation is issue #88 (research PR #89; implementation PR #107 closes #88);
- F-017 research-decision PR #92 closes issue #91.

The mappings therefore do not depend on guesswork from feature numbers, branch names, or issue ordering.

### Post-F-021 additions / neighboring current owners

Current primary research added after the earlier inventory was sampled directly from `main`:

- F-015 declares `**Issue:** #87`;
- F-018 declares `**Issue:** #90`;
- F-019 declares `**Issue:** #94`;
- F-020 declares `**Issue:** #95`;
- F-021 declares `**Issue:** #99`;
- F-022 declares `**Issue:** #103`.

Combined with the independent F-021 re-audit of F-001..F-011 and F-013, this leaves exactly the same four current primary F-series research omissions. No fifth migration target was found.

F-019's separate CPython evidence document is supporting evidence under the same ticket, not a new feature allocation. F-021 explicitly permits multiple same-ID research/evidence/amendment artifacts when their authoritative owner agrees; D-004 should not invent a second owner for supporting material.

## Decision

D-004 should perform a four-file metadata-only migration:

| Feature | Research file | Authoritative owner |
| --- | --- | --- |
| F-012 | `F-012-file-hash-object-binding.md` | `#80` |
| F-014 | `F-014-windows-exact-file-paths.md` | `#84` |
| F-016 | `F-016-custom-schema-recursion-boundary.md` | `#88` |
| F-017 | `F-017-inplace-file-mutation.md` | `#91` |

For each file, insert only the canonical ownership line immediately below the title (with normal Markdown spacing):

```markdown
**Issue:** #N
```

Do not rewrite titles, prose, conclusions, historical baseline SHAs, citations, feature identifiers, or filenames.

## Why a direct metadata backfill is sufficient

F-021's accepted v1 invariant is current-tree based. Once every accepted primary F-series research allocation has an explicit issue owner, a future checker can require ownership metadata and reject one F identifier mapping to multiple issue numbers without maintaining a permanent legacy allowlist.

D-004 does not make owner headers immutable. A pure current-tree check cannot detect a branch that edits the sole historical owner header in place without a prior-state authority; F-021 research explicitly excludes that guarantee. This migration therefore establishes complete current-tree metadata, not historical tamper detection.

## RED contract

Before editing the four research files, add a repository-state test which scans primary `docs/research/F-*.md` feature research and demonstrates the present migration gap.

The RED should prove at least:

1. current primary F-series research ownership is incomplete;
2. the missing set is exactly `F-012`, `F-014`, `F-016`, `F-017` on the reviewed baseline;
3. no current explicitly owned feature maps to multiple issue numbers;
4. the four expected mappings are represented in the test as migration expectations, not inferred by sequential numbering;
5. supporting same-feature evidence such as F-019's CPython note does not create a second allocation requirement.

The test may be a D-004-specific migration test rather than the eventual F-021 enforcement implementation. It should fail only because those four primary files lack headers. After GREEN, it should require every current primary F-series allocation to expose one machine-readable owner and verify the four backfilled values exactly.

## Scope and implementation gate

Research must be independently reviewed before a plan. The plan should then freeze:

- how primary allocation documents are distinguished from supporting evidence/amendments for this migration test;
- exact parsing of the `**Issue:** #N` line;
- RED evidence before metadata edits;
- four-file-only GREEN;
- focused documentation/repository-state CI plus authoritative full suite;
- exact-head independent review of both mappings and absence of prose drift.

No runtime, schema, digest, ontology, semantic validator, packaging behavior, dependency, or public Python API is in scope.

## Non-goals

- no F-021 uniqueness checker implementation;
- no permanent feature registry or allowlist;
- no GitHub API dependency in normal CI;
- no automatic ticket renumbering;
- no historical rewrite or filename normalization;
- no owner-header immutability claim;
- no changes to supporting research/evidence documents unless a later F-021 plan explicitly requires same-owner annotation there.

## Exit condition

D-004 is research-complete when independent review confirms that the current migration set is exactly F-012/#80, F-014/#84, F-016/#88, and F-017/#91, that newer F-series primaries are already owned, and that a four-file metadata-only RED/GREEN migration is sufficient to unblock F-021's accepted current-tree invariant.
