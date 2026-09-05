# R-005 independent-review reconciliation

**Issue:** #5  
**PR:** #7  
**Recorded:** 2026-09-05  
**Status:** normative amendment to `R-005-corpus-semantic-census.md` for the reviewed R-005 branch

This note records how the blocking findings from independent skeptical reviews were addressed. It is not a substitute for a fresh independent review: every material fix invalidates reviews of earlier heads.

Where this amendment conflicts with deferred-work shorthand in `R-005-corpus-semantic-census.md`, this amendment is authoritative for PR #7. In particular, the stale §7 sentence saying that CUC editorial domains should only be regenerated when a production mapping is designed is superseded: the exact observed release domains are generated and preserved by R-005 itself.

## Finding 1 — incomplete per-corpus feature/value census

### Review finding

The earlier report documented representative feature families but did not provide the complete per-corpus node/edge feature census required by issue #5. In particular, bounded values such as CUC `cert` and `emen` were not exhaustively recorded from the pinned released artifact.

### Resolution

The branch now contains reproducible research tooling:

- `scripts/research/r005_inventory.py`
- `tests/research/test_r005_inventory.py`
- `.github/workflows/r005-research-inventory.yml`
- generated exact-artifact inventories under `docs/research/data/generated/r005/`

The workflow checks out the exact pinned TF directories for BHSA 2021, CUC 0.2.8, ETCBC Syriac 0.9, Peshitta 0.2, SyrNT 0.1, ExtraBiblical 0.2, and TLHdig-TF 0.2.0. It loads those artifacts with Text-Fabric 13.1.0 and records, for every non-warp node/edge feature:

- feature metadata, including source `@description` and `@valueType` where present;
- node types on which a non-empty value is actually observed;
- count of nodes carrying a semantic value;
- observed value cardinality;
- the complete observed non-empty domain when it has at most 64 values;
- a bounded sample and cardinality when the observed domain is larger;
- edge source and target node types;
- whether an edge is valued;
- observed valued-edge domains;
- the exact corpus revision/version and a digest over the inspected `.tf` feature files.

The generator intentionally says `observed_small_domain`, not `closed vocabulary`. A small observed release domain is empirical evidence; formal categorical closure still requires corpus documentation/source semantics.

### TDD regressions discovered while closing the finding

The first exact multi-corpus run exposed a real filesystem edge case: BHSA contains a directory whose name ends in `.tf`. The digest walker initially treated it as a feature file. A failing regression was added, then the walker was restricted to actual files.

The next exact run exposed a semantic edge case in dense TF features: loaded feature APIs can contain empty-string records for positions with no semantic value. Treating `""` as a category member both polluted the observed domain and made a feature appear applicable to node types on which it carried no value. A failing regression was added first; the generator now:

- excludes `None` and `""` from semantic domains;
- excludes those records when deriving `applies_to`;
- records `empty_observation_count` and `raw_observation_count` separately.

The same run also corrected the manually anticipated CUC emendation inventory. At pinned CUC `ad69400f5446e1c8217af01659c7c10ab00c015b`, non-empty `emen` values are:

- `excised`
- `missing`
- `redundant`
- `remark`
- `restored`

The previously omitted `remark` value is now a regression assertion. `cert` has the non-empty observed domain `False`, `True`.

The generated CUC inventory also preserves dense empty-record counts separately (`cert`: 68,802; `emen`: 93,786). These empty records are not semantic domain members.

### What is and is not deferred

R-005 has already measured and preserved the exact observed domains for the pinned corpus releases. A later production mapping must **not** rediscover those values as if R-005 had deferred the evidence collection. The later mapping stage still has to decide:

1. whether an observed small release domain is formally closed under the corpus's documented semantics;
2. which ontology term, if any, each native value maps to;
3. the reviewed mapping strength and provenance;
4. how later parent-corpus revisions change the observed domain.

This distinction supersedes the conflicting sentence in §7 of the main census report.

## Finding 2 — missing explicit candidate relationship classes

### Review finding

The earlier cross-corpus table often described representation/presence but did not assign the required `same | close | broader/narrower | related | unknown | local-only` class to every apparent semantic match.

### Resolution

`docs/research/R-005-candidate-strength-matrix.md` now provides a separate explicit classification matrix. Every relevant corpus/semantic-cluster cell is prefixed with one of:

- `S` — same at the deliberately stated row-level abstraction;
- `C` — close;
- `B` — broader;
- `N` — narrower;
- `R` — related but not substitutable;
- `U` — unknown/unsupported/not established;
- `L` — local-only language/annotation-system category.

`S` explicitly does **not** imply OWL identity/equivalence. These are conservative research-stage candidate relations; later ontology mappings must provide term-level evidence and may weaken, but may not silently strengthen, them.

The matrix pins several negative cases that later design/runtime tests must preserve:

