from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_agents_pins_tf_native_materializer_boundary():
    text = _read("AGENTS.md")
    assert "TF-native runtime boundary" in text
    assert "materializer" in text.lower()
    assert "at least two independent real corpus cases" in text.lower()


def test_r005_supersession_amendment_preserves_history_and_corrects_oracc_boundary():
    text = _read("docs/research/A-001-r005-oracc-zero-span-supersession.md")
    assert "Superseded ORACC zero-span architecture" in text
    assert "R-005 remains unchanged" in text
    assert "ADR-0001-empty-slots-not-sidecars.md" in text
    assert "synthetic/empty" in text


def test_r007_supersession_rejects_generic_external_carrier():
    text = _read("docs/research/A-001-r007-external-carrier-supersession.md")
    assert "R-007 remains unchanged" in text
    assert "generic `sidecar/native-adapter` carrier is superseded" in text
    assert "not a baseline TFont runtime carrier" in text
    assert "Slot" in text
    assert "slotLink" in text
    assert "technicalAnchor" in text


def test_r007_supersession_reconciles_oracc_with_current_tf_architecture():
    text = _read("docs/research/A-001-r007-external-carrier-supersession.md")
    assert "ADR-0001-empty-slots-not-sidecars.md" in text
    assert "synthetic/empty" in text
    assert "materialized" in text.lower()
    assert "ORACC" in text


def test_supersession_states_storage_is_not_semantic_carrier_type():
    text = _read("docs/research/A-001-r007-external-carrier-supersession.md")
    assert "Storage location or source format is not a semantic carrier type" in text


def test_a001_does_not_replace_adapter_with_another_generic_runtime_api():
    research = _read("docs/research/A-001-tf-native-runtime-boundary.md")
    plan = _read("docs/plans/A-001-tf-native-runtime-boundary-plan.md")
    combined = research + "\n" + plan
    assert "No production Python runtime" in combined
    assert "does not own generic ingestion/query adapters" in combined
    assert "two independent real corpus cases" in combined
