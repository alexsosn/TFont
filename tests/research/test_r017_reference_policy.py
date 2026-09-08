import pytest

from scripts.research.r017_reference_policy import (
    ExternalReference,
    identifier_key,
    resolve,
    reverse_index_bucket,
    validate,
)


def test_semantic_pivot_exact_resolves_as_semantic_constraint():
    ref = ExternalReference(
        "noun",
        "semantic-pivot",
        external="olia:Noun",
        native_selector="sp=subs",
        assessment="exact",
        prerequisites_executable=True,
    )
    r = resolve(ref)
    assert r.status == "resolvable"
    assert r.query_role == "semantic-constraint"
    assert reverse_index_bucket(ref) == "semantic"


@pytest.mark.parametrize("assessment", ["close", "broader", "narrower"])
def test_non_exact_semantic_pivot_is_deferred_to_r016(assessment):
    ref = ExternalReference(
        f"semantic-{assessment}",
        "semantic-pivot",
        external="olia:SomeConcept",
        native_selector="feature=value",
        assessment=assessment,
    )
    r = resolve(ref)
    assert r.status == "informative-only"
    assert r.native_selector == ""
    assert "R-016" in r.reason


def test_authority_value_never_uses_semantic_reverse_bucket():
    ref = ExternalReference(
        "aat-clay",
        "authority-value",
        external="aat:300014109",
        native_selector="material=clay",
        authority="Getty AAT",
        assessment="exact",
        prerequisites_executable=True,
    )
    r = resolve(ref)
    assert r.status == "resolvable"
    assert r.query_role == "authority-value-filter"
    assert reverse_index_bucket(ref) == "authority"


@pytest.mark.parametrize("assessment", ["close", "broader", "narrower"])
def test_non_exact_authority_value_is_deferred_to_r016(assessment):
    ref = ExternalReference(
        f"authority-{assessment}",
        "authority-value",
        external="aat:300014109",
        native_selector="material=clay",
        authority="Getty AAT",
        assessment=assessment,
    )
    r = resolve(ref)
    assert r.status == "informative-only"
    assert r.native_selector == ""
    assert "R-016" in r.reason


def test_unmapped_authority_uri_is_informative_only():
    ref = ExternalReference(
        "period",
        "authority-value",
        external="http://n2t.net/ark:/99152/example",
        authority="PeriodO",
        assessment="close",
    )
    assert resolve(ref).status == "informative-only"


@pytest.mark.parametrize("kind", ["semantic-pivot", "authority-value"])
@pytest.mark.parametrize("assessment", ["native-only", "unsupported"])
def test_no_target_states_cannot_be_external_reverse_index_records(kind, assessment):
    ref = ExternalReference(
        f"{kind}-{assessment}",
        kind,
        external="https://example.org/fabricated-target",
        authority="Example Authority" if kind == "authority-value" else "",
        assessment=assessment,
    )
    errors = validate(ref)
    assert any("no-target" in error for error in errors)
    with pytest.raises(ValueError, match="no-target"):
        reverse_index_bucket(ref)


def test_entity_identity_requires_identity_strength():
    ref = ExternalReference("x", "entity-identity", external="https://example.org/object/1")
    assert any("identity strength" in e for e in validate(ref))


def test_same_entity_can_resolve_identity_filter():
    ref = ExternalReference(
        "x",
        "entity-identity",
        external="https://example.org/object/1",
        identity_strength="same-entity",
        native_selector="docid=KBo1.1",
        prerequisites_executable=True,
    )
    r = resolve(ref)
    assert r.status == "resolvable"
    assert r.query_role == "identity-filter"
    assert reverse_index_bucket(ref) == "identity"


def test_related_record_cannot_substitute_for_identity():
    ref = ExternalReference(
        "x",
        "entity-identity",
        external="https://example.org/record/1",
        identity_strength="related-record",
        native_selector="docid=KBo1.1",
    )
    assert resolve(ref).status == "informative-only"


