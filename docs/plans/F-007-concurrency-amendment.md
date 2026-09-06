# F-007 plan amendment: branch-scoped cancellation and exact-head checkout

**Issue:** #34  
**Parent plan:** `docs/plans/F-007-ci-full-suite-deduplication-plan.md`

## Why this amendment exists

The initial plan used the commit SHA as the `concurrency.group` discriminator. That does not cancel a stale run after a new commit is pushed to the same branch because each commit gets a different group. The RED contract inherited the same mistake.

This was detected after the first valid RED run (`34050023987`) and before any production workflow was edited. The correction therefore changes the plan/acceptance contract, not implementation behavior after the fact.

## Corrected concurrency contract

Use the source branch identity for cancellation:

```yaml
concurrency:
  group: full-suite-${{ github.event.pull_request.head.ref || github.ref_name }}
  cancel-in-progress: true
```

For a pull request, `github.event.pull_request.head.ref` is the source branch name. For a push, `github.ref_name` is that same branch name. Successive push/PR runs for one source branch therefore share a group and stale runs can be cancelled.

## Exact-head checkout remains a separate concern

The authoritative workflow must still check out the exact source head rather than the pull-request merge ref:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha || github.sha }}
```

The static CI contract must require both expressions:
- `github.event.pull_request.head.ref || github.ref_name` for concurrency;
- `github.event.pull_request.head.sha || github.sha` for exact-head checkout.

No runtime, test semantic, matrix, trigger-path, or focused-workflow responsibility changes from the parent plan.
