#!/usr/bin/env python3
"""Measure the non-production R-011 ontology-mapped pilot fixture.

The report keeps three deliberately separate measurements:

1. agent-useful weighted mapping-row coverage;
2. raw native schema coverage, including explicitly bounded feature values;
3. common-target query-plan compilability plus native/non-executable probes.

This script does not authorize approximate execution. R-016 owns that policy.
"""

from __future__ import annotations

import argparse
import copy
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

DEFAULT_RAW_POLICY = Path("docs/research/data/r-011/raw-schema-policy.json")
DEFAULT_QUERY_SUITE = Path("docs/research/data/r-011/query-suite.json")


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
    for assessment in ASSESSMENTS:
        assessments.setdefault(assessment, 0)

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


def _value_key(feature: str, value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return f"node_value:{feature}={encoded}"


def _machine_inventory_keys(
    inventory: dict[str, Any], bounded_features: list[str]
) -> tuple[set[str], dict[str, set[str]]]:
    keys = {f"node_type:{name}" for name in inventory.get("node_types", {})}
    keys |= {f"node_feature:{name}" for name in inventory.get("node_features", {})}
    keys |= {f"edge_feature:{name}" for name in inventory.get("edge_features", {})}

    value_keys: dict[str, set[str]] = {}
    node_features = inventory.get("node_features", {})
    for feature in bounded_features:
        if feature not in node_features:
            raise ValueError(f"bounded feature {feature!r} absent from R-005 inventory")
        values = node_features[feature].get("observed_values")
        if not isinstance(values, list) or not values:
            raise ValueError(
                f"bounded feature {feature!r} has no explicit observed_values in R-005 inventory"
            )
        expanded = {_value_key(feature, value) for value in values}
        value_keys[feature] = expanded
        keys |= expanded
    return keys, value_keys


def _mapping_rows_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in data["mappings"]}


