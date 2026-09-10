# I-007 plan-review amendment — keep parent compatibility orthogonal to ontology-bundle availability

**Issue:** #130  
**Amends:** `docs/plans/I-007-runtime-prerequisite-evaluator-plan.md`  
**Reason:** logically-independent adversarial plan review

Where this amendment is more specific than the parent plan, this amendment is authoritative.

## Finding

The parent plan calls `verified-exact | verified-compatible | unverified | incompatible` an "overall state" while also preserving I-006's separate `ontology_bundle_state` axis. That wording is unsafe.

I-006 deliberately evaluates these axes separately: parent/release dependency compatibility is represented by `parent_state`, while local ontology-bundle availability is represented by `ontology_bundle_state` and `active_ontology_bundle_digest`. Resolver diagnostics distinguish, for example, `parent_unverified` from `ontology_bundle_unavailable`.

If I-007 were to downgrade `parent_state` to `unverified` merely because a required ontology bundle is unavailable, I-006 would fail at the parent gate before reaching the bundle gate. The evaluator would thereby erase a more precise runtime fact and would make bundle installation appear to require re-evaluating parent compatibility.

## Normative correction

Treat runtime prerequisite state as orthogonal axes, not one overloaded four-state executable status.

### Parent/dependency compatibility axis

`RuntimePrerequisiteState.parent_state` is derived only from the observed parent identity plus the complete P-002 release dependency closure:

- any deterministic dependency/component failure -> `incompatible`;
- else any required dependency/parent observation is unknown/incomplete -> `unverified`;
- else observed parent digest equals expected digest -> `verified-exact`;
- else observed parent digest differs and the complete dependency closure passes -> `verified-compatible`.

A required ontology bundle being unavailable, stale, or malformed does **not** rewrite an otherwise established parent state.

### Ontology-bundle axis

Preserve I-006's independent bundle state exactly:

- release requires no bundle -> `not-required`, active digest `None`;
- required bundle is locally selected and exact -> `verified`, exact active digest;
- required bundle is not locally available/selected -> `unavailable`, active digest `None`;
- explicitly selected different digest -> stale/mismatched runtime input;
- malformed/empty digest -> invalid input.

### Executability

If `RuntimeEvaluationReport` exposes a convenience executable/ready status, it must be a **derived** property over both axes and must not be projected back into `parent_state`.

Exact execution readiness requires:

1. `parent_state in {verified-exact, verified-compatible}`;
2. every release dependency result is `pass`;
3. bundle state is either `not-required` for a no-bundle release or `verified` with the exact required digest;
4. release/variant/source-contract inputs are current and valid.

The report may name the four-state field `parent_state` or `parent_compatibility_state`; it must not call it an overall execution status. The resolver-facing projection uses the exact I-006 field name `parent_state`.

## Research wording reconciliation

The I-007 research document says `verified-exact` / `verified-compatible` require exact ontology-bundle closure. Interpret that as a statement about a **fully executable runtime report**, not as permission to overload I-006's `parent_state` field. This amendment narrows the implementation to the already-frozen I-006 public contract and preserves the more precise diagnostics.

No source semantic decision changes: a report is executable only when bundle closure is exact. The correction only prevents bundle state from being collapsed into the parent compatibility axis.

## RED additions / corrections

Add these permanent tests to the I-007 RED matrix:

1. exact parent + all dependency pass + required bundle unavailable produces `parent_state="verified-exact"` and `ontology_bundle_state="unavailable"`; I-006 rejects it specifically as bundle unavailable, not parent unverified;
2. changed compatible parent + all dependency pass + required bundle unavailable preserves `parent_state="verified-compatible"`;
3. bundle availability changing from unavailable to exact verified does not change dependency results or parent state, but does change prerequisite/report fingerprint and execution readiness;
4. a dependency unknown plus exact bundle remains `parent_state="unverified"` regardless of bundle success;
5. a dependency fail plus exact bundle remains `parent_state="incompatible"`;
6. an explicitly wrong active bundle digest is stale runtime input and does not reclassify the observed parent as incompatible;
7. report serialization/documentation never describes the four P-001 parent states as sufficient execution authority by themselves.

## Plan-review conclusion

With this correction, the plan preserves I-006's diagnostic and trust model: parent/dependency compatibility can be cached/reasoned about independently from local ontology-bundle installation, while actual execution still requires both axes to be satisfied. No duplicate status machine or resolver policy is introduced.