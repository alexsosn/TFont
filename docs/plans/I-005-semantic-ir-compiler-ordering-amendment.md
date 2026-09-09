# I-005 plan amendment: explicit UTF-16 ordering and participating fingerprints

**Issue:** #123  
**Status:** normative amendment to the I-005 compiler plan  
**Reason:** adversarial plan check before independent review

Where this amendment conflicts with earlier I-005 plan text, this amendment is authoritative.

## 1. Do not use dataclass-generated ordering

The parent plan used `@dataclass(frozen=True, order=True)` in examples while also requiring contract-visible UTF-16 code-unit ordering. Those two requirements conflict.

Python dataclass-generated comparison delegates to Python string comparison, which is Unicode code-point order rather than the repository's pinned UTF-16 code-unit order for all strings. It also cannot safely compare `None` and `str` in a nullable tuple field such as `ontology_bundle_digest` when preceding fields are equal.

Therefore **all public IR/key records are frozen but non-orderable by default**:

```python
@dataclass(frozen=True)
class BundleVariantKey: ...

@dataclass(frozen=True)
class ProfileReleaseKey: ...

@dataclass(frozen=True)
class SemanticKey: ...
# same for AuthorityKey, IdentityKey, IdentifierKey, NativeKey, CapabilityKey
```

No public ordering semantics are implied by `__lt__`.

## 2. Explicit internal sort keys

Implement dedicated total-order helpers for every contract-visible collection.

String component:

```python
def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16be")
```

Nullable string component uses an explicit tag, for example:

```text
None -> (0, b"")
str  -> (1, utf16(value))
```

The exact tag direction above is frozen for v1: `None` sorts before present strings.

Composite records are sorted by tuples of those tagged/UTF-16 component keys, never by dataclass comparison and never by Python's default string ordering.

## 3. RED additions for ordering

Add deterministic regressions with strings whose Python code-point order differs from UTF-16 code-unit order. Use synthetic IDs only; do not require such strings to be meaningful ontology terms.

At minimum prove:

1. semantic/index key ordering follows UTF-16 code units for a BMP-vs-supplementary pair;
2. bundle variants identical except `ontology_bundle_digest=None` versus a present digest sort deterministically with `None` first and never raise `TypeError`;
3. input order reversal yields identical tuple-index order under those adversarial strings;
4. callers are not expected to sort public key dataclasses directly through generated comparison operators.

## 4. Participating ontology-lock fingerprints

The profile-release coherence amendment says the release signature carries sorted ontology-lock fingerprints. Freeze this as **participating/reachable locks**, not every unused lock artifact merely present in a source bundle.

The participating set is the union of lock IDs referenced by:

- approved projections;
- ambiguous candidates;
- active ontology-bundle source entries;
- reviewed bridge endpoints/requirements when a bundle is active.

I-004 has already validated those references and bundle/bridge closure. An otherwise unused extra ontology-lock artifact does not become execution semantics merely because it was packaged in the source bundle.

The profile-release signature and `BundleVariantIR` runtime fingerprints use this reachable participating set. The compiler may retain unused lock artifacts nowhere in runtime IR; they remain source-level material.

Add a RED control proving an extra unused lock artifact does not change semantic IR/profile-release signature, while changing a referenced lock identity does.

## 5. Embedded policy versions

P-003 asks runtime IR to preserve reference-policy/catalog and approximation-policy versions where relevant. Current I-004 v1 exposes no separate authored reference-policy or approximation-policy version fields: standalone reference catalog artifacts are explicitly unsupported, and routing/assessment/loss vocabularies are frozen by mapping schema v2 plus the current controlled semantic vocabulary.

I-005 therefore must not invent new source version fields. In v1 provenance:

- `mapping schema_version == 2` plus mapping semantic algorithm v2 identifies the mapping/reference/approximation source contract;
- `profile_catalog_version == 1` identifies the controlled profile/capability catalog;
- the compiled IR may expose descriptive constants such as `reference_policy_version="mapping-v2"` / `approximation_policy_version="mapping-v2"` only if the plan/RED makes clear that these are compiler contract labels derived from the validated mapping schema version, not authored independent identities.

Prefer carrying the actual validated schema/catalog versions and avoiding redundant labels in I-005 unless I-006 demonstrates a lookup need.