def raw_schema_coverage(
    data: dict[str, Any], repo_root: Path, policy: dict[str, Any]
) -> dict[str, Any]:
    if set(policy.get("corpora", {})) != REQUIRED_CORPORA:
        raise ValueError("raw-schema policy must define all seven required corpora")

    rows = _mapping_rows_by_id(data)
    result: dict[str, Any] = {}
    aggregate = Counter()
    basis_counts = Counter()

    for corpus in sorted(REQUIRED_CORPORA):
        corpus_policy = policy["corpora"][corpus]
        meta = data["corpora"][corpus]
        inventory_rel = meta.get("inventory")
        value_families: dict[str, set[str]] = {}

        if inventory_rel:
            path = repo_root / inventory_rel
            if not path.exists():
                raise ValueError(f"R-005 inventory file missing for {corpus}: {inventory_rel}")
            inventory = load_json(path)
            available, value_families = _machine_inventory_keys(
                inventory, corpus_policy.get("bounded_features", [])
            )
            denominator_basis = "generated-r005-inventory"
            denominator_quality = "machine-exhaustive-for-r005-nonwarp-inventory"
        else:
            available = set(corpus_policy.get("manual_items", []))
            if not available:
                raise ValueError(f"curated raw denominator missing for {corpus}")
            denominator_basis = corpus_policy.get(
                "denominator_basis", "R-005 curated stress-profile baseline"
            )
            denominator_quality = "curated-r005-baseline-not-exhaustive-generated-inventory"

        refs_by_mapping: dict[str, set[str]] = {}
        for mapping_id, refs in corpus_policy.get("mapping_refs", {}).items():
            row = rows.get(mapping_id)
            if row is None:
                raise ValueError(f"raw policy references unknown mapping id: {mapping_id}")
            if row["corpus"] != corpus:
                raise ValueError(
                    f"raw policy mapping {mapping_id} belongs to {row['corpus']}, not {corpus}"
                )
            refs_by_mapping.setdefault(mapping_id, set()).update(refs)

        for mapping_id, families in corpus_policy.get("mapping_value_families", {}).items():
            row = rows.get(mapping_id)
            if row is None or row["corpus"] != corpus:
                raise ValueError(f"invalid value-family mapping reference: {mapping_id}")
            for feature in families:
                if feature not in value_families:
                    raise ValueError(
                        f"value-family {feature!r} for {mapping_id} is not an expanded bounded feature"
                    )
                refs_by_mapping.setdefault(mapping_id, set()).update(value_families[feature])

        referenced = set().union(*refs_by_mapping.values()) if refs_by_mapping else set()
        invalid_refs = referenced - available
        if invalid_refs:
            raise ValueError(
                f"raw policy refs absent from {corpus} denominator: {sorted(invalid_refs)}"
            )

        mappings_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for mapping_id, refs in refs_by_mapping.items():
            for ref in refs:
                mappings_by_item[ref].append(rows[mapping_id])

        reviewed = set(mappings_by_item)
        common_target = {
            ref
            for ref, mapped_rows in mappings_by_item.items()
            if any(row.get("target") for row in mapped_rows)
        }
        assessment_items = Counter()
        for ref, mapped_rows in mappings_by_item.items():
            strengths = sorted({row["assessment"] for row in mapped_rows})
            label = strengths[0] if len(strengths) == 1 else "mixed:" + "+".join(strengths)
            assessment_items[label] += 1

        total = len(available)
        reviewed_count = len(reviewed)
        common_count = len(common_target)
        unreviewed_count = total - reviewed_count
        value_item_count = sum(1 for item in available if item.startswith("node_value:"))

        result[corpus] = {
            "status": "ok",
            "denominator_basis": denominator_basis,
            "denominator_quality": denominator_quality,
            "raw_items": total,
            "bounded_value_items": value_item_count,
            "reviewed_items": reviewed_count,
            "reviewed_pct": round(reviewed_count * 100 / total, 1) if total else 0.0,
            "common_target_items": common_count,
            "common_target_pct": round(common_count * 100 / total, 1) if total else 0.0,
            "unreviewed_items": unreviewed_count,
            "reviewed_assessment_items": dict(sorted(assessment_items.items())),
            "reviewed_refs": sorted(reviewed),
        }

        aggregate.update(
            raw_items=total,
            bounded_value_items=value_item_count,
            reviewed_items=reviewed_count,
            common_target_items=common_count,
            unreviewed_items=unreviewed_count,
        )
        basis_counts[denominator_quality] += 1

    aggregate_dict = dict(aggregate)
    total = aggregate["raw_items"]
    aggregate_dict["reviewed_pct"] = round(
        aggregate["reviewed_items"] * 100 / total, 1
    ) if total else 0.0
    aggregate_dict["common_target_pct"] = round(
        aggregate["common_target_items"] * 100 / total, 1
    ) if total else 0.0
    aggregate_dict["denominator_quality_corpora"] = dict(sorted(basis_counts.items()))

    return {"corpora": result, "aggregate": aggregate_dict}


def _merge_query_suite(
    data: dict[str, Any], supplement: dict[str, Any]
) -> list[dict[str, Any]]:
    queries = [copy.deepcopy(query) for query in data["queries"]]
    by_id = {query["id"]: query for query in queries}

    for query_id, patch in supplement.get("query_overrides", {}).items():
        if query_id not in by_id:
            raise ValueError(f"query override references unknown query: {query_id}")
        by_id[query_id].update(copy.deepcopy(patch))

    for query in supplement.get("additional_queries", []):
        query_id = query["id"]
        if query_id in by_id:
            raise ValueError(f"duplicate supplemental query id: {query_id}")
        clone = copy.deepcopy(query)
        queries.append(clone)
        by_id[query_id] = clone

    return queries


def validate_queries(queries: list[dict[str, Any]]) -> None:
    ids: set[str] = set()
    for query in queries:
        query_id = query.get("id")
        if not query_id or query_id in ids:
            raise ValueError(f"invalid/duplicate query id: {query_id}")
        ids.add(query_id)
        if not query.get("intent"):
            raise ValueError(f"query {query_id} lacks intent")
        if not (
            query.get("target")
            or query.get("targets")
            or query.get("native_roles")
        ):
            raise ValueError(f"query {query_id} lacks target(s) or native roles")
        for probe in query.get("probes", []):
            if probe.get("corpus") not in REQUIRED_CORPORA:
                raise ValueError(f"query {query_id} has invalid probe corpus")
            if not probe.get("capability"):
                raise ValueError(f"query {query_id} probe lacks capability")
            if probe.get("mapping_strength") not in ASSESSMENTS:
                raise ValueError(f"query {query_id} probe has invalid mapping strength")
            if not isinstance(probe.get("native_selectors"), list):
                raise ValueError(f"query {query_id} probe lacks native selectors list")
            if not probe.get("reason"):
                raise ValueError(f"query {query_id} probe lacks reason")


