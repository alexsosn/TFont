from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "research" / "R-002-ontology-governance.md"


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

    def test_saws_license_is_not_invented(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("SAWS | v2.1 model; CC BY-NC-SA 3.0 project licensing", text)
        self.assertNotIn(
            "The published project materials are under **CC BY-NC-SA 3.0**, which conflicts",
            text,
        )
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
        self.assertIn("do not mint", text.lower())
        self.assertIn("pseudepigrapha-tf", text.lower())
        self.assertIn("second independent corpus", text.lower())

    def test_main_report_records_r005_as_accepted_dependency(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertNotIn(
            "merge is blocked on independent acceptance of R-005 (#7)", text
        )
        self.assertIn("R-005 accepted", text)
        self.assertIn("48c8bd78d0c3a0501b2fdec6946db5df90517bdb", text)


if __name__ == "__main__":
    unittest.main()
