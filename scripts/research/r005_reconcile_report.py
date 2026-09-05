#!/usr/bin/env python3
"""Reconcile the authoritative R-005 report with its generated evidence path.

This is a narrow, idempotent research migration used to repair wording that predates
the exhaustive pinned inventory generator. It intentionally modifies only exact known
sentences/anchors and fails closed if the report has drifted unexpectedly.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-005-corpus-semantic-census.md"

OLD_CUC = (
    "- CUC's editorial feature value domains should be regenerated from the exact TF "
    "release when a production mapping is designed; README descriptions establish the "
    "categories, but final mapping must enumerate the actual release values rather than "
    "infer them from typography descriptions."
)
NEW_CUC = (
    "- CUC's exact-release observed feature domains are generated and preserved by R-005 "
    "in `docs/research/data/generated/r005/cuc.json`. At pinned 0.2.8, the non-empty "
    "`cert` values are `False` and `True`; the non-empty `emen` values are `excised`, "
    "`missing`, `redundant`, `remark`, and `restored`. The generator records these as an "
    "observed small domain rather than claiming permanent categorical closure. A later "
    "production mapping must separately justify domain closure and ontology relations "
    "while preserving the native release values."
)

METHOD_ANCHOR = (
    "This census inspected corpus data, generated TF feature files, generated census "
    "reports, converter contracts and feature documentation at exact Git commits. "
    "Repository front pages were used only as supplementary explanation. The reproducible "
    "pins are also recorded in [`data/R-005-corpus-pins.json`](data/R-005-corpus-pins.json)."
)
METHOD_ADDITION = (
    METHOD_ANCHOR
    + "\n\nFor every released minimum corpus, `scripts/research/r005_inventory.py` loads the exact "
      "pinned TF artifact and preserves an exhaustive non-warp node/edge feature inventory "
      "under `docs/research/data/generated/r005/`. Those JSON artifacts record feature "
      "metadata/value types, empirical node-type applicability, observed non-empty domains "
      "or large-domain samples/cardinalities, edge direction/value status, corpus pins, and "
      "a deterministic digest over the inspected TF files. Dense empty-string/`None` records "
      "are counted diagnostically but are not semantic domain members or applicability evidence."
)

AC_ANCHOR = "- [x] Recorded exact commits and TF/schema versions."
AC_ADDITION = (
    AC_ANCHOR
    + "\n- [x] Generated exhaustive node/edge feature inventories for every released minimum "
      "corpus at the pinned revisions, including metadata/value type, empirical applicability, "
      "observed non-empty domains/cardinalities, and edge direction/value status."
    + "\n- [x] Classified every relevant apparent cross-corpus match explicitly in "
      "`R-005-candidate-strength-matrix.md` using the required candidate relationship vocabulary."
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one old anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = REPORT.read_text(encoding="utf-8")
    text = replace_once(text, METHOD_ANCHOR, METHOD_ADDITION, "method")
    text = replace_once(text, OLD_CUC, NEW_CUC, "CUC uncertainty")
    text = replace_once(text, AC_ANCHOR, AC_ADDITION, "acceptance trace")
    REPORT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