def _strength_label(rows: list[dict[str, Any]]) -> str:
    strengths = [row["assessment"] for row in rows]
    return strengths[0] if len(set(strengths)) == 1 else "conjunction:" + "+".join(strengths)


def compile_queries(
    data: dict[str, Any], queries: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    rows_by_corpus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["mappings"]:
        rows_by_corpus[row["corpus"]].append(row)

    source_queries = queries if queries is not None else data["queries"]
    validate_queries(source_queries)
    output: list[dict[str, Any]] = []

    rank = {"exact": 0, "close": 1, "broader": 2, "narrower": 3, "related": 4}
    for query in source_queries:
        targets = query.get("targets") or ([query["target"]] if query.get("target") else [])
        compiled: dict[str, Any] = {}
        outcomes: dict[str, Any] = {}

        if targets:
            for corpus, rows in sorted(rows_by_corpus.items()):
                chosen: list[dict[str, Any]] = []
                for target in targets:
                    candidates = [row for row in rows if row.get("target") == target]
                    if not candidates:
                        chosen = []
                        break
                    candidates.sort(key=lambda row: rank.get(row["assessment"], 99))
                    chosen.append(candidates[0])
                if chosen:
                    authorization = (
                        "exact-candidate"
                        if all(row["assessment"] == "exact" for row in chosen)
                        else "approximate-candidate-R016-required"
                    )
                    compiled[corpus] = {
                        "mapping_ids": [row["id"] for row in chosen],
                        "plans": [row["plan"] for row in chosen],
                        "assessments": [row["assessment"] for row in chosen],
                        "authorization": authorization,
                    }
                    outcomes[corpus] = {
                        "capability": "shared-projection",
                        "mapping_strength": _strength_label(chosen),
                        "native_selectors": [row["plan"] for row in chosen],
                        "execution": authorization,
                        "reason": (
                            "All required projections are exact reviewed candidates."
                            if authorization == "exact-candidate"
                            else "Native plan compiles, but R-016 must authorize approximate execution."
                        ),
                    }

        for probe in query.get("probes", []):
            corpus = probe["corpus"]
            if corpus in outcomes:
                raise ValueError(
                    f"query {query['id']} defines native probe for already compiled corpus {corpus}"
                )
            outcomes[corpus] = {
                **copy.deepcopy(probe),
                "execution": "non-executable-common-pivot",
            }
            outcomes[corpus].pop("corpus", None)

        output.append(
            {
                "id": query["id"],
                "intent": query["intent"],
                "targets": targets,
                "native_roles": query.get("native_roles", []),
                "compiled": compiled,
                "compiled_corpora": len(compiled),
                "capability_outcomes": outcomes,
                "expected_multi_corpus": query["expected_multi_corpus"],
                "reason": query.get("reason"),
            }
        )
    return output


def build_report(
    data: dict[str, Any],
    repo_root: Path,
    raw_policy: dict[str, Any],
    query_supplement: dict[str, Any],
) -> dict[str, Any]:
    validate_fixture(data)
    queries = _merge_query_suite(data, query_supplement)
    validate_queries(queries)
    compiled_queries = compile_queries(data, queries)
    return {
        "schema_version": 2,
        "fixture": weighted_summary(data),
        "raw_schema_coverage": raw_schema_coverage(data, repo_root, raw_policy),
        "queries": compiled_queries,
        "query_count": len(compiled_queries),
        "multi_corpus_target_queries": sum(
            1
            for query in compiled_queries
            if query["targets"] and query["compiled_corpora"] >= 2
        ),
        "policy": {
            "compilability_is_not_execution_authorization": True,
            "approximate_execution_owned_by": "R-016",
            "native_only_is_legitimate": True,
            "unreviewed_raw_items_are_not_native_only": True,
            "curated_raw_denominators_are_labelled_non_exhaustive": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture", type=Path, default=Path("docs/research/data/r-011/pilots.json")
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--raw-policy", type=Path, default=DEFAULT_RAW_POLICY)
    parser.add_argument("--query-suite", type=Path, default=DEFAULT_QUERY_SUITE)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_json(args.fixture)
    raw_policy = load_json(args.raw_policy)
    query_supplement = load_json(args.query_suite)
    report = build_report(data, args.repo_root, raw_policy, query_supplement)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
