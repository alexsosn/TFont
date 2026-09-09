from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts" / "check_f_series_ownership.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("_f024_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load checker from {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def research_doc(*header_lines: str, feature: str = "F-900") -> str:
    return "\n".join([f"# {feature} fixture", "", *header_lines, "", "## Body", ""])


def write_research(root: Path, *, feature: str = "F-900", issue: int = 900, name: str = "authority") -> Path:
    path = root / "docs" / "research" / f"{feature}-{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(research_doc(f"**Issue:** #{issue}", feature=feature), encoding="utf-8")
    return path


def write_plan(root: Path, *, feature: str = "F-900", owner: str = "**Issue:** #900", name: str = "plan") -> Path:
    path = root / "docs" / "plans" / f"{feature}-{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(research_doc(owner, feature=feature), encoding="utf-8")
    return path


def write_workflow(root: Path, *, feature: str = "F-900", owner: str = "# Issue: #900", name: str = "fixture") -> Path:
    digits = feature.removeprefix("F-")
    path = root / ".github" / "workflows" / f"f{digits}-{name}.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{owner}\nname: fixture\n", encoding="utf-8")
    return path


def write_test_package(root: Path, *, feature: str = "F-900", sidecar: bool = True) -> tuple[Path, Path]:
    digits = feature.removeprefix("F-")
    package = root / "tests" / f"f{digits}"
    package.mkdir(parents=True, exist_ok=True)
    carrier = package / "issue-owner.txt"
    if sidecar:
        carrier.write_text("Issue: #900\n", encoding="utf-8")
    return package, carrier


def selective_failure(checker, method: str, target: Path, exc: BaseException):
    original = getattr(checker.Path, method)

    def wrapped(path, *args, **kwargs):
        if path == target:
            raise exc
        return original(path, *args, **kwargs)

    return mock.patch.object(checker.Path, method, wrapped)


