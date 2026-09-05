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

The inventory workflow can regenerate JSON and commit it back to the PR branch. Before this fix, generated inventory paths did not trigger the workflow. A successful run could therefore create a **new PR head** containing the generated evidence while the green run remained attached only to its parent SHA.

That violates the repository's exact-head review discipline: the final reviewed tree must itself be verified.

### Resolution

The workflow trigger now covers the entire R-005 evidence contract, including:

- `.github/workflows/r005-research-inventory.yml`
- `scripts/research/r005_inventory.py`
- `tests/research/test_r005_inventory.py`
- `docs/research/R-005-corpus-semantic-census.md`
- `docs/research/R-005-candidate-strength-matrix.md`
- `docs/research/R-005-review-reconciliation.md`
- `docs/research/data/R-005-corpus-pins.json`
- `docs/research/data/generated/r005/**`

The resulting gate is deliberately two-stage when generation changes committed evidence:

1. a relevant source/research change runs the pinned census, regressions and deterministic generation;
2. if JSON inventories differ, CI commits only the regenerated inventories;
3. that generated-output commit itself triggers the workflow because generated paths are included;
4. the second run must regenerate byte-for-byte identical inventories, produce no commit, and finish green;
5. the stable final PR head therefore has a green R-005 run attached to that exact tree.

A no-diff run on a source/research head is already exact-head verification. A generated-data commit is not considered final evidence until its follow-up run is green.

## Final review gate

A fresh independent skeptical reviewer must inspect the exact stable head after:

1. the pinned inventory workflow is green on that exact head;
2. all generated inventories are present in the branch;
3. workflow regression assertions pass;
4. the candidate-strength matrix remains unchanged or any later change is included in that review;
5. this reconciliation amendment and its exact-head CI rule are part of the reviewed tree.

The reviewer should verify the generated inventories against at least several pinned upstream feature files and explicitly check that the prior blocking findings are closed. An author-side reread or approval attached to an earlier head does not satisfy this gate.

## Acceptance trace amendment

- [x] Exhaustive machine-readable pinned feature/domain inventories exist for all seven released primary census corpora.
- [x] Dense empty/`None` TF records are separated from semantic observed values.
- [x] CUC `cert` and `emen` exact observed release domains are regression-checked.
- [x] Candidate mapping strengths are explicit in the companion matrix rather than inferred from representation prose.
- [x] Generated inventories are committed reviewable artifacts.
- [x] The stale CUC deferral statement is explicitly superseded by the generated R-005 evidence contract.
- [x] Workflow path coverage makes a generated-output head trigger its own verification run.
- [ ] The resulting exact stable head must finish green.
- [ ] A fresh independent reviewer who did not author these fixes must review that stable head before merge.
