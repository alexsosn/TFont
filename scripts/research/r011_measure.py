#!/usr/bin/env python3
"""Measure the non-production R-011 ontology-mapped pilot fixture.

This script intentionally separates:

1. reviewed fixture coverage (agent-useful weighted mapping rows),
2. raw schema-concept consideration against accepted R-005 inventories where available,
3. common-target query-plan compilability.

It does not authorize approximate execution. R-016 owns that policy.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ASSESSMENTS = {
    "exact",
    "close",
    "broader",
    "narrower",
    "related",
    "ambiguous",
    "native-only",
    "unsupported",
}
NO_TARGET = {"native-only", "unsupported", "ambiguous"}
REQUIRED_CORPORA = {
    "bhsa",
    "cuc",
    "syriac",
    "extrabiblical",
    "pseudepigrapha",
    "oracc",
    "tlhdig",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_fixture(data: dict[str, Any]) -> None:
    corpora = set(data["corpora"])
    if corpora != REQUIRED_CORPORA:
        raise ValueError(f"fixture corpora mismatch: {sorted(corpora)}")

    ids: set[str] = set()
    for row in data["mappings"]:
        if row["id"] in ids:
            raise ValueError(f"duplicate mapping id: {row['id']}")
        ids.add(row["id"])
        if row["corpus"] not in REQUIRED_CORPORA:
            raise ValueError(f"unknown corpus in {row['id']}")
        if row["assessment"] not in ASSESSMENTS:
            raise ValueError(f"unknown assessment in {row['id']}")
        if not isinstance(row["weight"], int) or row["weight"] <= 0:
            raise ValueError(f"invalid weight in {row['id']}")
        if row["assessment"] in NO_TARGET and row.get("target") is not None:
            raise ValueError(f"{row['id']} must not expose a direct target")
        if row["assessment"] not in NO_TARGET and not row.get("target"):
            raise ValueError(f"{row['id']} requires a target")
        if not row.get("plan"):
            raise ValueError(f"{row['id']} lacks a native plan fragment")


def weighted_summary(data: dict[str, Any]) -> dict[str, Any]:
    rows = data["mappings"]
    total_weight = sum(row["weight"] for row in rows)
    target_weight = sum(row["weight"] for row in rows if row.get("target"))

    assessments = Counter(row["assessment"] for row in rows)
    by_profile: dict[str, dict[str, Any]] = {}
    for profile in sorted({row["profile"] for row in rows}):
        selected = [row for row in rows if row["profile"] == profile]
        weight = sum(row["weight"] for row in selected)
        mapped = sum(row["weight"] for row in selected if row.get("target"))
        by_profile[profile] = {
            "rows": len(selected),
            "weight": weight,
            "target_weight": mapped,
            "target_weight_pct": round(mapped * 100 / weight, 1) if weight else 0.0,
        }

    return {
        "mapping_rows": len(rows),
        "weighted_total": total_weight,
        "weighted_target": target_weight,
        "weighted_target_pct": round(target_weight * 100 / total_weight, 1),
        "assessment_rows": dict(sorted(assessments.items())),
        "profiles": by_profile,
    }


def inventory_keys(inventory: dict[str, Any]) -> set[str]:
    keys = {f"node_type:{name}" for name in inventory.get("node_types", {})}
    keys |= {f"node_feature:{name}" for name in inventory.get("node_features", {})}
    keys |= {f"edge_feature:{name}" for name in inventory.get("edge_features", {})}
    return keys


def raw_schema_consideration(data: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    rows_by_corpus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["mappings"]:
        rows_by_corpus[row["corpus"]].append(row)

    result: dict[str, Any] = {}
    for corpus, meta in sorted(data["corpora"].items()):
        inventory_rel = meta.get("inventory")
        if not inventory_rel:
            result[corpus] = {
                "status": "not-machine-inventoried-in-r005-generated-set",
                "considered_refs": sorted(
                    {
                        ref
                        for row in rows_by_corpus[corpus]
                        for ref in row.get("inventory_refs", [])
                    }
                ),
            }
            continue

        path = repo_root / inventory_rel
        if not path.exists():
            result[corpus] = {"status": "inventory-file-missing", "path": inventory_rel}
            continue

        inventory = load_json(path)
        available = inventory_keys(inventory)
        considered = {
            ref
            for row in rows_by_corpus[corpus]
            for ref in row.get("inventory_refs", [])
            if ref.startswith(("node_type:", "node_feature:", "edge_feature:"))
        }
        matched = considered & available
        result[corpus] = {
            "status": "ok",
            "inventory_items": len(available),
            "considered_inventory_items": len(matched),
            "considered_pct": round(len(matched) * 100 / len(available), 1)
            if available
            else 0.0,
            "considered_refs": sorted(matched),
            "fixture_refs_not_in_inventory": sorted(considered - available),
        }
    return result


def compile_queries(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows_by_corpus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["mappings"]:
        rows_by_corpus[row["corpus"]].append(row)

    output: list[dict[str, Any]] = []
    for query in data["queries"]:
        targets = query.get("targets") or ([query["target"]] if query.get("target") else [])
        compiled: dict[str, Any] = {}
        if targets:
            for corpus, rows in sorted(rows_by_corpus.items()):
                chosen: list[dict[str, Any]] = []
                for target in targets:
                    candidates = [row for row in rows if row.get("target") == target]
                    if not candidates:
                        chosen = []
                        break
                    # Prefer the strongest available reviewed assessment without inventing hierarchy reasoning.
                    rank = {"exact": 0, "close": 1, "broader": 2, "narrower": 3, "related": 4}
                    candidates.sort(key=lambda row: rank.get(row["assessment"], 99))
                    chosen.append(candidates[0])
                if chosen:
                    compiled[corpus] = {
                        "mapping_ids": [row["id"] for row in chosen],
                        "plans": [row["plan"] for row in chosen],
                        "assessments": [row["assessment"] for row in chosen],
                        "authorization": "exact-candidate"
                        if all(row["assessment"] == "exact" for row in chosen)
                        else "approximate-candidate-R016-required",
                    }

        output.append(
            {
                "id": query["id"],
                "intent": query["intent"],
                "targets": targets,
                "compiled": compiled,
                "compiled_corpora": len(compiled),
                "expected_multi_corpus": query["expected_multi_corpus"],
                "reason": query.get("reason"),
            }
        )
    return output


def build_report(data: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    validate_fixture(data)
    queries = compile_queries(data)
    return {
        "schema_version": 1,
        "fixture": weighted_summary(data),
        "raw_schema_consideration": raw_schema_consideration(data, repo_root),
        "queries": queries,
        "multi_corpus_target_queries": sum(
            1 for query in queries if query["targets"] and query["compiled_corpora"] >= 2
        ),
        "policy": {
            "compilability_is_not_execution_authorization": True,
            "approximate_execution_owned_by": "R-016",
            "native_only_is_legitimate": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("docs/research/data/r-011/pilots.json"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_json(args.fixture)
    report = build_report(data, args.repo_root)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
