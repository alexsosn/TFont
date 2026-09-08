# F-021 research — detect duplicate F-series ticket identifiers before merge

**Issue:** #99  
**Baseline:** `main` `200dcaba593d02d4d903aa424d6c7fec574f2ff2`  
**Type:** repository ergonomics / agentic-loop collision prevention

## Question

Can TFont mechanically prevent two distinct feature tickets from claiming the same `F-NNN` namespace without adding a manually maintained feature registry or a network-dependent GitHub lookup to ordinary CI?

## Trigger

Two independent active lanes were assigned `F-015`:

- #87 — direct source-validation boundary;
- #90 — file-object identity hardening, later renumbered to F-018.

Before the collision was noticed, the second lane had accumulated research, plan, workflow and `tests/f015/**` artifacts. Once both lines are integrated, those names are not cosmetic: they collide in test packages, workflow families, documentation identity and review traceability.

The failure mode is therefore suitable for a repository invariant.

## Current F-series inventory

Current `main` contains one primary research file for each of:

`F-001` through `F-014`, then `F-016` and `F-017`.

`F-015` is intentionally absent from this baseline because #87 is still in final review at the time of this research.

The repository also contains corresponding plans/workflows/tests for many, but not all, feature IDs. Research-only conclusions such as F-013 and F-017 correctly have no implementation workflow/test family. Therefore workflow/test presence cannot be the authority for allocating an ID.

### Explicit issue metadata

The earlier feature research files consistently declare an owner near the top:

- F-001 -> #18;
- F-002 -> #21;
- F-003 -> #26;
- F-004 -> #28;
- F-005 -> #30;
- F-006 -> #32;
- F-007 -> #34;
- F-008 -> #66;
- F-009 -> #69;
- F-010 -> #71;
- F-011 -> #78.

F-013 also declares `**Issue:** #81`.

Later filesystem/schema research is not perfectly uniform. At least F-012, F-014, F-016 and F-017 do not carry an `**Issue:**` header in their opening metadata even though their authoritative GitHub tickets are #80, #84, #88 and #91 respectively.

So a new invariant cannot simply require every historical F-series document to contain an issue header without either rewriting accepted historical research or introducing a migration ticket.

## Authority model

Use two independent facts, in this order:

1. **namespace reservation:** the presence of any committed `docs/research/F-NNN-*.md` on the merge base reserves `F-NNN`;
2. **ticket ownership proof:** explicit `**Issue:** #N` metadata proves which issue owns a new or changed F-series research artifact.

This avoids a separate registry while remaining fail-closed for legacy metadata gaps.

### New identifier

If the current branch introduces the first `docs/research/F-NNN-*.md` for an ID that is absent from the merge base:

- at least one newly introduced research artifact for that ID must declare exactly one `**Issue:** #N`;
- every explicit issue declaration among that ID's research artifacts must name the same issue;
- malformed/multiple issue declarations fail deterministically.

The F-021 research file itself is an example: `F-021` is new and declares #99.

### Existing identifier with explicit owner on base

If `F-NNN` already exists on the merge base and the base research artifacts establish exactly one explicit owner issue:

- a newly added research/evidence/amendment file under the same ID is allowed only when its explicit issue metadata matches the existing owner;
- a conflicting explicit issue number fails;
- changing an existing ownership declaration to a different issue fails.

This permits legitimate multiple documents for one ticket, such as an evidence note or review amendment, without permitting namespace reassignment.

### Existing legacy identifier without explicit owner on base

If an ID already exists on the merge base but no base research artifact declares an issue number, the ID is still **reserved**.

A branch must not claim that legacy ID for a new ticket merely because ownership metadata is absent. New F-series research under such an ID should fail closed with a diagnostic such as:

`F-012 is a reserved legacy identifier without machine-readable owner metadata; choose a new feature ID or establish ownership in a separately reviewed metadata migration.`

This is intentionally stricter than guessing from issue titles, commit history or filenames. It avoids hidden network/history dependence in the contract.

A later metadata-only migration could annotate legacy IDs if continued amendments to them become necessary; F-021 does not need that migration merely to protect new allocations.