def test_catalogue_identifier_requires_issuer():
    ref = ExternalReference("museum", "catalogue-identifier", value="12345", native_selector="museum=12345")
    assert "catalogue identifier requires issuer/namespace" in validate(ref)


def test_equal_identifier_literals_under_different_issuers_are_distinct():
    a = ExternalReference("a", "catalogue-identifier", issuer="museum-a", value="123", native_selector="a=123")
    b = ExternalReference("b", "catalogue-identifier", issuer="museum-b", value="123", native_selector="b=123")
    assert identifier_key(a) != identifier_key(b)


def test_provenance_url_is_explanation_only_by_default():
    ref = ExternalReference("doi", "provenance-source", external="https://doi.org/10.example/x")
    r = resolve(ref)
    assert r.status == "informative-only"
    assert r.query_role == "metadata/explanation"


def test_provenance_source_requires_explicit_external_reference():
    ref = ExternalReference("doi", "provenance-source")
    assert any("external" in e for e in validate(ref))


def test_locator_is_explanation_only():
    ref = ExternalReference("url", "locator", external="https://example.org/page")
    r = resolve(ref)
    assert r.status == "informative-only"
    assert r.query_role == "explanation-only"


def test_locator_requires_explicit_external_reference():
    ref = ExternalReference("url", "locator")
    assert any("external" in e for e in validate(ref))


def test_native_lexical_key_does_not_become_semantic_or_authority_reference_by_string_shape():
    ref = ExternalReference("lex", "catalogue-identifier", issuer="bhsa-native", value="MLK[", native_selector="lex=MLK[")
    assert reverse_index_bucket(ref) == "identifier"
    assert resolve(ref).query_role == "identifier-filter"


def test_period_label_requires_explicit_authority_mapping():
    ref = ExternalReference(
        "period",
        "authority-value",
        external="Old Babylonian",
        authority="PeriodO",
        assessment="ambiguous",
        native_selector="period=Old Babylonian",
    )
    assert resolve(ref).status == "informative-only"


def test_material_label_requires_explicit_authority_mapping():
    ref = ExternalReference(
        "material",
        "authority-value",
        external="clay",
        authority="Getty AAT",
        assessment="ambiguous",
        native_selector="material=clay",
    )
    assert resolve(ref).status == "informative-only"


def test_owl_sameas_rejected_outside_same_entity_identity():
    ref = ExternalReference(
        "bad",
        "authority-value",
        external="aat:1",
        authority="Getty AAT",
        assessment="exact",
        publication_relation="owl:sameAs",
    )
    assert any("owl:sameAs" in e for e in validate(ref))


def test_owl_sameas_allowed_only_for_same_entity_shape():
    ref = ExternalReference(
        "good",
        "entity-identity",
        external="https://example.org/entity/1",
        identity_strength="same-entity",
        publication_relation="owl:sameAs",
    )
    assert validate(ref) == []


def test_skos_mapping_rejected_for_catalogue_identifier():
    ref = ExternalReference(
        "bad",
        "catalogue-identifier",
        issuer="museum",
        value="123",
        publication_relation="skos:exactMatch",
    )
    assert any("SKOS mapping" in e for e in validate(ref))


def test_authority_assessment_does_not_create_semantic_bucket():
    ref = ExternalReference(
        "period",
        "authority-value",
        external="periodo:example",
        authority="PeriodO",
        assessment="exact",
        native_selector="period=X",
    )
    assert reverse_index_bucket(ref) == "authority"


def test_uri_hostname_never_infers_role_or_dereference_capability():
    ref = ExternalReference("x", "", external="https://vocab.getty.edu/aat/300014109")
    assert validate(ref) == ["reference kind must be explicit and controlled"]


def test_identifier_key_rejects_wrong_kind():
    with pytest.raises(ValueError):
        identifier_key(ExternalReference("x", "locator", external="https://example.org"))
