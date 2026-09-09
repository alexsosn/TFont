from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

ARTIFACT_PATH_RE = re.compile(r"^docs/research/(F-[0-9]{3})-.*\.md$")
PLAN_FILENAME_RE = re.compile(r"^(F-[0-9]{3})-.*\.md$")
WORKFLOW_FILENAME_RE = re.compile(r"^f([0-9]{3})-.*\.(?:yml|yaml)$")
TEST_PACKAGE_RE = re.compile(r"^f([0-9]{3})$")
ISSUE_RE = re.compile(r"^\*\*Issue:\*\* #([1-9][0-9]*)\s*$")
WORKFLOW_ISSUE_RE = re.compile(r"^# Issue: #([1-9][0-9]*)\s*$")
SIDECAR_ISSUE_RE = re.compile(r"^Issue: #([1-9][0-9]*)$")
AUTHORITY_PATH = "docs/research"


def _header_lines(text: str):
    lines = text.splitlines()
    for line_no in range(2, min(len(lines), 12) + 1):
        line = lines[line_no - 1]
        if line.startswith("## "):
            break
        yield line_no, line


def _markdown_owners(text: str) -> tuple[list[tuple[int, int]], list[tuple[int, str]]]:
    canonical: list[tuple[int, int]] = []
    malformed: list[tuple[int, str]] = []
    for line_no, line in _header_lines(text):
        issue_match = ISSUE_RE.fullmatch(line)
        if issue_match is not None:
            canonical.append((line_no, int(issue_match.group(1))))
        elif line.lstrip().startswith("**Issue:**"):
            malformed.append((line_no, line))
    return canonical, malformed


def check_artifacts(artifacts: Mapping[str, str]) -> list[str]:
    diagnostics: list[str] = []
    valid_by_feature: dict[str, dict[int, list[str]]] = {}

    for path in sorted(artifacts):
        path_match = ARTIFACT_PATH_RE.fullmatch(path)
        if path_match is None:
            continue

        canonical, malformed = _markdown_owners(artifacts[path])

        for line_no, line in malformed:
            diagnostics.append(f"malformed_owner: {path}:{line_no}: {line!r}")

        if len(canonical) >= 2:
            line_numbers = ",".join(str(line_no) for line_no, _owner in canonical)
            diagnostics.append(f"duplicate_owner: {path}: lines {line_numbers}")

        if malformed or len(canonical) >= 2:
            continue

        if not canonical:
            diagnostics.append(f"missing_owner: {path}")
            continue

        feature = path_match.group(1)
        owner = canonical[0][1]
        valid_by_feature.setdefault(feature, {}).setdefault(owner, []).append(path)

    for feature, by_owner in sorted(valid_by_feature.items()):
        if len(by_owner) <= 1:
            continue
        owner_groups: list[str] = []
        for owner in sorted(by_owner):
            paths = ",".join(sorted(by_owner[owner]))
            owner_groups.append(f"#{owner}={paths}")
        diagnostics.append(f"conflicting_owner: {feature}: {'; '.join(owner_groups)}")

    return sorted(diagnostics)


def _scan_research_repository(
    root: Path,
) -> tuple[dict[str, str], list[str], set[str], bool]:
    research_dir = root / "docs" / "research"
    if not research_dir.is_dir():
        return (
            {},
            [f"authority_error: {AUTHORITY_PATH}: missing_or_not_directory"],
            set(),
            True,
        )

    candidates = sorted(research_dir.glob("F-[0-9][0-9][0-9]-*.md"))
    files = [path for path in candidates if path.is_file()]
    if not files:
        return (
            {},
            [f"authority_error: {AUTHORITY_PATH}: no_f_series_artifacts"],
            set(),
            True,
        )

    artifacts: dict[str, str] = {}
    diagnostics: list[str] = []
    invalid_features: set[str] = set()
    for path in files:
        relative_path = path.relative_to(root).as_posix()
        try:
            artifacts[relative_path] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as exc:
            diagnostics.append(f"read_error: {relative_path}: {type(exc).__name__}")
            match = PLAN_FILENAME_RE.fullmatch(path.name)
            if match is not None:
                invalid_features.add(match.group(1))

    return artifacts, sorted(diagnostics), invalid_features, False


