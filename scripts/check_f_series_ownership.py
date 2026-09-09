from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

ARTIFACT_PATH_RE = re.compile(r"^docs/research/(F-[0-9]{3})-.*\.md$")
ISSUE_RE = re.compile(r"^\*\*Issue:\*\* #([1-9][0-9]*)\s*$")
AUTHORITY_PATH = "docs/research"


def _header_lines(text: str):
    lines = text.splitlines()
    for line_no in range(2, min(len(lines), 12) + 1):
        line = lines[line_no - 1]
        if line.startswith("## "):
            break
        yield line_no, line


def check_artifacts(artifacts: Mapping[str, str]) -> list[str]:
    diagnostics: list[str] = []
    valid_by_feature: dict[str, dict[int, list[str]]] = {}

    for path in sorted(artifacts):
        path_match = ARTIFACT_PATH_RE.fullmatch(path)
        if path_match is None:
            continue

        canonical: list[tuple[int, int]] = []
        malformed: list[tuple[int, str]] = []
        for line_no, line in _header_lines(artifacts[path]):
            issue_match = ISSUE_RE.fullmatch(line)
            if issue_match is not None:
                canonical.append((line_no, int(issue_match.group(1))))
            elif line.lstrip().startswith("**Issue:**"):
                malformed.append((line_no, line))

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


def scan_repository(root: Path) -> tuple[dict[str, str], list[str]]:
    research_dir = root / "docs" / "research"
    if not research_dir.is_dir():
        return {}, [f"authority_error: {AUTHORITY_PATH}: missing_or_not_directory"]

    candidates = sorted(research_dir.glob("F-[0-9][0-9][0-9]-*.md"))
    files = [path for path in candidates if path.is_file()]
    if not files:
        return {}, [f"authority_error: {AUTHORITY_PATH}: no_f_series_artifacts"]

    artifacts: dict[str, str] = {}
    diagnostics: list[str] = []
    for path in files:
        relative_path = path.relative_to(root).as_posix()
        try:
            artifacts[relative_path] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as exc:
            diagnostics.append(f"read_error: {relative_path}: {type(exc).__name__}")

    return artifacts, sorted(diagnostics)


def check_repository(root: Path) -> list[str]:
    artifacts, scan_diagnostics = scan_repository(root)
    return sorted([*scan_diagnostics, *check_artifacts(artifacts)])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check F-series research issue ownership in the current repository tree."
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
