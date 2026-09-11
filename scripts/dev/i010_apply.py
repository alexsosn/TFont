from __future__ import annotations

import json
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# Schema: selected values are a finite query subset, distinct from closed_values.
schema_path = Path("src/tfont/schemas/mapping.schema.json")
schema = json.loads(schema_path.read_text(encoding="utf-8"))
binding = schema["$defs"]["nativeBinding"]
binding["properties"]["values"] = {
    "type": "array",
    "minItems": 1,
    "uniqueItems": True,
    "items": {"$ref": "#/$defs/jsonScalar"},
}
shapes = binding["properties"]["execution_shape"]["enum"]
if "value-set-predicate" not in shapes:
    shapes.insert(shapes.index("value-predicate") + 1, "value-set-predicate")
forbidden_set = [
    {"required": [field]}
    for field in ("value", "closed_values", "edge", "direction", "steps", "interpretation")
]
forbidden_scalar = [
    {"required": [field]}
    for field in ("values", "closed_values", "edge", "direction", "steps", "interpretation")
]
binding["allOf"] = [
    {
        "if": {
            "properties": {"execution_shape": {"const": "value-predicate"}},
            "required": ["execution_shape"],
        },
        "then": {
            "required": ["component_id", "node_type", "feature", "value"],
            "not": {"anyOf": forbidden_scalar},
        },
    },
    {
        "if": {
            "properties": {"execution_shape": {"const": "value-set-predicate"}},
            "required": ["execution_shape"],
        },
        "then": {
            "required": ["component_id", "node_type", "feature", "values"],
            "not": {"anyOf": forbidden_set},
        },
    },
    {
        "if": {"required": ["values"]},
        "then": {
            "required": ["execution_shape"],
            "properties": {"execution_shape": {"const": "value-set-predicate"}},
        },
    },
]
schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


# Semantic digests: values is semantically set-like.
replace_once(
    "src/tfont/semantic_digest_v2.py",
    '    "losses",\n}',
    '    "losses",\n    "values",\n}',
)


# IR: retain a canonical finite set and make native-binding identity order-invariant.
replace_once(
    "src/tfont/semantic_ir.py",
    "    interpretation: str | None\n    execution_shape: str | None\n",
    "    interpretation: str | None\n    execution_shape: str | None\n    values: tuple[str | int | float | bool | None, ...] | None = None\n",
)
replace_once(
    "src/tfont/semantic_ir.py",
    '''def native_binding_identity(binding: dict[str, Any]) -> str:\n    if type(binding) is not dict:\n        raise TypeError("native binding must be an exact dict")\n    payload = canonical_json_bytes(binding)\n    return "sha256:" + hashlib.sha256(payload).hexdigest()\n''',
    '''def native_binding_identity(binding: dict[str, Any]) -> str:\n    if type(binding) is not dict:\n        raise TypeError("native binding must be an exact dict")\n    normalized = dict(binding)\n    selected_values = normalized.get("values")\n    if type(selected_values) is list:\n        normalized["values"] = sorted(selected_values, key=canonical_json_bytes)\n    payload = canonical_json_bytes(normalized)\n    return "sha256:" + hashlib.sha256(payload).hexdigest()\n''',
)
replace_once(
    "src/tfont/semantic_ir.py",
    '''    closed_value = binding.get("closed_values")\n    closed_values = tuple(closed_value) if type(closed_value) is list else None\n    return NativeBindingIR(\n''',
    '''    closed_value = binding.get("closed_values")\n    closed_values = tuple(closed_value) if type(closed_value) is list else None\n    selected_value = binding.get("values")\n    selected_values = (\n        tuple(sorted(selected_value, key=canonical_json_bytes))\n        if type(selected_value) is list\n        else None\n    )\n    return NativeBindingIR(\n''',
)
replace_once(
    "src/tfont/semantic_ir.py",
    '''        interpretation=binding.get("interpretation"),\n        execution_shape=binding.get("execution_shape"),\n    )\n''',
    '''        interpretation=binding.get("interpretation"),\n        execution_shape=binding.get("execution_shape"),\n        values=selected_values,\n    )\n''',
)


