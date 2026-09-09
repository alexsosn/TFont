# I-005 plan amendment: review authority is release semantics

**Issue:** #123  
**Status:** normative amendment to the I-005 compiler plan and prior profile-release coherence amendment  
**Reason:** logically-independent adversarial plan review found an authorization-coherence blocker

Where this amendment conflicts with earlier I-005 plan text, this amendment is authoritative.

## 1. Blocker

I-005 uses review status as an authorization boundary:

- only a mapping with `mapping.review.status == "reviewed"` may contribute positive capability support or authoritative external-reference indexes;
- a target projection enters `semantic_index` / `authority_index` only when both its parent mapping and `projection.review.status` are `reviewed`.

The prior `ProfileReleaseSignature` covered mapping semantic digests but excluded review state. Mapping/projection semantic digests intentionally exclude their review wrappers. Therefore two exact-parent variants under the same:

```text
(corpus_id, authored_profile_id, profile_version)
```

could have identical semantic digests yet different review statuses (`reviewed` versus `provisional`/`disputed`). They would pass release-coherence checks while compiling different authoritative indexes and capability facts.

That is invalid. Review status is audit metadata only when it does not affect authorization. In I-005, the controlled status and the digest binding it authorizes are runtime semantic authority and must be coherent across one profile release.

## 2. Authoritative review fingerprint

Freeze an authorization-relevant review fingerprint distinct from audit-only review provenance:

```python
@dataclass(frozen=True)
class ReviewFingerprint:
    review_id: str
    status: str
    reviewed_semantic_digest: str
```

For mapping reviews, `reviewed_semantic_digest` is `reviewed_mapping_digest` bound to the mapping-v2 semantic digest.

For projection reviews, it is `reviewed_mapping_digest` bound to the projection semantic digest under the current schema naming.

The following remain audit-only for I-005 release coherence and may vary without changing compiled authority:

- `reviewer_id`;
- `reviewed_at`;
- `review_source`;
- `review_method`;
- free-form notes.

A future contract may promote more review provenance into release identity, but I-005 does not do so implicitly.

## 3. Profile release signature addition

`ProfileReleaseSignature` must additionally contain deterministic authorization fingerprints for every mapping and approved projection:

```text
sorted mapping review fingerprints keyed by mapping_id
sorted projection review fingerprints keyed by (mapping_id, projection_id)
```

The fingerprint includes exactly:

```text
review_id
status
reviewed_semantic_digest
```

Review fingerprints are sorted using the explicit UTF-16 ordering rules from `I-005-semantic-ir-compiler-ordering-amendment.md`.

Consequences:

- same mapping/projection semantics + same review authorization + different parent digest -> legal exact-parent variants;
- same release key + mapping review status change -> `profile_release_conflict`;
- same release key + projection review status change -> `profile_release_conflict`;
- same release key + review ID or reviewed-digest binding change -> `profile_release_conflict`;
- audit-only reviewer/timestamp/method/note edits do not create a false release conflict;
- a bumped `profile_version` may carry changed review authorization as a distinct release.

This makes the prior statement true by construction: one `ProfileReleaseKey` has stable authoritative semantic-index/capability content across all of its exact-parent variants.

## 4. Evidence preservation in compiled target bindings

The issue requires mapping/projection review and evidence identities to survive into compiled binding records so I-006 does not need to reopen source mappings.

`TargetBindingIR` must preserve mapping-level and projection-level evidence separately:

```python
mapping_evidence: tuple[EvidenceFingerprint, ...]
projection_evidence: tuple[EvidenceFingerprint, ...]
```

Do not collapse them into one unlabeled tuple. Mapping evidence and projection evidence authorize different source assertions and may overlap without being semantically interchangeable.

`NativeRecordIR` retains mapping-level evidence. `CandidateIR` and `ExternalReferenceIR` retain their own evidence bindings where the source schema provides them.

Review-record `evidence` string lists are audit/source-review metadata under the current v2 schema and are not substituted for content-addressed mapping/projection `EvidenceFingerprint` bindings.

## 5. RED additions

Before GREEN, add regressions proving:

1. same release key + identical semantics but mapping review status `reviewed` versus `provisional` -> `profile_release_conflict`;
2. same release key + identical semantics but projection review status `reviewed` versus `provisional` -> `profile_release_conflict`;
3. same release key + changed mapping/projection `review_id` or reviewed semantic digest -> `profile_release_conflict`;
4. audit-only reviewer/timestamp/method/notes edits do not create a release conflict;
5. two legal parent variants of one release compile identical authoritative semantic/authority/index membership and capability facts apart from variant provenance;
6. `TargetBindingIR` exposes mapping and projection evidence as separate content-addressed fingerprint tuples.

## 6. Error precedence

When several composition defects coexist, use deterministic precedence:

1. API type errors;
2. invalid zero/multi-corpus bundle scope;
3. exact duplicate `BundleVariantKey`;
4. `profile_release_conflict` across distinct variants sharing one release key;
5. downstream compiled-index assembly conflicts.

A review-coherence mismatch is therefore reported as `profile_release_conflict`, not silently expressed as differing per-variant index contents.

## 7. I-006 handoff

I-006 may rely on this invariant:

> For one `ProfileReleaseKey`, all exact-parent variants expose the same reviewed semantic authority; runtime selection changes parent provenance/compatibility, not which mappings or projections are authorized.

I-006 therefore selects the compatible parent variant without re-evaluating review status or comparing source review wrappers across variants.