from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tfont.digests import evidence_record_digest
from tfont.semantic_digest_v2 import mapping_semantic_digest_v2, projection_semantic_digest_v1

ROOT = Path(__file__).resolve().parents[1] / "src" / "tfont" / "resources"
OLIA_REVISION = "d3bd4f1aef9047b33186bfb2a1795401f3f1a4a6"
OLIA_NOUN = "http://purl.org/olia/olia.owl#Noun"
OLIA_DIGEST = "sha256:5983683f27ba524027ffa12a02aead4a115baf9c8933079eabbb4aa71be4e9fd"
OLIA_LICENSE_URI = "https://creativecommons.org/licenses/by/3.0/"

CORPORA = {
    "bhsa": {
        "profile_id": "tfont-bhsa",
        "component_id": "bhsa-tf",
        "component_digest": "sha256:5178414e293a743fc98768abcab5b9cb268e14ad56fd2cfbac544ae2869d2e6f",
        "upstream_revision": "4db00e2157915495e1a4d3d57e41223df24775da",
        "values": ("nmpr", "subs"),
        "execution_shape": "value-set-predicate",
    },
    "syriac": {
        "profile_id": "tfont-syriac",
        "component_id": "syriac-tf",
        "component_digest": "sha256:54a2596d5525f3afb34db0a89d5511e6b8471ce4a93fae4825b22f0945ab62ef",
        "upstream_revision": "bb0eaa7e21b020a26b7566d2e495da9b1f84a919",
        "value": "subs",
        "execution_shape": "value-predicate",
    },
    "extrabiblical": {
        "profile_id": "tfont-extrabiblical",
        "component_id": "extrabiblical-tf",
        "component_digest": "sha256:d0ca9bdf90bfdefe19861c2c68e91071650ed511b8a79270490238b30274aee0",
        "upstream_revision": "9a56288e6777bad6328856acf055c780e65dd5d9",
        "values": ("nmpr", "subs"),
        "execution_shape": "value-set-predicate",
    },
}
LINKSYR_REVISION = "3ba42432b0ed95c1ad65eb06865c3a5f7175f8b6"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evidence(
    evidence_id: str,
    *,
    kind: str,
    source_uri: str,
    source_revision: str,
    reviewed_content: dict[str, Any],
    license_ref: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "evidence_id": evidence_id,
        "kind": kind,
        "source_uri": source_uri,
        "source_revision": source_revision,
        "content_mode": "normalized-record",
        "reviewed_content": reviewed_content,
        "content_digest": "pending",
    }
    if license_ref is not None:
        row["license_ref"] = license_ref
    row["content_digest"] = evidence_record_digest(row)
    return row


def binding(row: dict[str, Any]) -> dict[str, str]:
    return {"evidence_id": row["evidence_id"], "content_digest": row["content_digest"]}


def native_binding(corpus_id: str) -> dict[str, Any]:
    spec = CORPORA[corpus_id]
    row: dict[str, Any] = {
        "component_id": spec["component_id"],
        "node_type": "word",
        "feature": "sp",
        "execution_shape": spec["execution_shape"],
    }
    if spec["execution_shape"] == "value-set-predicate":
        row["values"] = list(spec["values"])
    else:
        row["value"] = spec["value"]
    return row