## Why not a hand-maintained registry

A registry such as `feature-ids.json` would duplicate information already present in research paths and issue metadata. It would also create a second file that agents must remember to update atomically, recreating the same class of drift the invariant is meant to prevent.

Research files are already mandatory artifacts in the development loop, so they are the natural ownership source.

## Why not GitHub API lookup in ordinary CI

GitHub issue titles do provide useful external evidence for legacy IDs, but making correctness depend on live issue/PR enumeration would add:

- network availability;
- token/permission behavior;
- pagination/rate-limit handling;
- mutable issue titles;
- more complicated local reproduction.

More importantly, a network lookup is unnecessary for the merge-time safety goal. A static repository check becomes decisive after one colliding branch lands and the other is rebuilt/integrated with current `main`, which is already a mandatory finalization step in this project.

The check cannot observe two branches that have never shared a base containing either new allocation. That limitation is real and should be documented rather than hidden. The final current-main integration gate is where the second branch becomes rejectable deterministically.

## Proposed static contract

A later plan may implement a pure-Python repository test with no Git/network calls. Conceptually:

1. enumerate `docs/research/F-[0-9][0-9][0-9]-*.md` in the merge-base fixture and current tree;
2. extract the `F-NNN` prefix from each path;
3. extract zero or one explicit issue declaration from a small metadata/header region;
4. reject multiple distinct explicit issue numbers for one F ID;
5. reject a new F ID with no explicit issue owner;
6. reject a new artifact under an already-reserved legacy/headerless ID;
7. permit multiple artifacts under an ID only when ownership is consistent;
8. return sorted deterministic diagnostics.

The implementation must not call GitHub or `git` at test runtime. Like F-008, tests can exercise a deterministic classifier against synthetic path/content fixtures, and a repository-state test can validate the checked-out tree.

## Plans/workflows/tests as consistency checks

Research ownership should remain authoritative. Plans, workflows and test-package names are downstream artifacts, so a future plan may also require:

- any newly introduced `docs/plans/F-NNN-*` has an owned research ID;
- any newly introduced `.github/workflows/fNNN-*` has an owned research ID;
- any newly introduced `tests/fNNN/**` has an owned research ID.

These checks catch typos and stale renames, but they must not require every research-only feature to have implementation artifacts.

This would have caught the F-018 branch's stale `F-015` workflow/test namespace after F-015 became reserved by #87.

## RED strategy if independently approved

Before implementation, tests should pin at least:

1. two different explicit issues under one F ID -> fail;
2. two files with the same F ID and same issue -> pass;
3. brand-new F ID with one explicit issue -> pass;
4. brand-new F ID with no issue metadata -> fail;
5. existing legacy/headerless ID remains reserved -> new artifact fails rather than becoming silently claimable;
6. changing an established owner issue -> fail;
7. malformed or duplicate `**Issue:**` declarations -> fail deterministically;
8. unrelated R/P/I/A/D research files are ignored;
9. research-only F ID without plans/workflows/tests remains valid;
10. downstream plan/workflow/test artifact with unknown or mismatched feature ID fails if that optional consistency layer is adopted;
11. diagnostics are sorted and stable across filesystem enumeration order.

The RED must fail because the ownership classifier/check does not yet exist, not because current accepted repository history is retroactively invalidated.

## Scope and non-goals

- no automatic renumbering;
- no rewriting accepted historical research merely to normalize headers;
- no live GitHub API dependency in normal CI;
- no promise to detect two completely independent, never-integrated branches simultaneously;
- no runtime/schema/digest/ontology behavior change;
- no general ticket taxonomy redesign beyond the F-series collision demonstrated here.

## Conclusion

F-021 is implementable as a local, deterministic merge-time namespace invariant.

The correct authority is not a new registry and not workflow/test naming. Current-main research paths reserve IDs; explicit issue metadata proves ownership for new/changed artifacts; legacy headerless IDs remain reserved fail-closed. Because every feature branch is already required to integrate current main before final exact-head review, this is sufficient to prevent the observed collision from reaching merge even though it cannot provide cross-branch omniscience before integration.