# Resolver: reconstruct canonical set bindings and reject fabricated mixed/unsorted IR.
replace_once(
    "src/tfont/semantic_resolver.py",
    '''    if binding.value_present:\n        result["value"] = binding.value\n    if binding.closed_values is not None:\n''',
    '''    if binding.value_present:\n        result["value"] = binding.value\n    if binding.values is not None:\n        if type(binding.values) is not tuple or not binding.values:\n            _fail("invalid_compiled_ir", "native binding values must be a non-empty exact tuple")\n        encoded_values: list[bytes] = []\n        for value in binding.values:\n            if not (value is None or type(value) in {str, int, float, bool}):\n                _fail("invalid_compiled_ir", "native binding values must contain JSON scalars")\n            try:\n                encoded_values.append(canonical_json_bytes(value))\n            except Exception:\n                _fail("invalid_compiled_ir", "native binding values contain a non-canonical JSON scalar")\n        if len(set(encoded_values)) != len(encoded_values):\n            _fail("invalid_compiled_ir", "native binding values contain canonical duplicates")\n        if tuple(encoded_values) != tuple(sorted(encoded_values)):\n            _fail("invalid_compiled_ir", "native binding values are not canonically ordered")\n        result["values"] = list(binding.values)\n    if binding.closed_values is not None:\n''',
)
replace_once(
    "src/tfont/semantic_resolver.py",
    '''        result["steps"] = steps\n    return result\n\n\ndef _has_duplicate_ids''',
    '''        result["steps"] = steps\n    if binding.execution_shape == "value-set-predicate":\n        valid = (\n            type(binding.component_id) is str\n            and bool(binding.component_id)\n            and type(binding.node_type) is str\n            and bool(binding.node_type)\n            and type(binding.feature) is str\n            and bool(binding.feature)\n            and binding.value_present is False\n            and binding.value is None\n            and binding.values is not None\n            and binding.closed_values is None\n            and binding.edge is None\n            and binding.direction is None\n            and binding.steps is None\n            and binding.interpretation is None\n        )\n        if not valid:\n            _fail("invalid_compiled_ir", "value-set-predicate binding has an invalid mixed shape")\n    if binding.execution_shape == "value-predicate" and binding.values is not None:\n        _fail("invalid_compiled_ir", "value-predicate binding cannot carry selected values")\n    return result\n\n\ndef _has_duplicate_ids''',
)


