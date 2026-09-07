from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "docs/research/data/r-011/pilots.json"
RAW_POLICY = ROOT / "docs/research/data/r-011/raw-schema-policy.json"
QUERY_SUITE = ROOT / "docs/research/data/r-011/query-suite.json"
SCRIPT = ROOT / "scripts/research/r011_measure.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("r011_measure", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inputs():
    return (
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        json.loads(RAW_POLICY.read_text(encoding="utf-8")),
        json.loads(QUERY_SUITE.read_text(encoding="utf-8")),
    )


def _queries(module, data, supplement):
    merged = module._merge_query_suite(data, supplement)
    return {query["id"]: query for query in module.compile_queries(data, merged)}


def test_r011_fixture_contract() -> None:
    data, _, _ = _inputs()
    module = _load_script()
    module.validate_fixture(data)

    summary = module.weighted_summary(data)
    assert summary["mapping_rows"] == 53
    assert summary["weighted_total"] == 109
    assert summary["weighted_target"] == 69
    assert summary["weighted_target_pct"] == 63.3

    assessments = summary["assessment_rows"]
    assert assessments["exact"] == 15
    assert assessments["close"] == 12
    assert assessments["ambiguous"] == 3
    assert assessments["native-only"] == 22
    assert assessments["unsupported"] == 1
    assert assessments["broader"] == 0
    assert assessments["narrower"] == 0
    assert assessments["related"] == 0


def test_r011_raw_schema_coverage_includes_bounded_values() -> None:
    data, policy, _ = _inputs()
    module = _load_script()
    raw = module.raw_schema_coverage(data, ROOT, policy)

    for corpus in module.REQUIRED_CORPORA:
        result = raw["corpora"][corpus]
        assert result["status"] == "ok"
        assert result["raw_items"] > 0
        assert result["reviewed_items"] > 0
        assert result["common_target_items"] <= result["reviewed_items"]
        assert result["unreviewed_items"] == result["raw_items"] - result["reviewed_items"]

    for corpus in ("bhsa", "cuc", "syriac", "extrabiblical", "tlhdig"):
        result = raw["corpora"][corpus]
        assert result["denominator_quality"] == "machine-exhaustive-for-r005-nonwarp-inventory"
        assert result["bounded_value_items"] > 0

    for corpus in ("pseudepigrapha", "oracc"):
        assert (
            raw["corpora"][corpus]["denominator_quality"]
            == "curated-r005-baseline-not-exhaustive-generated-inventory"
        )

    bhsa = raw["corpora"]["bhsa"]
    assert 'node_value:sp="subs"' in bhsa["reviewed_refs"]
    assert "node_feature:sp" not in bhsa["reviewed_refs"]
    assert bhsa["unreviewed_items"] > 0

    aggregate = raw["aggregate"]
    assert aggregate["raw_items"] > aggregate["reviewed_items"]
    assert aggregate["reviewed_items"] >= aggregate["common_target_items"]
    assert aggregate["bounded_value_items"] > 0
    assert aggregate["denominator_quality_corpora"] == {
        "curated-r005-baseline-not-exhaustive-generated-inventory": 2,
        "machine-exhaustive-for-r005-nonwarp-inventory": 5,
    }


def test_r011_raw_policy_refs_fail_closed() -> None:
    data, policy, _ = _inputs()
    module = _load_script()
    broken = copy.deepcopy(policy)
    broken["corpora"]["bhsa"]["mapping_refs"]["bhsa-pos-noun"].append(
        'node_value:sp="definitely-not-a-native-value"'
    )
    with pytest.raises(ValueError, match="raw policy refs absent"):
        module.raw_schema_coverage(data, ROOT, broken)


def test_r011_query_compilation_contract() -> None:
    data, _, supplement = _inputs()
    module = _load_script()
    by_id = _queries(module, data, supplement)

    assert len(by_id) == 19

    for query_id in (
        "q-noun",
        "q-verb-plural",
        "q-first-person",
        "q-gender",
        "q-lex-entry",
        "q-line",
        "q-physical-object",
    ):
        assert by_id[query_id]["compiled_corpora"] >= 2

    assert by_id["q-noun"]["compiled_corpora"] == 3
    assert by_id["q-verb-plural"]["compiled_corpora"] == 3
    assert by_id["q-first-person"]["compiled_corpora"] == 3
    assert by_id["q-gender"]["compiled_corpora"] == 2
    assert by_id["q-lex-entry"]["compiled_corpora"] == 5
    assert by_id["q-line"]["compiled_corpora"] == 3
    assert by_id["q-physical-object"]["compiled_corpora"] == 3
    assert "pseudepigrapha" not in by_id["q-physical-object"]["compiled"]

    for query_id in (
        "q-apparatus-reading",
        "q-damage",
        "q-period",
        "q-provenience",
        "q-unsafe-stem",
        "q-archaeology-negative",
        "q-lemma",
        "q-sense",
        "q-shared-lexical-concept",
        "q-structural-navigation",
        "q-physical-witness-manuscript-fragment",
        "q-material",
    ):
        assert by_id[query_id]["compiled_corpora"] == 0
        assert by_id[query_id]["capability_outcomes"]

    assert len(by_id["q-lemma"]["capability_outcomes"]) == 5
    assert len(by_id["q-structural-navigation"]["capability_outcomes"]) == 3
    assert set(by_id["q-physical-witness-manuscript-fragment"]["capability_outcomes"]) == {
        "pseudepigrapha",
        "tlhdig",
    }
    assert set(by_id["q-material"]["capability_outcomes"]) == {"oracc"}


def test_r011_every_reported_query_outcome_is_explainable() -> None:
    data, _, supplement = _inputs()
    module = _load_script()
    by_id = _queries(module, data, supplement)

    for query in by_id.values():
        for outcome in query["capability_outcomes"].values():
            assert outcome["capability"]
            assert outcome["mapping_strength"]
            assert isinstance(outcome["native_selectors"], list)
            assert outcome["execution"] in {
                "exact-candidate",
                "approximate-candidate-R016-required",
                "non-executable-common-pivot",
            }
            assert outcome["reason"]


def test_r011_approximate_compilation_is_not_authorization() -> None:
    data, _, supplement = _inputs()
    module = _load_script()
    by_id = _queries(module, data, supplement)

    assert all(
        plan["authorization"] == "exact-candidate"
        for plan in by_id["q-noun"]["compiled"].values()
    )
    assert all(
        plan["authorization"] == "approximate-candidate-R016-required"
        for plan in by_id["q-line"]["compiled"].values()
    )
    assert all(
        plan["authorization"] == "approximate-candidate-R016-required"
        for corpus, plan in by_id["q-lex-entry"]["compiled"].items()
        if corpus != "bhsa"
    )


def test_r011_pseudepigrapha_manuscript_is_not_physical_by_default() -> None:
    data, _, _ = _inputs()
    row = next(row for row in data["mappings"] if row["id"] == "pseudo-manuscript")
    assert row["assessment"] == "native-only"
    assert row["target"] is None


def test_r011_tlh_surface_is_not_written_text_segment() -> None:
    data, _, _ = _inputs()
    row = next(row for row in data["mappings"] if row["id"] == "tlh-surface")
    assert row["assessment"] == "native-only"
    assert row["target"] is None
