from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tfont.source_validation import SCHEMA_FILES  # noqa: E402


def evidence_binding(evidence_id: str = "evidence:test") -> dict:
    return {"evidence_id": evidence_id, "content_digest": "sha256:evidence"}


def review_record() -> dict:
    return {
        "review_id": "review:test",
        "status": "reviewed",
        "reviewed_mapping_digest": "sha256:mapping",
        "reviewer_id": "reviewer:test",
        "reviewed_at": "2026-09-05T21:00:00Z",
        "review_source": "offline:test",
        "review_method": "independent-skeptical",
    }


def exact_mapping() -> dict:
    return {
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
        "ontology_lock": "olia-test",
        "evidence": [evidence_binding()],
        "review": review_record(),
        "mapping_semantic_digest": "sha256:mapping",
        "rationale": "fixture",
    }


def minimal_valid_instances() -> dict[str, dict]:
    return {
        "profile": {
            "schema_version": 1,
            "profile_id": "tfont-test",
            "profile_version": "0.1.0",
            "semantic_domains": ["morphology"],
            "parent_component_manifest": "parent/expected-components.json",
            "required_components": ["test-tf"],
            "ontology_locks": ["olia-test"],
            "mapping_sources": ["mappings/test.yaml"],
            "dependency_contract_version": 1,
            "minimum_tfont_runtime": "0.1.0",
            "license": "CC-BY-4.0",
        },
        "parent-component-manifest": {
            "algorithm": "tfont-parent-components-sha256-v1",
            "components": [
                {
                    "component_id": "test-tf",
                    "kind": "tf-payload",
                    "identity_algorithm": "tfont-tf-files-sha256-v1",
                    "content_digest": "sha256:test",
                }
            ],
        },
        "ontology-lock": {
            "lock_id": "olia-test",
            "ontology_id": "olia",
            "support_tier": "core",
            "term_namespace": "https://example.org/olia#",
            "release": "test-release",
            "source_uri": "https://example.org/olia.ttl",
            "content_digest": "sha256:ontology",
            "license": "CC-BY-4.0",
            "snapshot_artifact": "ontology/olia.ttl",
            "terms_used": ["https://example.org/olia#Noun"],
        },
        "evidence": {
            "evidence_id": "evidence:test",
            "kind": "native-doc",
            "source_uri": "https://example.org/native-doc",
            "content_mode": "external-payload",
            "content_digest": "sha256:evidence",
        },
        "review": review_record(),
        "mapping": {"schema_version": 1, "mappings": [exact_mapping()]},
        "compatibility-report": {
            "compatibility_report_id": "tfont-compatibility-sha256-v1:test",
            "report_digest": "sha256:report",
            "profile_id": "tfont-test",
            "profile_version": "0.1.0",
            "profile_semantic_digest": "sha256:profile",
            "expected_parent_manifest_digest": "sha256:expected",
            "observed_parent_manifest_digest": "sha256:observed",
            "state": "verified-compatible",
            "changed_components": ["test-sidecar"],
            "dependency_results": [
                {
                    "dependency_id": "dep:test",
                    "component_id": "test-sidecar",
                    "result": "pass",
                    "evaluator_rule_version": "1",
                }
            ],
            "evaluator_version": "1",
            "incomplete_reasons": [],
            "failure_reasons": [],
        },
    }


class WheelSchemaResourceTests(unittest.TestCase):
    def test_non_editable_wheel_contains_and_uses_all_structural_schemas(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dist = tmp_path / "dist"
            target = tmp_path / "target"
            outside = tmp_path / "outside"
            dist.mkdir()
            target.mkdir()
            outside.mkdir()

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--wheel",
                    "--outdir",
                    str(dist),
                    str(ROOT),
                ],
                check=True,
                cwd=outside,
            )
            wheels = list(dist.glob("*.whl"))
            self.assertEqual(len(wheels), 1, wheels)
            wheel = wheels[0]

            expected_resources = {
                f"tfont/schemas/{filename}" for filename in SCHEMA_FILES.values()
            }
            with zipfile.ZipFile(wheel) as archive:
                wheel_names = set(archive.namelist())
            self.assertTrue(
                expected_resources <= wheel_names,
                f"missing wheel schema resources: {sorted(expected_resources - wheel_names)}",
            )

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--target",
                    str(target),
                    str(wheel),
                ],
                check=True,
                cwd=outside,
            )

            fixtures = tmp_path / "fixtures.json"
            fixtures.write_text(
                json.dumps(minimal_valid_instances()),
                encoding="utf-8",
            )

            child = """
import json
import sys
from pathlib import Path

import tfont
from tfont.source_validation import validate_source

target = Path(sys.argv[1]).resolve()
fixtures = Path(sys.argv[2])
package_file = Path(tfont.__file__).resolve()
if not package_file.is_relative_to(target):
    raise AssertionError(f"imported TFont outside wheel target: {package_file} not under {target}")

for schema_name, instance in json.loads(fixtures.read_text(encoding="utf-8")).items():
    validate_source(instance, schema_name)
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = str(target)
            env["PYTHONNOUSERSITE"] = "1"
            subprocess.run(
                [sys.executable, "-c", child, str(target), str(fixtures)],
                check=True,
                cwd=outside,
                env=env,
            )


if __name__ == "__main__":
    unittest.main()