def dependencies(corpus_id: str, evidence_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    spec = CORPORA[corpus_id]
    if corpus_id == "bhsa":
        value_evidence = {
            "nmpr": "evidence:bhsa:word-sp-noun-codes",
            "subs": "evidence:bhsa:word-sp-noun-codes",
        }
    elif corpus_id == "syriac":
        value_evidence = {"subs": "evidence:syriac:word-sp-substantive"}
    else:
        value_evidence = {
            "nmpr": "evidence:extrabiblical:word-sp-enum",
            "subs": "evidence:extrabiblical:word-sp-enum",
        }
    values = spec.get("values", (spec.get("value"),))
    rows = []
    for value in values:
        evidence_row = evidence_by_id[value_evidence[value]]
        rows.append(
            {
                "dependency_id": f"dep:{corpus_id}:word-sp:{value}",
                "component_id": spec["component_id"],
                "kind": "native-value-present",
                "assertion": {
                    "node_type": "word",
                    "feature": "sp",
                    "value": value,
                    "value_semantics": "semantic",
                },
                "evidence": [binding(evidence_row)],
            }
        )
    return rows


def profile(corpus_id: str, dependency_rows: list[dict[str, Any]]) -> dict[str, Any]:
    spec = CORPORA[corpus_id]
    return {
        "schema_version": 2,
        "profile_id": spec["profile_id"],
        "profile_version": "0.1.0",
        "semantic_domains": ["linguistic"],
        "profile_catalog_version": 1,
        "profiles": ["linguistic"],
        "capabilities": ["linguistic.part-of-speech"],
        "parent_component_manifest": "parent/expected-components.json",
        "required_components": [spec["component_id"]],
        "ontology_locks": ["olia-reference-model"],
        "mapping_sources": ["mappings/noun.json"],
        "dependency_contract_version": 1,
        "dependencies": dependency_rows,
        "minimum_tfont_runtime": "0.1.0",
        "license": "MIT",
    }


def mapping(corpus_id: str, evidence_rows: list[dict[str, Any]], dependency_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_bindings = [binding(row) for row in evidence_rows]
    execution = native_binding(corpus_id)
    projection: dict[str, Any] = {
        "projection_id": f"projection:{corpus_id}:olia-noun",
        "target": OLIA_NOUN,
        "reference_kind": "semantic-pivot",
        "query_role": "semantic-constraint",
        "formal_kind": "class",
        "semantic_role": "annotation-value",
        "profile_id": "linguistic",
        "capability_id": "linguistic.part-of-speech",
        "assessment": "exact",
        "ontology_lock": "olia-reference-model",
        "publication_relation": None,
        "native_execution_binding": execution,
        "evidence": evidence_bindings,
        "projection_semantic_digest": "pending",
    }
    projection["projection_semantic_digest"] = projection_semantic_digest_v1(projection)
    row: dict[str, Any] = {
        "mapping_id": f"mapping:{corpus_id}:olia-noun",
        "corpus_id": corpus_id,
        "native_binding": native_binding(corpus_id),
        "native_dependencies": [dependency["dependency_id"] for dependency in dependency_rows],
        "profiles": ["linguistic"],
        "capabilities": ["linguistic.part-of-speech"],
        "native_state": "positive",
        "projections": [projection],
        "ambiguous_candidates": [],
        "external_references": [],
        "evidence": evidence_bindings,
        "mapping_semantic_digest": "pending",
        "rationale": "Reviewed production projection for the v0.1 OLiA Noun semantic slice; see I-009 research and implementation PR #156.",
    }
    row["mapping_semantic_digest"] = mapping_semantic_digest_v2(row)
    return {"schema_version": 2, "mappings": [row]}


def main() -> None:
    olia = evidence(
        "evidence:olia:noun-hierarchy",
        kind="ontology-definition",
        source_uri=f"https://raw.githubusercontent.com/acoli-repo/olia/{OLIA_REVISION}/owl/core/olia.owl",
        source_revision=OLIA_REVISION,
        reviewed_content={
            "target": OLIA_NOUN,
            "direct_subclasses_include": [
                "http://purl.org/olia/olia.owl#CommonNoun",
                "http://purl.org/olia/olia.owl#ProperNoun",
            ],
            "snapshot_digest": OLIA_DIGEST,
            "license_uri": OLIA_LICENSE_URI,
        },
        license_ref=OLIA_LICENSE_URI,
    )
    bhsa = evidence(
        "evidence:bhsa:word-sp-noun-codes",
        kind="corpus-feature-definition",
        source_uri="https://raw.githubusercontent.com/ETCBC/bhsa/4db00e2157915495e1a4d3d57e41223df24775da/docs/features/sp.md",
        source_revision="4db00e2157915495e1a4d3d57e41223df24775da",
        reviewed_content={
            "feature": "sp",
            "feature_semantics": "part-of-speech",
            "documented_node_types": ["word", "lex"],
            "values": {"subs": "noun", "nmpr": "proper noun"},
            "production_scope": {"node_type": "word", "selected_values": ["nmpr", "subs"]},
        },
    )
    syriac_sp = evidence(
        "evidence:syriac:word-sp-substantive",
        kind="corpus-grammar-definition",
        source_uri=f"https://raw.githubusercontent.com/ETCBC/linksyr/{LINKSYR_REVISION}/data/lib/syriac/word_grammar",
        source_revision=LINKSYR_REVISION,
        reviewed_content={
            "feature": "sp",
            "feature_semantics": "part of speech",
            "value": "subs",
            "value_semantics": "substantive",
        },
    )
    syriac_proper = evidence(
        "evidence:syriac:proper-inside-subs",
        kind="corpus-lexicon-encoding",
        source_uri=f"https://raw.githubusercontent.com/ETCBC/linksyr/{LINKSYR_REVISION}/data/lib/syriac/lexicon",
        source_revision=LINKSYR_REVISION,
        reviewed_content={
            "encoding": "sp=subs:ls=prop",
            "part_of_speech_value": "subs",
            "lexical_semantics_value": "prop",
            "lexical_semantics": "proper noun",
        },
    )
    extra_enum = evidence(
        "evidence:extrabiblical:word-sp-enum",
        kind="corpus-source-enumeration",
        source_uri="https://raw.githubusercontent.com/ETCBC/extrabiblical/9a56288e6777bad6328856acf055c780e65dd5d9/source/0.2/extraBiblical.mql.bz2",
        source_revision="9a56288e6777bad6328856acf055c780e65dd5d9",
        reviewed_content={
            "node_type": "word",
            "feature": "sp",
            "source_type": "part_of_speech_t",
            "values": {"subs": 2, "nmpr": 3},
        },
    )
    extra_authority = evidence(
        "evidence:extrabiblical:feature-authority",
        kind="corpus-provenance",
        source_uri="https://raw.githubusercontent.com/ETCBC/extrabiblical/9a56288e6777bad6328856acf055c780e65dd5d9/README.md",
        source_revision="9a56288e6777bad6328856acf055c780e65dd5d9",
        reviewed_content={
            "resource_family": "ETCBC/BHSA",
            "conversion": "Conversion of some extra-biblical writings from ETCBC-encoded texts",
            "feature_documentation": "BHSA core data and feature documentation",
        },
    )

    evidence_by_id = {
        row["evidence_id"]: row
        for row in (olia, bhsa, syriac_sp, syriac_proper, extra_enum, extra_authority)
    }

    olia_root = ROOT / "ontologies" / "olia" / OLIA_REVISION
    write_json(
        olia_root / "lock.json",
        {
            "lock_id": "olia-reference-model",
            "ontology_id": "olia",
            "support_tier": "supported-profile",
            "term_namespace": "http://purl.org/olia/olia.owl#",
            "release": f"snapshot-{OLIA_REVISION}",
            "upstream_release_status": "git-snapshot",
            "source_uri": f"https://raw.githubusercontent.com/acoli-repo/olia/{OLIA_REVISION}/owl/core/olia.owl",
            "source_revision": OLIA_REVISION,
            "content_digest": OLIA_DIGEST,
            "license": "CC-BY-3.0",
            "redistribution_policy": "redistributable-with-attribution",
            "snapshot_artifact": f"resources/ontologies/olia/{OLIA_REVISION}/olia.owl",
            "terms_used": [OLIA_NOUN],
        },
    )
    write_json(olia_root / "noun-evidence.json", olia)
    (olia_root / "ATTRIBUTION.txt").write_text(
        "OLiA – Ontologies of Linguistic Annotation\n"
        "Reference Model snapshot: owl/core/olia.owl\n"
        f"Source: https://github.com/acoli-repo/olia\nRevision: {OLIA_REVISION}\n"
        "License: Creative Commons Attribution 3.0 Unported (CC BY 3.0)\n"
        f"License URI: {OLIA_LICENSE_URI}\n"
        "The bundled olia.owl and LICENSE.data are third-party OLiA data. "
        "ontoTF-authored mappings and metadata remain under the repository MIT license.\n",
        encoding="utf-8",
    )

    corpus_evidence = {
        "bhsa": [bhsa, olia],
        "syriac": [syriac_sp, syriac_proper, olia],
        "extrabiblical": [extra_enum, extra_authority, bhsa, olia],
    }
    local_evidence_files = {
        "bhsa": [("native-pos.json", bhsa)],
        "syriac": [
            ("native-pos.json", syriac_sp),
            ("proper-noun-encoding.json", syriac_proper),
        ],
        "extrabiblical": [
            ("native-pos-enum.json", extra_enum),
            ("feature-authority.json", extra_authority),
        ],
    }

    for corpus_id, spec in CORPORA.items():
        root = ROOT / "profiles" / corpus_id / "0.1.0"
        deps = dependencies(corpus_id, evidence_by_id)
        write_json(root / "profile.json", profile(corpus_id, deps))
        write_json(
            root / "parent" / "expected-components.json",
            {
                "algorithm": "tfont-parent-components-sha256-v1",
                "components": [
                    {
                        "component_id": spec["component_id"],
                        "kind": "tf-payload",
                        "identity_algorithm": "tfont-tf-files-sha256-v1",
                        "content_digest": spec["component_digest"],
                    }
                ],
            },
        )
        for filename, row in local_evidence_files[corpus_id]:
            write_json(root / "evidence" / filename, row)
        mapping_root = mapping(corpus_id, corpus_evidence[corpus_id], deps)
        write_json(root / "mappings" / "noun.json", mapping_root)
        row = mapping_root["mappings"][0]
        print(
            f"{corpus_id}: mapping={row['mapping_semantic_digest']} "
            f"projection={row['projections'][0]['projection_semantic_digest']}"
        )


if __name__ == "__main__":
    main()
