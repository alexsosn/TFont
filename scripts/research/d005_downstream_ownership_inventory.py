from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "docs" / "research"
PLANS_DIR = ROOT / "docs" / "plans"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
TESTS_DIR = ROOT / "tests"

F_DOC_RE = re.compile(r"^(F-[0-9]{3})-.*\.md$")
F_WORKFLOW_RE = re.compile(r"^f([0-9]{3})-.*\.ya?ml$")
F_TEST_RE = re.compile(r"^f([0-9]{3})$")
ISSUE_RE = re.compile(r"^\*\*Issue:\*\* #([1-9][0-9]*)\s*$")
WORKFLOW_OWNER_RE = re.compile(r"^# Issue: #([1-9][0-9]*)\s*$")
TEST_OWNER_RE = re.compile(r"^Issue: #([1-9][0-9]*)\n?$")


def bounded_markdown_owners(text: str) -> tuple[list[int], list[tuple[int, str]]]:
    owners: list[int] = []
    malformed: list[tuple[int, str]] = []
    lines = text.splitlines()
    for line_no in range(2, min(len(lines), 12) + 1):
        line = lines[line_no - 1]
        if line.startswith("## "):
            break
        match = ISSUE_RE.fullmatch(line)
        if match:
            owners.append(int(match.group(1)))
        elif line.lstrip().startswith("**Issue:**"):
            malformed.append((line_no, line))
    return owners, malformed


def research_authority() -> tuple[dict[str, int], list[str]]:
    by_feature: dict[str, set[int]] = defaultdict(set)
    errors: list[str] = []
    for path in sorted(RESEARCH_DIR.glob("F-[0-9][0-9][0-9]-*.md")):
        if not path.is_file():
            continue
        match = F_DOC_RE.fullmatch(path.name)
        if match is None:
            continue
        owners, malformed = bounded_markdown_owners(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        if malformed or len(owners) != 1:
            errors.append(f"invalid research authority: {rel}: owners={owners!r} malformed={malformed!r}")
            continue
        by_feature[match.group(1)].add(owners[0])

    authority: dict[str, int] = {}
    for feature, owners in sorted(by_feature.items()):
        if len(owners) != 1:
            errors.append(f"conflicting research authority: {feature}: {sorted(owners)!r}")
        else:
            authority[feature] = next(iter(owners))
    return authority, errors


def inventory_plans(authority: dict[str, int]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for path in sorted(PLANS_DIR.glob("F-[0-9][0-9][0-9]-*.md")):
        if not path.is_file():
            continue
        match = F_DOC_RE.fullmatch(path.name)
        if match is None:
            continue
        feature = match.group(1)
        owners, malformed = bounded_markdown_owners(path.read_text(encoding="utf-8"))
        expected = authority.get(feature)
        if malformed:
            status = "malformed"
        elif len(owners) == 0:
            status = "missing"
        elif len(owners) > 1:
            status = "duplicate"
        elif expected is None:
            status = "unknown_feature"
        elif owners[0] != expected:
            status = "conflicting"
        else:
            status = "matching"
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "feature": feature,
                "expected_issue": expected,
                "declared_issues": owners,
                "malformed": malformed,
                "status": status,
            }
        )
    return summarize_rows(rows)


def inventory_workflows(authority: dict[str, int]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for path in sorted(WORKFLOWS_DIR.iterdir()):
        if not path.is_file():
            continue
        match = F_WORKFLOW_RE.fullmatch(path.name)
        if match is None:
            continue
        feature = f"F-{match.group(1)}"
        declared: list[int] = []
        malformed: list[tuple[int, str]] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines()[:12], start=1):
            owner_match = WORKFLOW_OWNER_RE.fullmatch(line)
            if owner_match:
                declared.append(int(owner_match.group(1)))
            elif line.lstrip().startswith("# Issue:"):
                malformed.append((line_no, line))
        expected = authority.get(feature)
        if malformed:
            status = "malformed"
        elif not declared:
            status = "missing"
        elif len(declared) > 1:
            status = "duplicate"
        elif expected is None:
            status = "unknown_feature"
        elif declared[0] != expected:
            status = "conflicting"
        else:
            status = "matching"
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "feature": feature,
                "expected_issue": expected,
                "declared_issues": declared,
                "malformed": malformed,
                "status": status,
            }
        )
    return summarize_rows(rows)


def detect_test_owner(package: Path) -> tuple[list[int], str | None, bool]:
    path = package / "issue-owner.txt"
    if not path.is_file():
        return [], None, False
    text = path.read_text(encoding="utf-8")
    match = TEST_OWNER_RE.fullmatch(text)
    source = path.relative_to(ROOT).as_posix()
    if match is None:
        return [], source, True
    return [int(match.group(1))], source, False


def inventory_test_packages(authority: dict[str, int]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for package in sorted(TESTS_DIR.iterdir()):
        if not package.is_dir():
            continue
        match = F_TEST_RE.fullmatch(package.name)
        if match is None:
            continue
        feature = f"F-{match.group(1)}"
        declared, source, malformed = detect_test_owner(package)
        expected = authority.get(feature)
        if malformed:
            status = "malformed"
        elif not declared:
            status = "missing"
        elif expected is None:
            status = "unknown_feature"
        elif declared[0] != expected:
            status = "conflicting"
        else:
            status = "matching"
        rows.append(
            {
                "path": package.relative_to(ROOT).as_posix(),
                "feature": feature,
                "expected_issue": expected,
                "declared_issues": declared,
                "owner_source": source,
                "owner_malformed": malformed,
                "has_init_py": (package / "__init__.py").is_file(),
                "python_files": len(list(package.glob("*.py"))),
                "status": status,
            }
        )
    return summarize_rows(rows)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row["status"])] += 1
    return {
        "count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "rows": rows,
    }


def main() -> int:
    authority, authority_errors = research_authority()
    result = {
        "research_features": len(authority),
        "research_authority_errors": authority_errors,
        "plans": inventory_plans(authority),
        "workflows": inventory_workflows(authority),
        "test_packages": inventory_test_packages(authority),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if authority_errors else 0


if __name__ == "__main__":
    sys.exit(main())