# Executor: keep scalar behavior unchanged and add one finite-set primitive.
replace_once(
    "src/tfont/semantic_execution.py",
    "from typing import Any\n\nfrom .runtime_prerequisites",
    "from typing import Any\n\nfrom .digests import canonical_json_bytes\nfrom .runtime_prerequisites",
)
replace_once(
    "src/tfont/semantic_execution.py",
    '''        and binding.execution_shape == "value-predicate"\n        and binding.closed_values is None\n''',
    '''        and binding.execution_shape == "value-predicate"\n        and binding.values is None\n        and binding.closed_values is None\n''',
)
replace_once(
    "src/tfont/semantic_execution.py",
    '''    return binding\n\n\ndef _loaded_feature_api''',
    '''    return binding\n\n\ndef _validate_value_set_predicate(plan: ExactNativePlan) -> NativeBindingIR:\n    binding = plan.native_execution_binding\n    values_valid = type(binding) is NativeBindingIR and type(binding.values) is tuple and bool(binding.values)\n    encoded_values: list[bytes] = []\n    if values_valid:\n        for value in binding.values or ():\n            if not (value is None or type(value) in {str, int, float, bool}):\n                values_valid = False\n                break\n            try:\n                encoded_values.append(canonical_json_bytes(value))\n            except Exception:\n                values_valid = False\n                break\n        if values_valid:\n            values_valid = (\n                len(set(encoded_values)) == len(encoded_values)\n                and tuple(encoded_values) == tuple(sorted(encoded_values))\n            )\n    valid = (\n        type(binding) is NativeBindingIR\n        and _nonempty_string(binding.component_id)\n        and _nonempty_string(binding.node_type)\n        and _nonempty_string(binding.feature)\n        and binding.value_present is False\n        and binding.value is None\n        and values_valid\n        and binding.execution_shape == "value-set-predicate"\n        and binding.closed_values is None\n        and binding.edge is None\n        and binding.direction is None\n        and binding.steps is None\n        and binding.interpretation is None\n    )\n    if not valid:\n        _fail(\n            "unsupported_native_binding",\n            "v0.1 value-set execution requires one feature and a canonical finite JSON-scalar value set",\n            corpus_id=plan.corpus_id,\n            component_id=getattr(binding, "component_id", None),\n        )\n    return binding\n\n\ndef _loaded_feature_api''',
)
replace_once(
    "src/tfont/semantic_execution.py",
    '''        if node_type == binding.node_type:\n            result.append(node)\n    return tuple(result)\n\n\ndef execute_exact_semantic(\n''',
    '''        if node_type == binding.node_type:\n            result.append(node)\n    return tuple(result)\n\n\ndef _execute_value_set_predicate(\n    plan: ExactNativePlan,\n    component: LoadedComponentContext,\n) -> tuple[int, ...]:\n    binding = _validate_value_set_predicate(plan)\n    feature_selector, otype_lookup = _loaded_feature_api(\n        component.api,\n        binding,\n        corpus_id=plan.corpus_id,\n    )\n    selected_nodes: set[int] = set()\n    for selected_value in binding.values or ():\n        try:\n            raw_nodes = feature_selector(selected_value)\n        except Exception as error:\n            raise ExactExecutionError(\n                ExactExecutionProblem(\n                    "loaded_api_unavailable",\n                    "loaded feature selector failed",\n                    corpus_id=plan.corpus_id,\n                    component_id=binding.component_id,\n                )\n            ) from error\n        nodes = _normalize_result_nodes(\n            raw_nodes,\n            corpus_id=plan.corpus_id,\n            component_id=binding.component_id or "",\n        )\n        selected_nodes.update(nodes)\n\n    result: list[int] = []\n    for node in sorted(selected_nodes):\n        try:\n            node_type = otype_lookup(node)\n        except Exception as error:\n            raise ExactExecutionError(\n                ExactExecutionProblem(\n                    "loaded_api_unavailable",\n                    "loaded node-type lookup failed",\n                    corpus_id=plan.corpus_id,\n                    component_id=binding.component_id,\n                )\n            ) from error\n        if type(node_type) is not str or not node_type:\n            _fail(\n                "loaded_api_unavailable",\n                "loaded node-type lookup returned a malformed value",\n                corpus_id=plan.corpus_id,\n                component_id=binding.component_id,\n            )\n        if node_type == binding.node_type:\n            result.append(node)\n    return tuple(result)\n\n\ndef execute_exact_semantic(\n''',
)
replace_once(
    "src/tfont/semantic_execution.py",
    '''        binding = _validate_value_predicate(plan)\n        components = _components(normalized_contexts[plan.corpus_id])\n''',
    '''        binding = plan.native_execution_binding\n        if type(binding) is not NativeBindingIR:\n            _fail(\n                "unsupported_native_binding",\n                "fresh resolver plan has an invalid native binding",\n                corpus_id=plan.corpus_id,\n            )\n        if binding.execution_shape == "value-predicate":\n            binding = _validate_value_predicate(plan)\n        elif binding.execution_shape == "value-set-predicate":\n            binding = _validate_value_set_predicate(plan)\n        else:\n            _fail(\n                "unsupported_native_binding",\n                "v0.1 execution supports only scalar or finite-set feature predicates",\n                corpus_id=plan.corpus_id,\n                component_id=binding.component_id,\n            )\n        components = _components(normalized_contexts[plan.corpus_id])\n''',
)
replace_once(
    "src/tfont/semantic_execution.py",
    '''        nodes = _execute_value_predicate(plan, component)\n        executions.append(\n''',
    '''        if binding.execution_shape == "value-predicate":\n            nodes = _execute_value_predicate(plan, component)\n        else:\n            nodes = _execute_value_set_predicate(plan, component)\n        executions.append(\n''',
)

print("I-010 production patch applied")
