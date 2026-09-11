# I-008 research review amendment — bind observation and execution to one loaded component set

**Issue:** #143  
**Research under review:** `docs/research/I-008-exact-loaded-execution.md`  
**Review baseline:** `8a76e9357d2fa8a2d252698af96befe0d081beaa`

## Independent adversarial finding

The initial research said that each corpus runtime context should contain an I-007 `RuntimeObservation` plus the loaded API used for execution. That is still too permissive for the R-019 trust goal: a host could accidentally construct the observation from one loaded component/API and execute the freshly authorized plan against a different API object supplied beside it.

The execution boundary should make that mismatch unrepresentable in the normal v0.1 path.

## Amended context contract

The public executor should **not** accept an arbitrary pre-built `RuntimeObservation` beside an unrelated execution API.

Instead, each per-corpus execution context should own one normalized component table equivalent to:

```text
corpus_id
parent_manifest_digest
components[
  component_id -> (content_digest, already_loaded_api)
]
extent_interpretations
active_ontology_bundle_digest
```

The executor constructs `LoadedTFObservation` internally from that same component table and later resolves `plan.native_execution_binding.component_id` back into the same table for result execution.

Consequences:

- prerequisite observation and native execution necessarily use the same loaded API object for a component;
- component identity/digest and component API stay coupled;
- missing plan component fails closed before result access;
- an arbitrary external `RuntimePrerequisiteState` / `RuntimeEvaluationReport` is not accepted as execution authority;
- a caller may still choose which already-loaded corpus context is supplied, but cannot separately swap the observation API and execution API within the supported entry point.

This remains a same-process state-based trust boundary; Python object identity is not added to semantic fingerprints.

## Context-Fabric API compatibility recheck

The review also checked the I-007 assumptions against current Context-Fabric rather than only against Text-Fabric-compatible fixtures.

At Context-Fabric commit `3a38ca80e617d872ce1664e0f0740486d0e7e8ac`:

- `Api.Fall()` exists and returns loaded node feature names;
- `Api.Eall()` is used analogously by Context-Fabric's own MCP/resource code;
- `NodeFeature.v(node)` returns a value or `None`;
- `NodeFeature.s(value)` returns nodes sorted in canonical order;
- `OtypeFeature.v(node)` returns node type;
- `OtypeFeature.s(type)` returns nodes in canonical order.

Therefore the merged I-007 `LoadedTFObservation` adapter and the proposed I-008 read-only value-predicate execution surface match the real Context-Fabric 0.5.7 loaded API. No compatibility shim or Context-Fabric import is needed for the first slice.

## Additional fail-closed requirement

The plan must pin a component/API equality test: evaluation should be instrumented with one API object and execution with a deliberately different lookalike API. The production public entry point must provide no way for the second object to be substituted for the component after I-007 evaluation.

The plan should also test malformed component tables, duplicate component IDs if an iterable source form is accepted, and missing component IDs referenced by the freshly resolved plan.

## Review disposition

With this amendment, the research direction is sound and remains narrower than a generic Context-Fabric adapter:

```text
one normalized loaded component table
        ├─> internally constructed I-007 observation
        └─> native execution API lookup
                    ↓
          same component / same API
```

No further architecture research is required before the I-008 implementation plan. The plan must incorporate this amended context boundary explicitly.