# R-005 independent-review reconciliation

**Issue:** #5  
**PR:** #7  
**Recorded:** 2026-09-05

This note records how the two blocking findings from the independent skeptical review of the earlier head `14ba5919a283d11912f994036ad9495c0346a99a` were addressed. It is not a substitute for a fresh independent review: the fixes are material and therefore invalidate every review of that earlier head.

## Finding 1 — incomplete per-corpus feature/value census

### Review finding

The earlier report documented representative feature families but did not provide the complete per-corpus node/edge feature census required by issue #5. In particular, bounded values such as CUC `cert` and `emen` were not exhaustively recorded from the pinned released artifact.

### Resolution

The branch now contains reproducible research tooling:

- `scripts/research/r005_inventory.py`
- `tests/research/test_r005_inventory.py`
- `.github/workflows/r005-research-inventory.yml`
- generated exact-artifact inventories under `docs/research/data/generated/r005/` after the workflow's generated-data commit

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

The same run also corrected the manually anticipated CUC emendation inventory. At pinned CUC `ad69400f5446e1c8217af01659c7c10ab00c015b`, non-empty `emen` values include:

- `excised`
- `missing`
- `redundant`
- `remark`
- `restored`

The previously omitted `remark` value is now a regression assertion. `cert` is asserted to have the non-empty observed domain `False`, `True`.

The final exact pinned workflow is a release gate for this research PR. The PR is not considered reconciled until that workflow is green and the generated inventories are committed on the branch.

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

## Final review gate

A fresh independent skeptical reviewer must inspect the exact final head after:

1. the pinned inventory workflow is green;
2. all generated inventories are present in the branch;
3. the workflow regression assertions pass;
4. the candidate-strength matrix remains unchanged or any later change is included in that review.

The reviewer should verify the generated inventories against at least several pinned upstream feature files and explicitly check that the two prior blocking findings are closed. An author-side reread or approval attached to an earlier head does not satisfy this gate.
