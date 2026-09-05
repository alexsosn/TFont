from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-002-ontology-governance.md"
REGISTRY = ROOT / "docs" / "research" / "data" / "R-002-ontology-registry.json"
WORKFLOW = ROOT / ".github" / "workflows" / "r002-report-validation.yml"


class R002AuthoritativeReportTests(unittest.TestCase):
    def test_formal_mapping_assessment_is_separate_from_rdf_relation(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn(
            "Approximate mappings use SKOS mapping relations, with the corpus-native assertion remaining authoritative.",
            text,
        )
        self.assertIn("mapping assessment", text.lower())
        self.assertIn("publication relation", text.lower())
        self.assertIn("rdfs:subClassOf", text)
        self.assertIn("skos:exactMatch", text)
        self.assertIn("genuinely", text.lower())
        self.assertIn("skos", text.lower())

    def test_owl_targets_are_not_shown_with_skos_mapping_predicates(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("skos:broadMatch olia:", text)
        self.assertIn("publication_relation: none", text)
        self.assertIn("target: olia:", text)

    def test_mapping_assessment_direction_is_explicit(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("`broader` means the target is broader than the native/source concept", text)
        self.assertIn("`narrower` means the target is narrower than the native/source concept", text)

    def test_saws_license_is_not_invented(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("SAWS | v2.1 model; CC BY-NC-SA 3.0 project licensing", text)
        self.assertNotIn(
            "The published project materials are under **CC BY-NC-SA 3.0**, which conflicts",
            text,
        )
        self.assertNotIn("SAWS licensing is non-commercial", text)
        self.assertIn("license", text.lower())
        self.assertIn("not established", text.lower())

    def test_web_annotation_is_optional_not_core(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("SKOS, PROV-O, Web Annotation; SHACL 1.0", text)
        self.assertIn("optional publication/targeting", text.lower())

    def test_apparatus_domain_vocabulary_is_deferred(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn(
            "The R-005 evidence indicates one recurrent gap large enough to justify an initial small TFont vocabulary",
            text,
        )
        self.assertNotIn("Proposed conceptual scope for the later design ticket:", text)
        self.assertNotIn(
            "This is the strongest driver for the minimal TFont apparatus vocabulary.", text
        )
        self.assertNotIn(
            "TFont local apparatus concepts for variation units, readings, attestation and explicit absence;",
            text,
        )
        self.assertNotIn(
            "a deliberately small TFont apparatus vocabulary is justified", text
        )
        self.assertIn("do not mint", text.lower())
        self.assertIn("pseudepigrapha-tf", text.lower())
        self.assertIn("second independent corpus", text.lower())
        self.assertIn("native/profile-local", text.lower())

    def test_main_report_records_r005_as_accepted_dependency(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn(
            "merge is blocked on independent acceptance of R-005 (#7)", text
        )
        self.assertIn("R-005 accepted", text)
        self.assertIn("48c8bd78d0c3a0501b2fdec6946db5df90517bdb", text)

    def test_main_report_records_r001_as_accepted_dependency(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("R-001 accepted", text)
        self.assertIn("68b88a820f5519ad65d46b732679a6278e9ca3c9", text)
        self.assertIn("a22a95084a1518882d1e3e87d10e9757121f106d", text)

    def test_machine_registry_matches_reconciled_policy(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        candidates = {item["id"]: item for item in data["candidates"]}

        self.assertEqual(candidates["prov-o"]["use_mode"], "core")
        self.assertEqual(candidates["shacl"]["use_mode"], "validation-standard")

        web_annotation = candidates["web-annotation"]
        self.assertEqual(web_annotation["use_mode"], "optional-publication-targeting")

        saws = candidates["saws"]
        self.assertIn("not established", saws["license"].lower())
        self.assertNotIn("non-commercial", saws["redistribution"].lower())
        self.assertNotIn("nc licensing", saws["overlap"].lower())

        cao = candidates["cao"]
        self.assertNotIn("minimal tfont apparatus vocabulary", cao["overlap"].lower())
        self.assertIn("native/profile-local", cao["overlap"].lower())
        self.assertIn("second independent corpus", cao["overlap"].lower())

    def test_validation_workflow_tracks_machine_registry(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/research/data/R-002-ontology-registry.json", workflow)


if __name__ == "__main__":
    unittest.main()
