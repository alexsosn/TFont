from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
FULL_COMMAND = "python -m unittest discover -s tests -v"


class FullSuiteWorkflowContractTests(unittest.TestCase):
    def workflow_texts(self) -> dict[str, str]:
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(WORKFLOW_DIR.glob("*.yml"))
        }

    def test_exactly_one_workflow_owns_full_repository_command(self):
        texts = self.workflow_texts()
        owners = sorted(name for name, text in texts.items() if FULL_COMMAND in text)
        self.assertEqual(owners, ["full-suite.yml"])
        self.assertEqual(texts["full-suite.yml"].count(FULL_COMMAND), 1)

    def test_authoritative_workflow_preserves_cross_version_and_trigger_contract(self):
        text = (WORKFLOW_DIR / "full-suite.yml").read_text(encoding="utf-8")
        required_tokens = (
            "push:",
            "pull_request:",
            "workflow_dispatch:",
            "pyproject.toml",
            '"src/**"',
            '"tests/**"',
            '".github/workflows/**"',
            'python-version: ["3.10", "3.12"]',
            "fail-fast: false",
            "github.event.pull_request.head.sha || github.sha",
            "cancel-in-progress: true",
            "python -m pip install build",
            FULL_COMMAND,
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_focused_workflows_keep_their_distinct_contracts(self):
        texts = self.workflow_texts()
        required_by_workflow = {
            "d001-readme-status.yml": ("tests.docs.test_readme_status",),
            "f002-wheel-schema-resources.yml": (
                "tests.packaging.test_wheel_schema_resources",
                "discover -s tests/i001",
            ),
            "f003-digest-projection-key-errors.yml": (
                "tests.i002.test_projection_key_error_boundary",
                "discover -s tests/i002",
            ),
            "f004-source-bundle-diagnostic-paths.yml": (
                "tests.i002.test_source_bundle_diagnostic_paths",
                "discover -s tests/i002",
            ),
            "f005-utf16-diagnostic-paths.yml": (
                "tests.i002.test_utf16_diagnostic_paths",
                "discover -s tests/i002",
            ),
            "i001-validation.yml": ("discover -s tests/i001",),
            "i002-validation.yml": ("discover -s tests/i002",),
            "i003-validation.yml": ("discover -s tests/i003",),
            "f006-deep-source-nesting.yml": (
                "tests.i001.test_deep_source_nesting",
                "discover -s tests/i001",
            ),
        }
        for workflow, tokens in required_by_workflow.items():
            if workflow not in texts:
                continue
            for token in tokens:
                with self.subTest(workflow=workflow, token=token):
                    self.assertIn(token, texts[workflow])


if __name__ == "__main__":
    unittest.main()
