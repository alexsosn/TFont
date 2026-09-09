from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts" / "check_f_series_ownership.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("_f023_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load checker from {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def markdown_doc(*header_lines: str, feature: str = "F-015") -> str:
    return "\n".join([f"# {feature} fixture", "", *header_lines, "", "## Body", ""])


def write_research(
    root: Path,
    *,
    feature: str = "F-015",
    issue: int = 87,
    suffix: str = "authority",
    text: str | None = None,
) -> Path:
    path = root / "docs" / "research" / f"{feature}-{suffix}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        text if text is not None else markdown_doc(f"**Issue:** #{issue}", feature=feature),
        encoding="utf-8",
    )
    return path


def write_plan(
    root: Path,
    *,
    feature: str = "F-015",
    suffix: str = "plan",
    owner_line: str | None = "**Issue:** #87",
    extra_header_lines: tuple[str, ...] = (),
) -> Path:
    path = root / "docs" / "plans" / f"{feature}-{suffix}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (() if owner_line is None else (owner_line,)) + extra_header_lines
    path.write_text(markdown_doc(*header, feature=feature), encoding="utf-8")
    return path


def write_workflow(
    root: Path,
    *,
    feature: str = "F-015",
    suffix: str = "fixture",
    extension: str = "yml",
    lines: tuple[str, ...] = ("# Issue: #87", "name: fixture"),
) -> Path:
    digits = feature.removeprefix("F-")
    path = root / ".github" / "workflows" / f"f{digits}-{suffix}.{extension}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join((*lines, "")), encoding="utf-8")
    return path


def write_test_sidecar(
    root: Path,
    *,
    feature: str = "F-015",
    text: str = "Issue: #87\n",
) -> Path:
    digits = feature.removeprefix("F-")
    package = root / "tests" / f"f{digits}"
    package.mkdir(parents=True, exist_ok=True)
    sidecar = package / "issue-owner.txt"
    sidecar.write_text(text, encoding="utf-8")
    return sidecar