class NamespaceScanFailureTests(unittest.TestCase):
    maxDiff = None

    def assert_check(self, root: Path, expected: list[str]) -> None:
        checker = load_checker()
        self.assertEqual(checker.check_repository(root), expected)

    def test_research_namespace_classification_oserror_is_global_scan_error(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            research = root / "docs" / "research"
            research.mkdir(parents=True)
            write_workflow(root, feature="F-999", owner="# Issue: #999", name="orphan")
            with selective_failure(checker, "is_dir", research, PermissionError("denied")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, ["scan_error: docs/research: PermissionError"])

    def test_research_namespace_enumeration_oserror_is_global_scan_error(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root, feature="F-999", owner="# Issue: #999", name="orphan")
            research = root / "docs" / "research"
            with selective_failure(checker, "iterdir", research, OSError("scan failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, ["scan_error: docs/research: OSError"])

    def test_research_namespace_enumeration_valueerror_is_global_scan_error(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            research = root / "docs" / "research"
            with selective_failure(checker, "iterdir", research, ValueError("invalid path")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, ["scan_error: docs/research: ValueError"])

    def test_matching_research_entry_classification_failure_is_global(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            research_path = write_research(root)
            write_workflow(root, feature="F-999", owner="# Issue: #999", name="orphan")
            with selective_failure(checker, "is_file", research_path, OSError("stat failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            ["scan_error: docs/research/F-900-authority.md: OSError"],
        )

    def test_plan_enumeration_failure_is_local_and_workflow_error_remains_visible(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root)
            write_workflow(root, owner="# Issue: #abc", name="malformed")
            plans = root / "docs" / "plans"
            with selective_failure(checker, "iterdir", plans, OSError("scan failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            [
                "malformed_owner: .github/workflows/f900-malformed.yml:1: '# Issue: #abc'",
                "scan_error: docs/plans: OSError",
            ],
        )

    def test_matching_plan_entry_classification_failure_is_local(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            plan = write_plan(root)
            write_workflow(root, owner="# Issue: #abc", name="malformed")
            with selective_failure(checker, "is_file", plan, OSError("stat failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            [
                "malformed_owner: .github/workflows/f900-malformed.yml:1: '# Issue: #abc'",
                "scan_error: docs/plans/F-900-plan.md: OSError",
            ],
        )

    def test_workflow_enumeration_failure_is_local_and_test_error_remains_visible(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root)
            _package, sidecar = write_test_package(root, sidecar=False)
            workflows = root / ".github" / "workflows"
            with selective_failure(checker, "iterdir", workflows, OSError("scan failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            [
                "missing_owner: tests/f900/issue-owner.txt",
                "scan_error: .github/workflows: OSError",
            ],
        )
        self.assertFalse(sidecar.exists())

    def test_matching_workflow_entry_classification_failure_is_local(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            workflow = write_workflow(root)
            with selective_failure(checker, "is_file", workflow, PermissionError("denied")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            ["scan_error: .github/workflows/f900-fixture.yml: PermissionError"],
        )

    def test_tests_namespace_enumeration_failure_is_local_and_plan_error_remains_visible(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root, owner="**Issue:** #abc", name="malformed")
            write_test_package(root)
            tests_dir = root / "tests"
            with selective_failure(checker, "iterdir", tests_dir, OSError("scan failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            [
                "malformed_owner: docs/plans/F-900-malformed.md:3: '**Issue:** #abc'",
                "scan_error: tests: OSError",
            ],
        )

    def test_matching_test_package_classification_failure_is_local(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            package, _sidecar = write_test_package(root)
            with selective_failure(checker, "is_dir", package, OSError("stat failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, ["scan_error: tests/f900: OSError"])

    def test_sidecar_classification_failure_is_scan_error_not_missing_owner(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            _package, sidecar = write_test_package(root)
            with selective_failure(checker, "is_file", sidecar, OSError("stat failed")):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            ["scan_error: tests/f900/issue-owner.txt: OSError"],
        )

    def test_case_variant_research_and_plan_near_misses_are_not_classified(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            research_near = root / "docs" / "research" / "f-999-near-miss.md"
            research_near.write_text("unrelated\n", encoding="utf-8")
            plans = root / "docs" / "plans"
            plans.mkdir(parents=True)
            plan_near = plans / "f-999-plan.md"
            plan_near.write_text("unrelated\n", encoding="utf-8")

            original = checker.Path.is_file

            def guarded(path, *args, **kwargs):
                if path in {research_near, plan_near}:
                    raise AssertionError(f"near-miss was classified: {path}")
                return original(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "is_file", guarded):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, [])

    def test_case_variant_workflow_near_miss_is_not_classified(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            near = workflows / "F999-near-miss.yml"
            near.write_text("name: unrelated\n", encoding="utf-8")
            original = checker.Path.is_file

            def guarded(path, *args, **kwargs):
                if path == near:
                    raise AssertionError("workflow near-miss was classified")
                return original(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "is_file", guarded):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, [])

    def test_case_variant_test_package_near_miss_is_not_classified(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            near = root / "tests" / "F999"
            near.mkdir(parents=True)
            original = checker.Path.is_dir

            def guarded(path, *args, **kwargs):
                if path == near:
                    raise AssertionError("test-package near-miss was classified")
                return original(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "is_dir", guarded):
                diagnostics = checker.check_repository(root)
        self.assertEqual(diagnostics, [])

    def test_existing_read_error_contract_is_unchanged(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            workflow = write_workflow(root)
            original = checker.Path.read_text

            def selective_read(path, *args, **kwargs):
                if path == workflow:
                    raise UnicodeError("decode failed")
                return original(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "read_text", selective_read):
                diagnostics = checker.check_repository(root)
        self.assertEqual(
            diagnostics,
            ["read_error: .github/workflows/f900-fixture.yml: UnicodeError"],
        )

    def test_current_repository_passes(self):
        checker = load_checker()
        self.assertEqual(checker.check_repository(ROOT), [])


if __name__ == "__main__":
    unittest.main()
