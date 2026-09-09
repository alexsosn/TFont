from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "docs" / "research"
CHECKER_PATH = ROOT / "scripts" / "check_f_series_ownership.py"

FILENAME_RE = re.compile(r"^(F-[0-9]{3})-.*\.md$")
ISSUE_RE = re.compile(r"^\*\*Issue:\*\* #([1-9][0-9]*)\s*$")


def header_ownership(text: str) -> tuple[list[tuple[int, int]], list[tuple[int, str]]]:
    owners: list[tuple[int, int]] = []
    malformed: list[tuple[int, str]] = []
    lines = text.splitlines()
    for line_no in range(2, min(len(lines), 12) + 1):
        line = lines[line_no - 1]
        if line.startswith("## "):
            break
        match = ISSUE_RE.fullmatch(line)
        if match:
            owners.append((line_no, int(match.group(1))))
        elif line.lstrip().startswith("**Issue:**"):
            malformed.append((line_no, line))
    return owners, malformed


def current_records() -> dict[str, tuple[str, list[tuple[int, int]], list[tuple[int, str]]]]:
    result: dict[str, tuple[str, list[tuple[int, int]], list[tuple[int, str]]]] = {}
    if not RESEARCH_DIR.is_dir():
        return result
    for path in sorted(RESEARCH_DIR.glob("F-[0-9][0-9][0-9]-*.md")):
        if not path.is_file():
            continue
        match = FILENAME_RE.fullmatch(path.name)
        if match is None:
            continue
        owners, malformed = header_ownership(path.read_text(encoding="utf-8"))
        result[path.name] = (match.group(1), owners, malformed)
    return result


