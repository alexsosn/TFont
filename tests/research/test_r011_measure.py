from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "docs/research/data/r-011/pilots.json"
SCRIPT = ROOT / "scripts/research/r011_measure.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("r011_measure", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_r011_fixture_contract() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    module = _load_script()
    module.validate_fixture(data)

    summary = module.weighted_summary(data)
    assert summary["mapping_rows"] == 53
    assert summary["weighted_total"] == 109
    assert summary["weighted_target"] == 72
    assert summary["weighted_target_pct"] == 66.1

    assessments = summary["assessment_rows"]
    assert assessments["exact"] == 15
    assert assessments["close"] == 14
    assert assessments["ambiguous"] == 3
    assert assessments["native-only"] == 20
    assert assessments["unsupported"] == 1


def test_r011_query_compilation_contract() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    module = _load_script()
    queries = module.compile_queries(data)
    by_id = {query["id"]: query for query in queries}

    for query_id in (
        "q-noun",
        "q-verb-plural",
        "q-first-person",
        "q-lex-entry",
        "q-line",
        "q-physical-object",
    ):
        assert by_id[query_id]["compiled_corpora"] >= 2

    assert by_id["q-noun"]["compiled_corpora"] == 3
    assert by_id["q-verb-plural"]["compiled_corpora"] == 3
    assert by_id["q-first-person"]["compiled_corpora"] == 3
    assert by_id["q-lex-entry"]["compiled_corpora"] == 5
    assert by_id["q-line"]["compiled_corpora"] == 3
    assert by_id["q-physical-object"]["compiled_corpora"] == 4

    for query_id in (
        "q-apparatus-reading",
        "q-damage",
        "q-period",
        "q-provenience",
        "q-unsafe-stem",
        "q-archaeology-negative",
    ):
        assert by_id[query_id]["compiled_corpora"] == 0


def test_r011_approximate_compilation_is_not_authorization() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    module = _load_script()
    by_id = {query["id"]: query for query in module.compile_queries(data)}

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


def test_r011_machine_inventory_refs_fail_closed() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    module = _load_script()
    raw = module.raw_schema_consideration(data, ROOT)

    for corpus in ("bhsa", "cuc", "syriac", "extrabiblical", "tlhdig"):
        assert raw[corpus]["status"] == "ok"
        assert raw[corpus]["fixture_refs_not_in_inventory"] == []
        assert raw[corpus]["considered_inventory_items"] > 0

    assert raw["pseudepigrapha"]["status"] == "not-machine-inventoried-in-r005-generated-set"
    assert raw["oracc"]["status"] == "not-machine-inventoried-in-r005-generated-set"
