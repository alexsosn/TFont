#!/usr/bin/env python3
"""Measure the non-production R-011 ontology-mapped pilot fixture.

The report deliberately separates:
1. agent-useful weighted mapping-row coverage;
2. raw native schema coverage, including explicitly bounded values;
3. common-target query-plan compilability plus native/non-executable probes.

Fresh adversarial-review corrections live in mapping-overrides.json and are
applied before every measurement. Approximate compilation is not execution
authorization; R-016 owns that policy.
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

DEFAULT_FIXTURE = Path("docs/research/data/r-011/pilots.json")
DEFAULT_OVERRIDES = Path("docs/research/data/r-011/mapping-overrides.json")
DEFAULT_RAW_POLICY = Path("docs/research/data/r-011/raw-schema-policy.json")
DEFAULT_QUERY_SUITE = Path("docs/research/data/r-011/query-suite.json")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_mapping_overrides(
    data: dict[str, Any], overrides: dict[str, Any]
) -> dict[str, Any]:
    """Return the exact effective research fixture used by all measurements."""
    result = copy.deepcopy(data)
    rows = {row["id"]: row for row in result["mappings"]}

    excluded = set(overrides.get("exclude_mapping_ids", []))
    unknown_excluded = excluded - set(rows)
    if unknown_excluded:
        raise ValueError(f"mapping overrides exclude unknown ids: {sorted(unknown_excluded)}")

    for mapping_id, patch in overrides.get("mapping_overrides", {}).items():
        if mapping_id not in rows:
            raise ValueError(f"mapping override references unknown id: {mapping_id}")
        rows[mapping_id].update(copy.deepcopy(patch))

    result["mappings"] = [
        row for row in result["mappings"] if row["id"] not in excluded
    ]
    result["effective_overrides"] = {
        "excluded_mapping_ids": sorted(excluded),
        "overridden_mapping_ids": sorted(overrides.get("mapping_overrides", {})),
    }
    return result


def validate_fixture(data: dict[str, Any]) -> None:
    if set(data["corpora"]) != REQUIRED_CORPORA:
        raise ValueError("fixture must define exactly the seven required corpora")

    ids: set[str] = set()
    for corpus, meta in data["corpora"].items():
        revision = meta.get("revision")
        if not isinstance(revision, str) or len(revision) < 7:
            raise ValueError(f"corpus {corpus} lacks an exact revision pin")

    for row in data["mappings"]:
        mapping_id = row.get("id")
        if not mapping_id or mapping_id in ids:
            raise ValueError(f"invalid/duplicate mapping id: {mapping_id}")
        ids.add(mapping_id)
        if row.get("corpus") not in REQUIRED_CORPORA:
            raise ValueError(f"unknown corpus in {mapping_id}")
        assessment = row.get("assessment")
        if assessment not in ASSESSMENTS:
            raise ValueError(f"unknown assessment in {mapping_id}")
        if not isinstance(row.get("weight"), int) or row["weight"] <= 0:
            raise ValueError(f"invalid weight in {mapping_id}")
        if assessment in NO_TARGET and row.get("target") is not None:
            raise ValueError(f"{mapping_id} must not expose a direct target")
        if assessment not in NO_TARGET and not row.get("target"):
            raise ValueError(f"{mapping_id} requires a target")
        if not row.get("plan"):
            raise ValueError(f"{mapping_id} lacks a native plan fragment")


def weighted_summary(data: dict[str, Any]) -> dict[str, Any]:
    rows = data["mappings"]
    total = sum(row["weight"] for row in rows)
    target = sum(row["weight"] for row in rows if row.get("target"))
    assessments = Counter(row["assessment"] for row in rows)
    for assessment in ASSESSMENTS:
        assessments.setdefault(assessment, 0)

    profiles: dict[str, dict[str, Any]] = {}
    for profile in sorted({row["profile"] for row in rows}):
        selected = [row for row in rows if row["profile"] == profile]
        weight = sum(row["weight"] for row in selected)
        mapped = sum(row["weight"] for row in selected if row.get("target"))
        profiles[profile] = {
            "rows": len(selected),
            "weight": weight,
            "target_weight": mapped,
            "target_weight_pct": round(mapped * 100 / weight, 1) if weight else 0.0,
        }

    return {
        "mapping_rows": len(rows),
        "weighted_total": total,
        "weighted_target": target,
        "weighted_target_pct": round(target * 100 / total, 1) if total else 0.0,
        "assessment_rows": dict(sorted(assessments.items())),
        "profiles": profiles,
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
    features = inventory.get("node_features", {})
    for feature in bounded_features:
        if feature not in features:
            raise ValueError(f"bounded feature {feature!r} absent from R-005 inventory")
        values = features[feature].get("observed_values")
        if not isinstance(values, list) or not values:
            raise ValueError(f"bounded feature {feature!r} has no explicit observed_values")
        expanded = {_value_key(feature, value) for value in values}
        value_keys[feature] = expanded
        keys |= expanded
    return keys, value_keys


def raw_schema_coverage(
    data: dict[str, Any], repo_root: Path, policy: dict[str, Any]
) -> dict[str, Any]:
    if set(policy.get("corpora", {})) != REQUIRED_CORPORA:
        raise ValueError("raw-schema policy must define all seven required corpora")

    rows = {row["id"]: row for row in data["mappings"]}
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
            available, value_families = _machine_inventory_keys(
                load_json(path), corpus_policy.get("bounded_features", [])
            )
            denominator_basis = "generated-r005-inventory"
            denominator_quality = "machine-exhaustive-for-r005-nonwarp-inventory"
        else:
            available = set(corpus_policy.get("manual_items", []))
            if not available:
                raise ValueError(f"curated raw denominator missing for {corpus}")
            denominator_basis = corpus_policy.get("denominator_basis", "curated baseline")
            denominator_quality = "curated-r005-baseline-not-exhaustive-generated-inventory"

        refs_by_mapping: dict[str, set[str]] = {}
        for mapping_id, refs in corpus_policy.get("mapping_refs", {}).items():
            row = rows.get(mapping_id)
            if row is None:
                raise ValueError(f"raw policy references unknown effective mapping id: {mapping_id}")
            if row["corpus"] != corpus:
                raise ValueError(f"raw policy mapping {mapping_id} belongs to {row['corpus']}")
            refs_by_mapping.setdefault(mapping_id, set()).update(refs)

        for mapping_id, families in corpus_policy.get("mapping_value_families", {}).items():
            row = rows.get(mapping_id)
            if row is None or row["corpus"] != corpus:
                raise ValueError(f"invalid value-family mapping reference: {mapping_id}")
            for feature in families:
                if feature not in value_families:
                    raise ValueError(f"value-family {feature!r} is not an expanded feature")
                refs_by_mapping.setdefault(mapping_id, set()).update(value_families[feature])

        referenced = set().union(*refs_by_mapping.values()) if refs_by_mapping else set()
        invalid = referenced - available
        if invalid:
            raise ValueError(
                f"raw policy refs absent from {corpus} denominator: {sorted(invalid)}"
            )

        mappings_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for mapping_id, refs in refs_by_mapping.items():
            for ref in refs:
                mappings_by_item[ref].append(rows[mapping_id])

        reviewed = set(mappings_by_item)
        common = {
            ref
            for ref, mapped_rows in mappings_by_item.items()
            if any(row.get("target") for row in mapped_rows)
        }
        assessment_items = Counter()
        for mapped_rows in mappings_by_item.values():
            strengths = sorted({row["assessment"] for row in mapped_rows})
            label = strengths[0] if len(strengths) == 1 else "mixed:" + "+".join(strengths)
            assessment_items[label] += 1

        total = len(available)
        value_items = sum(item.startswith("node_value:") for item in available)
        reviewed_count = len(reviewed)
        common_count = len(common)
        unreviewed_count = total - reviewed_count
        result[corpus] = {
            "status": "ok",
            "denominator_basis": denominator_basis,
            "denominator_quality": denominator_quality,
            "raw_items": total,
            "bounded_value_items": value_items,
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
            bounded_value_items=value_items,
            reviewed_items=reviewed_count,
            common_target_items=common_count,
            unreviewed_items=unreviewed_count,
        )
        basis_counts[denominator_quality] += 1

    total = aggregate["raw_items"]
    aggregate_result = dict(aggregate)
    aggregate_result["reviewed_pct"] = (
        round(aggregate["reviewed_items"] * 100 / total, 1) if total else 0.0
    )
    aggregate_result["common_target_pct"] = (
        round(aggregate["common_target_items"] * 100 / total, 1) if total else 0.0
    )
    aggregate_result["denominator_quality_corpora"] = dict(sorted(basis_counts.items()))
    return {"corpora": result, "aggregate": aggregate_result}


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
        if query["id"] in by_id:
            raise ValueError(f"duplicate supplemental query id: {query['id']}")
        clone = copy.deepcopy(query)
        queries.append(clone)
        by_id[clone["id"]] = clone
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
        if not (query.get("target") or query.get("targets") or query.get("native_roles")):
            raise ValueError(f"query {query_id} lacks target(s) or native roles")
        for probe in query.get("probes", []):
            if probe.get("corpus") not in REQUIRED_CORPORA:
                raise ValueError(f"query {query_id} has invalid probe corpus")
            if probe.get("mapping_strength") not in ASSESSMENTS:
                raise ValueError(f"query {query_id} probe has invalid mapping strength")
            if not probe.get("capability") or not isinstance(probe.get("native_selectors"), list):
                raise ValueError(f"query {query_id} probe is incomplete")
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
    rank = {"exact": 0, "close": 1, "broader": 2, "narrower": 3, "related": 4}
    output: list[dict[str, Any]] = []

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
                if not chosen:
                    continue
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
                    f"query {query['id']} defines probe for already compiled corpus {corpus}"
                )
            outcomes[corpus] = {
                "capability": probe["capability"],
                "mapping_strength": probe["mapping_strength"],
                "native_selectors": copy.deepcopy(probe["native_selectors"]),
                "execution": "non-executable-common-pivot",
                "reason": probe["reason"],
            }

        output.append(
            {
                "id": query["id"],
                "intent": query["intent"],
                "targets": targets,
                "compiled": compiled,
                "compiled_corpora": len(compiled),
                "expected_multi_corpus": query.get("expected_multi_corpus", False),
                "reason": query.get("reason"),
                "capability_outcomes": outcomes,
            }
        )
    return output


def build_report(
    data: dict[str, Any],
    repo_root: Path,
    raw_policy: dict[str, Any],
    query_supplement: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    effective = apply_mapping_overrides(data, overrides)
    validate_fixture(effective)
    queries = compile_queries(effective, _merge_query_suite(effective, query_supplement))

    recurrent_gap_queries = [
        query["id"]
        for query in queries
        if query["compiled_corpora"] == 0 and len(query["capability_outcomes"]) >= 2
    ]
    complementary_rows = sum(
        1
        for row in effective["mappings"]
        if isinstance(row.get("targets"), list) and len(row["targets"]) > 1
    )

    return {
        "schema_version": 2,
        "effective_fixture": effective.get("effective_overrides", {}),
        "fixture": weighted_summary(effective),
        "raw_schema_coverage": raw_schema_coverage(effective, repo_root, raw_policy),
        "queries": queries,
        "multi_corpus_target_queries": sum(
            query["compiled_corpora"] >= 2 for query in queries if query["targets"]
        ),
        "recurrent_gap_queries": recurrent_gap_queries,
        "recurrent_gap_query_count": len(recurrent_gap_queries),
        "complementary_projection_rows": complementary_rows,
        "policy": {
            "compilability_is_not_execution_authorization": True,
            "approximate_execution_owned_by": "R-016",
            "native_only_is_legitimate": True,
            "raw_unreviewed_items_are_not_native_only": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--mapping-overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--raw-policy", type=Path, default=DEFAULT_RAW_POLICY)
    parser.add_argument("--query-suite", type=Path, default=DEFAULT_QUERY_SUITE)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        load_json(args.fixture),
        args.repo_root,
        load_json(args.raw_policy),
        load_json(args.query_suite),
        load_json(args.mapping_overrides),
    )
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
