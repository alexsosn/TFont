from __future__ import annotations

import subprocess
from pathlib import Path

PATH = "src/tfont/schemas/mapping.schema.json"
text = subprocess.check_output(
    ["git", "show", f"origin/main:{PATH}"], text=True
)

text = text.replace(
    '        "closed_values": {\n          "type": "array",\n          "minItems": 1,\n          "uniqueItems": true,\n          "items": {"$ref": "#/$defs/jsonScalar"}\n        },\n        "edge":',
    '        "closed_values": {\n          "type": "array",\n          "minItems": 1,\n          "uniqueItems": true,\n          "items": {"$ref": "#/$defs/jsonScalar"}\n        },\n        "values": {\n          "type": "array",\n          "minItems": 1,\n          "uniqueItems": true,\n          "items": {"$ref": "#/$defs/jsonScalar"}\n        },\n        "edge":',
    1,
)
text = text.replace(
    '"enum": ["membership", "value-predicate", "edge-path", "identity-key", "inspection-only"]',
    '"enum": ["membership", "value-predicate", "value-set-predicate", "edge-path", "identity-key", "inspection-only"]',
    1,
)
needle = '''      },\n      "additionalProperties": false\n    },\n    "evidenceBinding":'''
replacement = '''      },\n      "additionalProperties": false,\n      "allOf": [\n        {\n          "if": {"properties": {"execution_shape": {"const": "value-predicate"}}, "required": ["execution_shape"]},\n          "then": {\n            "required": ["component_id", "node_type", "feature", "value"],\n            "not": {"anyOf": [\n              {"required": ["values"]}, {"required": ["closed_values"]}, {"required": ["edge"]},\n              {"required": ["direction"]}, {"required": ["steps"]}, {"required": ["interpretation"]}\n            ]}\n          }\n        },\n        {\n          "if": {"properties": {"execution_shape": {"const": "value-set-predicate"}}, "required": ["execution_shape"]},\n          "then": {\n            "required": ["component_id", "node_type", "feature", "values"],\n            "not": {"anyOf": [\n              {"required": ["value"]}, {"required": ["closed_values"]}, {"required": ["edge"]},\n              {"required": ["direction"]}, {"required": ["steps"]}, {"required": ["interpretation"]}\n            ]}\n          }\n        },\n        {\n          "if": {"required": ["values"]},\n          "then": {\n            "required": ["execution_shape"],\n            "properties": {"execution_shape": {"const": "value-set-predicate"}}\n          }\n        }\n      ]\n    },\n    "evidenceBinding":'''
if needle not in text:
    raise SystemExit("nativeBinding insertion point not found")
text = text.replace(needle, replacement, 1)

if text.count('"value-set-predicate"') != 3:
    raise SystemExit("unexpected value-set-predicate count")
Path(PATH).write_text(text, encoding="utf-8")
print("restored main schema formatting with minimal I-010 edits")
