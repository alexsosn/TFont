from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tfont.source_validation import validate_source  # noqa: E402

SCHEMA_ROOT = ROOT / "schemas"


def reviewed_record() -> dict:
    return {
        "review_id": "review:with-audit-fields",
        "status": "reviewed",
        "reviewed_mapping_digest": "sha256:mapping",
        "reviewer_id": "reviewer:test",
        "reviewed_at": "2026-09-05T21:00:00Z",
        "review_source": "offline:test",
        "review_method": "independent-skeptical",
        "notes": ["audit note"],
        "evidence": ["review-evidence:test"],
    }


def mapping_with_review(review: dict) -> dict:
    return {
        "schema_version": 1,
        "mappings": [
            {
                "mapping_id": "mapping:test",
                "profile_id": "tfont-test",
                "native_selector": {
                    "kind": "feature-value",
                    "component_id": "test-tf",
                    "feature": "gn",
                    "value": "m",
                    "extent": "semantic",
                },
                "native_dependencies": ["dep:test"],
                "external_target": "https://example.org/term",
                "candidate_projections": [],
                "assessment": "exact",
                "publication_relation": None,
                "applicability": {"node_type": "word"},
                "ontology_lock": "lock:test",
                "evidence": [
                    {
                        "evidence_id": "evidence:test",
                        "content_digest": "sha256:evidence",
                    }
                ],
                "review": review,
                "mapping_semantic_digest": "sha256:mapping",
                "rationale": "fixture",
            }
        ],
    }


class ReviewSchemaConsistencyTests(unittest.TestCase):
    def test_standalone_review_shape_is_valid_when_embedded_in_mapping(self):
        review = reviewed_record()
        validate_source(review, "review", schema_root=SCHEMA_ROOT)
        validate_source(mapping_with_review(review), "mapping", schema_root=SCHEMA_ROOT)


if __name__ == "__main__":
    unittest.main()
