# I-008 plan review amendment — harden real Context-Fabric node IDs and pre-resolution IR access

**Issue:** #143  
**Plan under review:** `docs/plans/I-008-exact-loaded-execution-plan.md`  
**Review baseline:** `df8283534cbb16b8ecfb4d140fdfe57f97140e5f`

## Finding 1 — exact `int` result validation is incompatible with Context-Fabric mmap output

The initial plan required `type(node) is int`. Current Context-Fabric 0.5.7 `StringPool.filter_by_value()` explicitly returns `NDArray[np.int64]`, and `NodeFeature.s()` sorts those matches and returns them as a tuple. A real `.cfm`-backed feature can therefore expose NumPy integer scalars even though they are valid node IDs.

### Amendment

Normalize result-node IDs with the Python integer-index protocol rather than exact type equality:

1. reject `bool` explicitly;
2. call `operator.index(node)`;
3. require the normalized Python integer to be `> 0`;
4. reject values for which `operator.index()` fails;
5. reject duplicate normalized integer IDs;
6. store only normalized built-in Python `int` values in `ExactCorpusExecution.nodes`.

This accepts `int` and `numpy.integer` without importing NumPy, while still rejecting floats, strings, booleans and arbitrary numeric coercion.

Add RED controls for Python `int`, a minimal custom `__index__` integer-like object, boolean rejection, non-indexable numeric rejection, and duplicate IDs that collide after normalization.

## Finding 2 — empty-result test conflicts with the production Noun dependency

The release Noun profile uses `native-value-present(sp=subs)`. If `subs` is absent, I-007 correctly produces a dependency failure and I-006 blocks execution. Therefore a test that removes all `subs` rows from that same profile cannot reach native execution and cannot demonstrate executor empty-result semantics.

### Amendment

Keep empty-result semantics, but test it with a controlled I-008 fixture whose mapping remains `value-predicate sp=subs` while the profile prerequisite is `feature-present(word, sp)` rather than `native-value-present(subs)`. The loaded feature exists, I-007 authorizes the capability contract, and the actual selected value may have zero matches.

Production v0.1 Noun remains stricter and is expected to have at least one `subs` value because its dependency asserts that fact.

## Finding 3 — variant selection touches compiled IR before I-006 validates the whole IR

The initial plan proposed scanning `ir.variants` for `variant.key.corpus_id` before calling `semantic_resolve()`. A forged/malformed `CompiledSemanticIR` can therefore raise arbitrary `AttributeError`/shape errors during executor-side selection instead of reaching I-006's fail-closed IR validator.

### Amendment

Before variant selection:

- require `type(ir) is CompiledSemanticIR`, matching I-006's public boundary;
- require `type(ir.variants) is tuple`;
- for every row touched during selection require `type(row) is BundleVariantIR` and `type(row.key) is BundleVariantKey` before reading `corpus_id`;
- require `type(row.key.corpus_id) is str and row.key.corpus_id`;
- any failure becomes `ExactExecutionError(category="invalid_compiled_ir")` before runtime observation/native result access.

Do not duplicate deeper I-005/I-006 validation. The selected variant is subsequently validated by I-007, and the complete IR is subsequently revalidated by I-006 `semantic_resolve()` before execution.

Add RED cases for malformed `ir.variants`, malformed variant rows and malformed variant keys, asserting deterministic executor failure and zero result-selector calls.

## Final plan disposition

With these amendments the plan is implementation-ready. The RED matrix must incorporate all three corrections before production code:

- integer-like Context-Fabric node normalization without a NumPy dependency;
- a semantically valid feature-present empty-result fixture;
- guarded minimal IR preselection before I-007/I-006 take over full validation.

No broader execution shape or dependency is admitted by this review.