def scan_repository(root: Path) -> tuple[dict[str, str], list[str]]:
    artifacts, diagnostics, _invalid_features, _global_failure = _scan_research_repository(root)
    return artifacts, diagnostics


def _research_authority(
    artifacts: Mapping[str, str], read_invalid_features: set[str]
) -> tuple[dict[str, int], set[str]]:
    invalid_features = set(read_invalid_features)
    valid_by_feature: dict[str, dict[int, list[str]]] = {}

    for path in sorted(artifacts):
        path_match = ARTIFACT_PATH_RE.fullmatch(path)
        if path_match is None:
            continue
        feature = path_match.group(1)
        canonical, malformed = _markdown_owners(artifacts[path])
        if malformed or len(canonical) != 1:
            invalid_features.add(feature)
            continue
        owner = canonical[0][1]
        valid_by_feature.setdefault(feature, {}).setdefault(owner, []).append(path)

    for feature, by_owner in valid_by_feature.items():
        if len(by_owner) != 1:
            invalid_features.add(feature)

    authority: dict[str, int] = {}
    for feature, by_owner in sorted(valid_by_feature.items()):
        if feature in invalid_features or len(by_owner) != 1:
            continue
        authority[feature] = next(iter(by_owner))
    return authority, invalid_features


def _read_text(path: Path, root: Path) -> tuple[str | None, str | None]:
    relative_path = path.relative_to(root).as_posix()
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeError, ValueError) as exc:
        return None, f"read_error: {relative_path}: {type(exc).__name__}"


def _relationship_diagnostic(
    path: str,
    feature: str,
    owner: int,
    authority: Mapping[str, int],
    invalid_features: set[str],
) -> str | None:
    if feature in invalid_features:
        return None
    expected = authority.get(feature)
    if expected is None:
        return f"unknown_feature: {path}: {feature}"
    if owner != expected:
        return f"conflicting_owner: {path}: {feature}: expected #{expected}, found #{owner}"
    return None


def _check_plan(
    path: Path,
    root: Path,
    feature: str,
    authority: Mapping[str, int],
    invalid_features: set[str],
) -> list[str]:
    relative_path = path.relative_to(root).as_posix()
    text, read_diagnostic = _read_text(path, root)
    if read_diagnostic is not None:
        return [read_diagnostic]
    assert text is not None

    canonical, malformed = _markdown_owners(text)
    diagnostics = [
        f"malformed_owner: {relative_path}:{line_no}: {line!r}"
        for line_no, line in malformed
    ]
    if len(canonical) >= 2:
        line_numbers = ",".join(str(line_no) for line_no, _owner in canonical)
        diagnostics.append(f"duplicate_owner: {relative_path}: lines {line_numbers}")
    if malformed or len(canonical) >= 2:
        return sorted(diagnostics)
    if not canonical:
        return [f"missing_owner: {relative_path}"]

    relationship = _relationship_diagnostic(
        relative_path, feature, canonical[0][1], authority, invalid_features
    )
    return [] if relationship is None else [relationship]


def _workflow_owners(text: str) -> tuple[list[tuple[int, int]], list[tuple[int, str]]]:
    canonical: list[tuple[int, int]] = []
    malformed: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines()[:12], start=1):
        issue_match = WORKFLOW_ISSUE_RE.fullmatch(line)
        if issue_match is not None:
            canonical.append((line_no, int(issue_match.group(1))))
        elif line.lstrip().startswith("# Issue:"):
            malformed.append((line_no, line))
    return canonical, malformed


