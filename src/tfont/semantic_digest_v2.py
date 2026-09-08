from __future__ import annotations

import hashlib
from typing import Any

from .digests import DigestError, DigestProblem, canonical_json_bytes

MAPPING_SEMANTIC_ALGORITHM_V2 = "tfont-mapping-semantic-sha256-v2"
PROJECTION_SEMANTIC_ALGORITHM_V1 = "tfont-projection-semantic-sha256-v1"

_AUDIT_ONLY_TOP_LEVEL = {
    "review",
    "mapping_semantic_digest",
    "rationale",
    "introduced_in",
    "changed_in",
}
_AUDIT_ONLY_NESTED = {
    "review",
    "projection_semantic_digest",
}
_SET_LIKE_LIST_FIELDS = {
    "native_dependencies",
    "profiles",
    "capabilities",
    "evidence",
    "projections",
    "ambiguous_candidates",
    "external_references",
    "losses",
}


def _fail(message: str) -> None:
    raise DigestError(DigestProblem(category="projection_error", message=message))


def _canonical_sort(items: list[Any]) -> list[Any]:
    encoded = [(canonical_json_bytes(item), item) for item in items]
    encoded.sort(key=lambda pair: pair[0])
    return [item for _, item in encoded]


def _project(value: Any, *, top_level: bool = False, field: str | None = None) -> Any:
    if type(value) is dict:
        excluded = _AUDIT_ONLY_TOP_LEVEL if top_level else _AUDIT_ONLY_NESTED
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key in excluded:
                continue
            result[key] = _project(item, field=key)
        return result
    if type(value) is list:
        projected = [_project(item) for item in value]
        if field in _SET_LIKE_LIST_FIELDS:
            return _canonical_sort(projected)
        return projected
    return value


def mapping_semantic_projection_v2(mapping: dict[str, Any]) -> dict[str, Any]:
    if type(mapping) is not dict:
        _fail("mapping semantic projection requires an exact object")
    projection = _project(mapping, top_level=True)
    canonical_json_bytes(projection)
    return projection


def mapping_semantic_digest_v2(mapping: dict[str, Any]) -> str:
    payload = canonical_json_bytes(mapping_semantic_projection_v2(mapping))
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def projection_semantic_projection_v1(projection: dict[str, Any]) -> dict[str, Any]:
    if type(projection) is not dict:
        _fail("projection semantic projection requires an exact object")
    result = _project(projection, top_level=False)
    if type(result) is not dict:
        _fail("projection semantic projection requires an exact object")
    canonical_json_bytes(result)
    return result


def projection_semantic_digest_v1(projection: dict[str, Any]) -> str:
    payload = canonical_json_bytes(projection_semantic_projection_v1(projection))
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"
