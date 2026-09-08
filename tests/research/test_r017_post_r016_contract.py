from pathlib import Path

import pytest

from scripts.research.r017_reference_policy import ExternalReference, resolve, validate


def _with_prerequisite(ref: ExternalReference, value):
    object.__setattr__(ref, "prerequisites_executable", value)
    return ref


@pytest.mark.parametrize(
    "ref",
    [
        ExternalReference(
            "noun",
            "semantic-pivot",
            external="olia:Noun",
            native_selector="sp=subs",
            assessment="exact",
        ),
        ExternalReference(
            "aat-clay",
            "authority-value",
            external="aat:300014109",
            native_selector="material=clay",
            authority="Getty AAT",
            assessment="exact",
        ),
        ExternalReference(
            "entity",
            "entity-identity",
            external="https://example.org/entity/1",
            native_selector="docid=KBo1.1",
            identity_strength="same-entity",
        ),
        ExternalReference(
            "identifier",
            "catalogue-identifier",
            issuer="museum",
            value="123",
            native_selector="museum=123",
        ),
    ],
)
def test_queryable_reference_cannot_bypass_blocked_upstream_prerequisites(ref):
    blocked = _with_prerequisite(ref, False)
    result = resolve(blocked)
    assert result.status == "informative-only"
    assert result.native_selector == ""
    assert "prerequisite" in result.reason


def test_missing_upstream_prerequisite_defaults_fail_closed():
    ref = ExternalReference(
        "noun",
        "semantic-pivot",
        external="olia:Noun",
        native_selector="sp=subs",
        assessment="exact",
    )
    result = resolve(ref)
    assert result.status == "informative-only"
    assert result.native_selector == ""
    assert "prerequisite" in result.reason


@pytest.mark.parametrize("value", [1, 0, "true", "false", None, [], {}])
def test_non_boolean_upstream_prerequisite_fails_closed(value):
    ref = ExternalReference(
        "noun",
        "semantic-pivot",
        external="olia:Noun",
        native_selector="sp=subs",
        assessment="exact",
        prerequisites_executable=True,
    )
    object.__setattr__(ref, "prerequisites_executable", value)
    result = resolve(ref)
    assert result.status == "informative-only"
    assert result.native_selector == ""
    assert "boolean" in result.reason


def test_authority_literal_binding_does_not_authorize_skos_mapping_relation():
    ref = ExternalReference(
        "aat-clay",
        "authority-value",
        external="aat:300014109",
        native_selector="material=clay",
        authority="Getty AAT",
        assessment="exact",
        publication_relation="skos:exactMatch",
    )
    errors = validate(ref)
    assert any("R-013" in error or "SKOS" in error for error in errors)


def test_semantic_reference_role_alone_does_not_prove_skos_publication_operands():
    # The role tells R-017 which index family to use. It does not prove that
    # either native publication subject or external target is a SKOS concept.
    ref = ExternalReference(
        "noun",
        "semantic-pivot",
        external="olia:Noun",
        native_selector="sp=subs",
        assessment="exact",
        publication_relation="skos:exactMatch",
    )
    errors = validate(ref)
    assert any("R-013" in error or "SKOS" in error for error in errors)


@pytest.mark.parametrize(
    "relation",
    [
        "owl:equivalentClass",
        "rdfs:subClassOf",
        "ex:customRelation",
    ],
)
def test_unknown_positive_publication_relation_fails_closed_to_r013(relation):
    ref = ExternalReference(
        "authority-publication",
        "authority-value",
        external="aat:300014109",
        authority="Getty AAT",
        assessment="exact",
        publication_relation=relation,
    )
    errors = validate(ref)
    assert any("R-013" in error or "publication relation" in error for error in errors)


def test_full_iri_owl_sameas_cannot_bypass_identity_rule():
    ref = ExternalReference(
        "bad-full-iri-sameas",
        "authority-value",
        external="https://example.org/entity/1",
        authority="Example Authority",
        assessment="exact",
        publication_relation="http://www.w3.org/2002/07/owl#sameAs",
    )
    errors = validate(ref)
    assert any("sameAs" in error or "publication relation" in error for error in errors)


def test_full_iri_skos_mapping_cannot_bypass_formal_kind_delegation():
    ref = ExternalReference(
        "bad-full-iri-skos",
        "semantic-pivot",
        external="http://example.org/concept/1",
        assessment="exact",
        publication_relation="http://www.w3.org/2004/02/skos/core#exactMatch",
    )
    errors = validate(ref)
    assert any("R-013" in error or "SKOS" in error or "publication relation" in error for error in errors)


def test_normative_amendment_requires_upstream_gate_and_r013_publication_delegation():
    text = Path("docs/research/R-017-post-review-amendment.md").read_text(encoding="utf-8")
    assert "upstream execution prerequisite" in text
    assert "R-003" in text and "R-015" in text
    assert "even for `exact`" in text or "including `exact`" in text
    assert "R-013" in text
    assert "publication" in text