class DownstreamOwnershipEnforcementREDTests(unittest.TestCase):
    maxDiff = None

    def assert_check(self, root: Path, expected: list[str]) -> None:
        checker = load_checker()
        self.assertEqual(checker.check_repository(root), expected)

    def test_workflow_wrong_owner_conflicts_with_research_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root, lines=("# Issue: #90", "name: stale"))
            self.assert_check(
                root,
                [
                    "conflicting_owner: .github/workflows/f015-fixture.yml: "
                    "F-015: expected #87, found #90"
                ],
            )

    def test_test_sidecar_wrong_owner_conflicts_with_research_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_test_sidecar(root, text="Issue: #90\n")
            self.assert_check(
                root,
                [
                    "conflicting_owner: tests/f015/issue-owner.txt: "
                    "F-015: expected #87, found #90"
                ],
            )

    def test_matching_plan_yml_workflow_and_test_sidecar_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root)
            write_workflow(root)
            write_test_sidecar(root)
            self.assert_check(root, [])

    def test_yaml_workflow_is_independently_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(
                root,
                extension="yaml",
                lines=("# Issue: #90", "name: stale-yaml"),
            )
            self.assert_check(
                root,
                [
                    "conflicting_owner: .github/workflows/f015-fixture.yaml: "
                    "F-015: expected #87, found #90"
                ],
            )

    def test_plan_without_owner_fails_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root, owner_line=None)
            self.assert_check(root, ["missing_owner: docs/plans/F-015-plan.md"])

    def test_workflow_without_owner_fails_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root, lines=("name: missing",))
            self.assert_check(root, ["missing_owner: .github/workflows/f015-fixture.yml"])

    def test_test_package_without_sidecar_fails_at_expected_carrier_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            (root / "tests" / "f015").mkdir(parents=True)
            self.assert_check(root, ["missing_owner: tests/f015/issue-owner.txt"])

    def test_malformed_plan_owner_is_stable_and_suppresses_relationship_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root, owner_line="**Issue:** #abc")
            self.assert_check(
                root,
                ["malformed_owner: docs/plans/F-015-plan.md:3: '**Issue:** #abc'"],
            )

    def test_malformed_workflow_owner_is_stable_and_suppresses_relationship_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root, lines=("# Issue: #abc", "name: malformed"))
            self.assert_check(
                root,
                [
                    "malformed_owner: .github/workflows/f015-fixture.yml:1: "
                    "'# Issue: #abc'"
                ],
            )

    def test_duplicate_plan_owner_is_reported_without_relationship_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_plan(root, extra_header_lines=("**Issue:** #87",))
            self.assert_check(
                root,
                ["duplicate_owner: docs/plans/F-015-plan.md: lines 3,4"],
            )

    def test_duplicate_workflow_owner_is_reported_without_relationship_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(
                root,
                lines=("# Issue: #87", "# Issue: #87", "name: duplicate"),
            )
            self.assert_check(
                root,
                ["duplicate_owner: .github/workflows/f015-fixture.yml: lines 1,2"],
            )

    def test_duplicate_test_sidecar_is_distinct_from_malformed_extra_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            duplicate_root = Path(tmp) / "duplicate"
            malformed_root = Path(tmp) / "malformed"
            write_research(duplicate_root)
            write_test_sidecar(duplicate_root, text="Issue: #87\nIssue: #87\n")
            write_research(malformed_root)
            write_test_sidecar(malformed_root, text="Issue: #87\nextra\n")
            self.assert_check(
                duplicate_root,
                ["duplicate_owner: tests/f015/issue-owner.txt: lines 1,2"],
            )
            self.assert_check(
                malformed_root,
                ["malformed_owner: tests/f015/issue-owner.txt: invalid_sidecar_content"],
            )

    def test_locally_valid_downstream_claim_without_research_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(
                root,
                feature="F-999",
                lines=("# Issue: #999", "name: unknown"),
            )
            self.assert_check(
                root,
                ["unknown_feature: .github/workflows/f999-fixture.yml: F-999"],
            )

    def test_research_only_feature_without_downstream_namespaces_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root, feature="F-999", issue=999)
            self.assert_check(root, [])

    def test_multiple_plans_must_each_match_research_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            good_root = Path(tmp) / "good"
            bad_root = Path(tmp) / "bad"
            write_research(good_root)
            write_plan(good_root, suffix="a")
            write_plan(good_root, suffix="b")
            write_research(bad_root)
            write_plan(bad_root, suffix="a")
            write_plan(bad_root, suffix="b", owner_line="**Issue:** #90")
            self.assert_check(good_root, [])
            self.assert_check(
                bad_root,
                [
                    "conflicting_owner: docs/plans/F-015-b.md: "
                    "F-015: expected #87, found #90"
                ],
            )

    def test_invalid_research_authority_suppresses_relation_but_keeps_local_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root, issue=87, suffix="a")
            write_research(root, issue=88, suffix="b")
            write_workflow(root, lines=("# Issue: #abc", "name: malformed"))
            self.assert_check(
                root,
                [
                    "conflicting_owner: F-015: #87=docs/research/F-015-a.md; "
                    "#88=docs/research/F-015-b.md",
                    "malformed_owner: .github/workflows/f015-fixture.yml:1: "
                    "'# Issue: #abc'",
                ],
            )

    def test_research_read_failure_marks_known_feature_invalid_for_relationships(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            research_path = write_research(root)
            write_workflow(root, lines=("# Issue: #90", "name: downstream"))
            original_read_text = checker.Path.read_text

            def selective_read_text(path, *args, **kwargs):
                if path == research_path:
                    raise OSError("synthetic research read failure")
                return original_read_text(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "read_text", selective_read_text):
                diagnostics = checker.check_repository(root)
            self.assertEqual(
                diagnostics,
                ["read_error: docs/research/F-015-authority.md: OSError"],
            )

    def test_downstream_read_failure_is_stable_and_suppresses_relationship_noise(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            workflow_path = write_workflow(root)
            original_read_text = checker.Path.read_text

            def selective_read_text(path, *args, **kwargs):
                if path == workflow_path:
                    raise UnicodeError("synthetic downstream decode failure")
                return original_read_text(path, *args, **kwargs)

            with mock.patch.object(checker.Path, "read_text", selective_read_text):
                diagnostics = checker.check_repository(root)
            self.assertEqual(
                diagnostics,
                ["read_error: .github/workflows/f015-fixture.yml: UnicodeError"],
            )

    def test_diagnostics_are_deterministic_across_creation_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            forward_root = Path(tmp) / "forward"
            reverse_root = Path(tmp) / "reverse"

            write_research(forward_root)
            write_plan(forward_root, suffix="a", owner_line=None)
            write_workflow(forward_root, suffix="z", lines=("# Issue: #90", "name: stale"))

            write_research(reverse_root)
            write_workflow(reverse_root, suffix="z", lines=("# Issue: #90", "name: stale"))
            write_plan(reverse_root, suffix="a", owner_line=None)

            expected = [
                "conflicting_owner: .github/workflows/f015-z.yml: "
                "F-015: expected #87, found #90",
                "missing_owner: docs/plans/F-015-a.md",
            ]
            self.assert_check(forward_root, expected)
            self.assert_check(reverse_root, expected)

    def test_global_missing_authority_short_circuits_downstream_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_workflow(
                root,
                feature="F-999",
                lines=("# Issue: #999", "name: orphan"),
            )
            self.assert_check(
                root,
                ["authority_error: docs/research: missing_or_not_directory"],
            )

    def test_cli_matches_callable_on_downstream_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_research(root)
            write_workflow(root, lines=("# Issue: #90", "name: stale"))
            expected = (
                "conflicting_owner: .github/workflows/f015-fixture.yml: "
                "F-015: expected #87, found #90\n"
            )
            completed = subprocess.run(
                [sys.executable, str(CHECKER_PATH), str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr, expected)

    def test_current_repository_passes_new_repository_wide_checker(self):
        checker = load_checker()
        self.assertEqual(checker.check_repository(ROOT), [])


if __name__ == "__main__":
    unittest.main()