def _check_workflow(
    path: Path,
    root: Path,
    feature: str,
    authority: Mapping[str, int],
    invalid_features: set[str],
) -> list[str]:
    relative_path = path.relative_to(root).as_posix()
    text, read_diagnostic = _read_text(path, root)
    if read_diagnostic is not None:
        return [read_diagnostic]
    assert text is not None

    canonical, malformed = _workflow_owners(text)
    diagnostics = [
        f"malformed_owner: {relative_path}:{line_no}: {line!r}"
        for line_no, line in malformed
    ]
    if len(canonical) >= 2:
        line_numbers = ",".join(str(line_no) for line_no, _owner in canonical)
        diagnostics.append(f"duplicate_owner: {relative_path}: lines {line_numbers}")
    if malformed or len(canonical) >= 2:
        return sorted(diagnostics)
    if not canonical:
        return [f"missing_owner: {relative_path}"]

    relationship = _relationship_diagnostic(
        relative_path, feature, canonical[0][1], authority, invalid_features
    )
    return [] if relationship is None else [relationship]


def _check_test_package(
    package: Path,
    root: Path,
    feature: str,
    authority: Mapping[str, int],
    invalid_features: set[str],
) -> list[str]:
    sidecar = package / "issue-owner.txt"
    relative_path = sidecar.relative_to(root).as_posix()
    if not sidecar.is_file():
        return [f"missing_owner: {relative_path}"]

    text, read_diagnostic = _read_text(sidecar, root)
    if read_diagnostic is not None:
        return [read_diagnostic]
    assert text is not None

    canonical: list[tuple[int, int]] = []
    invalid_content = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        issue_match = SIDECAR_ISSUE_RE.fullmatch(line)
        if issue_match is None:
            invalid_content = True
        else:
            canonical.append((line_no, int(issue_match.group(1))))

    if invalid_content or not canonical:
        return [f"malformed_owner: {relative_path}: invalid_sidecar_content"]
    if len(canonical) >= 2:
        line_numbers = ",".join(str(line_no) for line_no, _owner in canonical)
        return [f"duplicate_owner: {relative_path}: lines {line_numbers}"]

    relationship = _relationship_diagnostic(
        relative_path, feature, canonical[0][1], authority, invalid_features
    )
    return [] if relationship is None else [relationship]


def _check_downstream(
    root: Path, authority: Mapping[str, int], invalid_features: set[str]
) -> list[str]:
    diagnostics: list[str] = []

    plans_dir = root / "docs" / "plans"
    if plans_dir.is_dir():
        for path in sorted(plans_dir.glob("F-[0-9][0-9][0-9]-*.md")):
            if not path.is_file():
                continue
            match = PLAN_FILENAME_RE.fullmatch(path.name)
            if match is None:
                continue
            diagnostics.extend(
                _check_plan(path, root, match.group(1), authority, invalid_features)
            )

    workflows_dir = root / ".github" / "workflows"
    if workflows_dir.is_dir():
        for path in sorted(workflows_dir.iterdir()):
            if not path.is_file():
                continue
            match = WORKFLOW_FILENAME_RE.fullmatch(path.name)
            if match is None:
                continue
            feature = f"F-{match.group(1)}"
            diagnostics.extend(
                _check_workflow(path, root, feature, authority, invalid_features)
            )

    tests_dir = root / "tests"
    if tests_dir.is_dir():
        for package in sorted(tests_dir.iterdir()):
            if not package.is_dir():
                continue
            match = TEST_PACKAGE_RE.fullmatch(package.name)
            if match is None:
                continue
            feature = f"F-{match.group(1)}"
            diagnostics.extend(
                _check_test_package(package, root, feature, authority, invalid_features)
            )

    return sorted(diagnostics)


def check_repository(root: Path) -> list[str]:
    artifacts, scan_diagnostics, read_invalid_features, global_failure = (
        _scan_research_repository(root)
    )
    research_diagnostics = check_artifacts(artifacts)
    if global_failure:
        return sorted([*scan_diagnostics, *research_diagnostics])

    authority, invalid_features = _research_authority(artifacts, read_invalid_features)
    downstream_diagnostics = _check_downstream(root, authority, invalid_features)
    return sorted([*scan_diagnostics, *research_diagnostics, *downstream_diagnostics])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check F-series research authority and downstream ownership in the current repository tree."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the repository containing this script)",
    )
    args = parser.parse_args(argv)

    diagnostics = check_repository(args.root)
    for diagnostic in diagnostics:
        print(diagnostic, file=sys.stderr)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
