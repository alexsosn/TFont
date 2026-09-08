# F-007 plan amendment: fork-safe cancellation and exact-head CI

**Issue:** #34  
**Parent plan:** `docs/plans/F-007-ci-full-suite-deduplication-plan.md`

## Why this amendment exists

The first amendment corrected SHA-scoped concurrency to branch-scoped cancellation. Independent adversarial review of exact head `d6bab201080ab6db2a744aff1fb1ef9d6c6215cc` found three further integration/robustness gaps before merge:

1. the branch had fallen behind current `main`, so final full-suite evidence no longer covered the current repository tree;
2. branch-name-only concurrency can collide across fork PRs that use the same source branch name;
3. the static future F-006 preservation assertion no longer matches the actual reviewed F-006 focused workflow, and the focused F-007 workflow labels checkout as exact-head without explicitly selecting the PR head SHA.

The branch has therefore been rebuilt on current `main` `03a6a89e93f0dbe2ae6b20a12f2f55cb6f47fb5a` before these contract changes. This amendment is committed before changing the RED contract or either workflow.

## Fork-safe concurrency contract

The authoritative full-suite workflow must namespace cancellation by **source repository plus source branch**:

```yaml
concurrency:
  group: full-suite-${{ github.event.pull_request.head.repo.full_name || github.repository }}-${{ github.event.pull_request.head.ref || github.ref_name }}
  cancel-in-progress: true
```

Properties:

- same-repository push and PR runs for the same branch use the same repository/branch pair and may cancel stale duplicates;
- successive commits on the same source branch share the group;
- two fork PRs with the same branch name do not cancel each other because their head repositories differ;
- cancellation identity remains independent of commit SHA, while checkout identity remains exact-head SHA.

The static CI contract must require both the repository namespace and branch discriminator rather than accepting branch name alone.

## Exact-head checkout contract

Both the authoritative full-suite workflow and the focused F-007 ownership-contract workflow must explicitly check out the source head:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha || github.sha }}
```

This keeps the focused contract test and the authoritative suite tied to the same exact authored head instead of relying on the synthetic pull-request merge ref.

## F-006 integration contract

F-006 is still unmerged, so F-007 must not modify its branch. The static ownership test may nevertheless recognize it when present, but the preservation assertion must match the actual F-006 focused contract on exact head `c1e05d34b3d12e047b07fe067770201da7be7de9`:

- `python -m unittest discover -s tests/f006 -v`;
- `python -m unittest discover -s tests/i001 -v`.

The assertion remains conditional while the workflow is absent from `main`. If F-006 merges before F-007 finalization, reintegrate current main, remove only F-006's generic full-suite step, and rerun RED/GREEN/current-head CI as needed.

## RED gate after this amendment

Before workflow implementation changes, update only `tests/ci/test_full_suite_workflow_contract.py` so the focused F-007 contract requires:

1. exactly one owner of the canonical full-repository unittest command;
2. Python 3.10/3.12 and existing trigger/packaging coverage;
3. repository-qualified plus branch-qualified concurrency with cancellation;
4. explicit exact-head checkout in both `full-suite.yml` and `f007-ci-full-suite-dedup.yml`;
5. the corrected optional F-006 focused-test tokens.

On the pre-GREEN workflows this must fail specifically because fork-safe repository qualification and focused F-007 explicit head checkout are absent.

## GREEN gate

Then change only the two F-007-owned workflow files needed for these findings:

- `.github/workflows/full-suite.yml`: repository+branch concurrency namespace;
- `.github/workflows/f007-ci-full-suite-dedup.yml`: explicit exact-head checkout.

Run on the new exact head:

- focused F-007 ownership contract;
- authoritative full repository suite on Python 3.10 and 3.12.

Before final review, verify the branch is still based on current `main`. Any material reintegration or implementation change invalidates earlier review and requires a fresh logically-independent exact-head adversarial review.

No runtime, schema, digest, corpus, semantic, test-semantic, matrix, or trigger-path behavior changes are in scope.