def load_checker():
    spec = importlib.util.spec_from_file_location("_f021_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load checker spec from {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def doc(*header_lines: str, feature: str = "F-900") -> str:
    body = [f"# {feature} fixture", "", *header_lines, "", "## Body", ""]
    return "\n".join(body)


class RepositoryMetadataControls(unittest.TestCase):
    def test_authority_directory_and_f_series_artifacts_exist(self):
        self.assertTrue(RESEARCH_DIR.is_dir())
        self.assertTrue(current_records())

    def test_every_current_artifact_has_one_canonical_owner(self):
        records = current_records()
        problems: list[str] = []
        for name, (_feature, owners, malformed) in sorted(records.items()):
            if malformed:
                problems.append(f"{name}: malformed={malformed!r}")
            if len(owners) != 1:
                problems.append(f"{name}: owners={owners!r}")
        self.assertEqual(problems, [])

    def test_current_same_id_groups_have_one_owner(self):
        by_feature: dict[str, set[int]] = {}
        for feature, owners, malformed in current_records().values():
            if malformed or len(owners) != 1:
                continue
            by_feature.setdefault(feature, set()).add(owners[0][1])
        conflicts = {
            feature: sorted(owners)
            for feature, owners in sorted(by_feature.items())
            if len(owners) > 1
        }
        self.assertEqual(conflicts, {})

    def test_f019_primary_and_evidence_share_issue_94(self):
        records = current_records()
        for name in (
            "F-019-invalid-source-filesystem-paths.md",
            "F-019-cpython-path-conversion-evidence.md",
        ):
            with self.subTest(path=name):
                self.assertIn(name, records)
                _feature, owners, malformed = records[name]
                self.assertEqual(malformed, [])
                self.assertEqual([owner for _line, owner in owners], [94])


class FeatureOwnershipCheckerREDTests(unittest.TestCase):
    def test_checker_module_exists(self):
        self.assertTrue(CHECKER_PATH.is_file(), f"missing planned checker: {CHECKER_PATH}")

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_different_owners_under_one_feature_conflict(self):
        checker = load_checker()
        artifacts = {
            "docs/research/F-900-a.md": doc("**Issue:** #123"),
            "docs/research/F-900-b.md": doc("**Issue:** #456"),
        }
        self.assertEqual(
            checker.check_artifacts(artifacts),
            [
                "conflicting_owner: F-900: #123=docs/research/F-900-a.md; "
                "#456=docs/research/F-900-b.md"
            ],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_same_owner_multi_artifact_passes(self):
        checker = load_checker()
        artifacts = {
            "docs/research/F-900-a.md": doc("**Issue:** #123"),
            "docs/research/F-900-evidence.md": doc("**Issue:** #123"),
        }
        self.assertEqual(checker.check_artifacts(artifacts), [])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_new_feature_with_one_owner_passes(self):
        checker = load_checker()
        self.assertEqual(
            checker.check_artifacts(
                {"docs/research/F-999-new.md": doc("**Issue:** #777", feature="F-999")}
            ),
            [],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_missing_owner_fails(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        self.assertEqual(checker.check_artifacts({path: doc()}), [f"missing_owner: {path}"])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_duplicate_same_owner_lines_fail(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        self.assertEqual(
            checker.check_artifacts({path: doc("**Issue:** #123", "**Issue:** #123")}),
            [f"duplicate_owner: {path}: lines 3,4"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_duplicate_different_owner_lines_do_not_create_conflict_noise(self):
        checker = load_checker()
        bad = "docs/research/F-900-a.md"
        good = "docs/research/F-900-b.md"
        artifacts = {
            bad: doc("**Issue:** #123", "**Issue:** #456"),
            good: doc("**Issue:** #789"),
        }
        self.assertEqual(
            checker.check_artifacts(artifacts),
            [f"duplicate_owner: {bad}: lines 3,4"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_malformed_owner_alone_has_no_redundant_missing_owner(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        line = "**Issue:** #abc"
        self.assertEqual(
            checker.check_artifacts({path: doc(line)}),
            [f"malformed_owner: {path}:3: {line!r}"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_malformed_owner_cannot_be_hidden_by_canonical_owner(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        line = "**Issue:** #abc"
        self.assertEqual(
            checker.check_artifacts({path: doc("**Issue:** #123", line)}),
            [f"malformed_owner: {path}:4: {line!r}"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_malformed_plus_duplicate_reports_both_without_conflict_noise(self):
        checker = load_checker()
        bad = "docs/research/F-900-a.md"
        good = "docs/research/F-900-b.md"
        malformed = "**Issue:** #abc"
        artifacts = {
            bad: doc("**Issue:** #123", "**Issue:** #123", malformed),
            good: doc("**Issue:** #999"),
        }
        self.assertEqual(
            checker.check_artifacts(artifacts),
            [
                f"duplicate_owner: {bad}: lines 3,4",
                f"malformed_owner: {bad}:5: {malformed!r}",
            ],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_body_issue_mention_does_not_count(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        text = "# F-900 fixture\n\n## Body\n\n**Issue:** #123\n"
        self.assertEqual(checker.check_artifacts({path: text}), [f"missing_owner: {path}"])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_line_12_owner_is_accepted(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        lines = ["# F-900 fixture", *("" for _ in range(10)), "**Issue:** #123", "## Body"]
        self.assertEqual(checker.check_artifacts({path: "\n".join(lines)}), [])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_line_13_owner_is_outside_header_contract(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        lines = ["# F-900 fixture", *("" for _ in range(11)), "**Issue:** #123"]
        self.assertEqual(
            checker.check_artifacts({path: "\n".join(lines)}),
            [f"missing_owner: {path}"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_section_heading_stops_header_scan(self):
        checker = load_checker()
        path = "docs/research/F-900-a.md"
        text = "# F-900 fixture\n\n## Body\n**Issue:** #123\n"
        self.assertEqual(checker.check_artifacts({path: text}), [f"missing_owner: {path}"])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_unrelated_namespace_paths_are_ignored(self):
        checker = load_checker()
        artifacts = {
            "docs/research/R-900-unrelated.md": doc("**Issue:** #abc", feature="R-900"),
            "docs/research/F-900-valid.md": doc("**Issue:** #123"),
        }
        self.assertEqual(checker.check_artifacts(artifacts), [])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_diagnostics_are_stable_across_input_order(self):
        checker = load_checker()
        items = [
            ("docs/research/F-901-missing.md", doc(feature="F-901")),
            ("docs/research/F-900-b.md", doc("**Issue:** #456")),
            ("docs/research/F-900-a.md", doc("**Issue:** #123")),
        ]
        forward = checker.check_artifacts(dict(items))
        reverse = checker.check_artifacts(dict(reversed(items)))
        self.assertEqual(forward, reverse)
        self.assertEqual(forward, sorted(forward))

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_scan_repository_preserves_read_failure_as_stable_diagnostic(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            research = root / "docs" / "research"
            research.mkdir(parents=True)
            path = research / "F-900-a.md"
            path.write_text(doc("**Issue:** #123"), encoding="utf-8")
            with mock.patch.object(checker.Path, "read_text", side_effect=OSError("boom")):
                artifacts, diagnostics = checker.scan_repository(root)
        self.assertEqual(artifacts, {})
        self.assertEqual(
            diagnostics,
            ["read_error: docs/research/F-900-a.md: OSError"],
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_missing_or_non_directory_authority_fails_closed(self):
        checker = load_checker()
        expected = ["authority_error: docs/research: missing_or_not_directory"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(checker.scan_repository(root), ({}, expected))
            docs = root / "docs"
            docs.mkdir()
            (docs / "research").write_text("not a directory", encoding="utf-8")
            self.assertEqual(checker.scan_repository(root), ({}, expected))

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_empty_authority_directory_fails_closed(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "research").mkdir(parents=True)
            self.assertEqual(
                checker.scan_repository(root),
                ({}, ["authority_error: docs/research: no_f_series_artifacts"]),
            )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_current_repository_passes(self):
        checker = load_checker()
        self.assertEqual(checker.check_repository(ROOT), [])

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_cli_is_silent_and_successful_on_current_repository(self):
        completed = subprocess.run(
            [sys.executable, str(CHECKER_PATH), str(ROOT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_cli_wrong_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, str(CHECKER_PATH), tmp],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            "authority_error: docs/research: missing_or_not_directory\n",
        )

    @unittest.skipUnless(CHECKER_PATH.exists(), "checker not implemented on RED head")
    def test_cli_conflict_fails_with_sorted_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            research = root / "docs" / "research"
            research.mkdir(parents=True)
            (research / "F-900-a.md").write_text(doc("**Issue:** #123"), encoding="utf-8")
            (research / "F-900-b.md").write_text(doc("**Issue:** #456"), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(CHECKER_PATH), str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            "conflicting_owner: F-900: #123=docs/research/F-900-a.md; "
            "#456=docs/research/F-900-b.md\n",
        )


if __name__ == "__main__":
    unittest.main()