- ORACC `c type=sentence` is `U` for the BHSA-style linguistic-sentence concept;
- Peshitta A/B witness designation, TLHdig line→fragment witness, and Pseudepigrapha reading→manuscript witness remain different relations;
- TLHdig lexical entities may map at the lexical-entity level, while their technical one-slot `oslots` anchor must not be interpreted as occurrence extent;
- Hebrew, Syriac, Hittite, and Akkadian/source-specific verbal systems remain `L` where exact category identity is not established;
- damage/restoration, witness omission/non-attestation, and uncertainty/confidence remain distinct semantic clusters.

## Finding 3 — final generated-data head lacked an exact-head verification run

### Review finding

The inventory workflow previously regenerated JSON and committed it back to the PR branch. A successful run could therefore verify one SHA and then mutate the branch to a different final SHA. Relying on that workflow's own `GITHUB_TOKEN` push to trigger a recursive verification run is also not a sound gate because GitHub suppresses most workflow recursion caused by `GITHUB_TOKEN` events.

That violates the repository's exact-head review discipline: the final reviewed tree must itself be verified.

### Resolution

The R-005 research inventory workflow is now **read-only and non-mutating**.

It triggers for the complete R-005 evidence contract:

- `.github/workflows/r005-research-inventory.yml`
- `scripts/research/r005_inventory.py`
- `tests/research/test_r005_inventory.py`
- `docs/research/R-005-corpus-semantic-census.md`
- `docs/research/R-005-candidate-strength-matrix.md`
- `docs/research/R-005-review-reconciliation.md`
- `docs/research/data/R-005-corpus-pins.json`
- `docs/research/data/generated/r005/**`

For the exact checked-out PR head the workflow:

1. checks out every exact pinned upstream corpus;
2. reruns the research-tool unit tests;
3. regenerates all seven inventories in place;
4. reruns the CUC editorial-domain regressions;
5. executes `git diff --exit-code -- docs/research/data/generated/r005`;
6. succeeds only when the committed inventories are byte-for-byte identical to regeneration from the pinned sources on **that same head**;
7. never commits or pushes from verification CI.

If generator logic, pins, or generated evidence change, the developer must regenerate and commit those artifacts as part of the PR before the verification gate can become green. This makes the tested tree and reviewed tree identical and removes recursive-workflow behavior from the correctness model.

A separate lightweight read-only workflow, `r005-generated-validation.yml`, additionally validates the already committed inventory set (pins, node counts, metadata/value accounting, semantic edge subset, CUC regressions and known edge directions). It complements but does not replace the full pinned-source regeneration gate.

## Finding 4 — one-time report reconciliation CI remained write-enabled

### Review finding

After the report had already been reconciled, the branch still contained `.github/workflows/r005-report-reconcile.yml` with `contents: write` and a `git push`, plus the one-time migration script `scripts/research/r005_reconcile_report.py`. A future edit to either file could therefore move the PR head from CI and recreate the same class of exact-head race eliminated in Finding 3.

### RED → GREEN resolution

A regression was added first in `tests/research/test_r005_generated.py`. It requires:

- the one-time reconciliation workflow to be absent;
- the one-time migration script to be absent;
- both remaining R-005 verification workflows to declare `contents: read`;
- neither remaining verification workflow to contain `contents: write` or `git push`.

The regression failed on head `69db8578ac4597b15a4f8349ca784f8c71d49b8a`, proving the stale mutating scaffold was still present. The workflow and script were then removed. The authoritative report already contains the migrated text, so no persistent write-enabled migration mechanism is required.

## Final review gate

A fresh independent skeptical reviewer must inspect the exact stable head after:

1. the non-mutating pinned inventory workflow is green on that exact head;
2. all generated inventories are present in the branch;
3. workflow regression assertions pass;
4. the candidate-strength matrix remains unchanged or any later change is included in that review;
5. this reconciliation amendment and its exact-head CI rule are part of the reviewed tree;
6. no write-enabled R-005 CI remains in the branch.

The reviewer should verify the generated inventories against at least several pinned upstream feature files and explicitly check that the prior blocking findings are closed. An author-side reread or approval attached to an earlier head does not satisfy this gate.

## Acceptance trace amendment

- [x] Exhaustive machine-readable pinned feature/domain inventories exist for all seven released primary census corpora.
- [x] Dense empty/`None` TF records are separated from semantic observed values.
- [x] CUC `cert` and `emen` exact observed release domains are regression-checked.
- [x] Candidate mapping strengths are explicit in the companion matrix rather than inferred from representation prose.
- [x] Generated inventories are committed reviewable artifacts.
- [x] The stale CUC deferral statement is explicitly superseded by the generated R-005 evidence contract.
- [x] Exact-head verification is non-mutating and compares regenerated inventories byte-for-byte with committed evidence.
- [x] Verification CI requires only read access to repository contents.
- [x] The one-time write-enabled reconciliation workflow/script have been removed and are regression-protected against reintroduction.
- [ ] The resulting exact stable head must finish green.
- [ ] A fresh independent reviewer who did not author these fixes must review that stable head before merge.
