# I-009 amendment: ExtraBiblical source POS evidence

**Recorded:** 2026-09-11  
**Supersedes:** the unresolved inspection note in section 4 of `I-009-production-noun-bundles.md`

## Finding

The exact ExtraBiblical source artifact at:

```text
ETCBC/extrabiblical@9a56288e6777bad6328856acf055c780e65dd5d9
source/0.2/extraBiblical.mql.bz2
Git blob: 4ba717b1716b747bb94d0359b950a55d8624b109
```

contains the native schema declaration:

```text
CREATE ENUMERATION part_of_speech_t = {
  art = 0,
  verb = 1,
  subs = 2,
  nmpr = 3,
  advb = 4,
  prep = 5,
  conj = 6,
  prps = 7,
  prde = 8,
  prin = 9,
  intj = 10,
  nega = 11,
  inrg = 12,
  adjv = 13
}
```

and the word object schema types `sp` as `part_of_speech_t`. The hosted I-009 research workflow asserts these facts directly from the compressed exact source.

The exact generated `tf/0.2/sp.tf` contains both `subs` and `nmpr`, so the chain from native MQL enum members to generated TF feature values is observed on the exact supported parent release.

## Semantic interpretation boundary

The MQL enum gives the native POS type and stable code members but does **not** itself provide human-language glosses such as `subs = noun` or `nmpr = proper noun`. We therefore must not claim a local ExtraBiblical glossary that does not exist.

The repository's own README supplies the interpretation boundary instead:

- it identifies ExtraBiblical as ETCBC-encoded MQL material converted to Text-Fabric;
- it places `extrabiblical` in the BHSA extended family;
- it explicitly identifies `bhsa` as **Core data and feature documentation**.

At the exact BHSA revision selected for this release, that core feature documentation defines `sp` as part of speech, `subs` as `noun`, and `nmpr` as `proper noun`.

The production ExtraBiblical evidence record should therefore preserve both sides of this evidence chain:

1. exact ExtraBiblical source/payload evidence proving that word `sp` is the native `part_of_speech_t` field and that `subs`/`nmpr` are exact native enum values used by the supported parent;
2. the repository-declared BHSA-family feature-documentation authority, pinned to the exact BHSA feature document used by the review, proving the human semantic glosses of those shared ETCBC codes.

This is stronger than inferring meaning from coincident strings and more accurate than pretending that the ExtraBiblical source itself contains the glosses.

## Consequence for the production review

The pinned OLiA Reference Model places both `CommonNoun` and `ProperNoun` directly under `Noun`. Because ExtraBiblical preserves separate `subs` and `nmpr` POS members, the exact reviewed selector for the broad OLiA class is:

```text
word.sp in {subs,nmpr}
execution_shape=value-set-predicate
```

not `word.sp=subs` alone.

That remains a scholarly review decision, not a mechanical rule such as "all ETCBC values with these spellings have the same semantics". The final review record must bind the production mapping digest and list the two-part evidence chain above. Each selected value must have a matching semantic `native-value-present` dependency under the merged I-010 contract. No generic ETCBC-code resolver or boolean query planner is introduced in I-009.
