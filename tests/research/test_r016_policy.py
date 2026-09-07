from scripts.research.r016_policy import (
    LOSS_OVER,
    LOSS_UNDER,
    MappingPolicy,
    comparison_state,
    resolve_atom,
    resolve_conjunction,
)


def m(assessment, *, eligible=False, losses=(), mid=None, plan=None):
    return MappingPolicy(
        mid or assessment,
        assessment,
        approximation_eligible=eligible,
        reviewed_losses=frozenset(losses),
        native_plan=f"plan:{assessment}" if plan is None else plan,
    )


def test_exact_executes_in_exact_mode():
    r = resolve_atom(m("exact"))
    assert r.status == "executable-exact"
    assert not r.losses


def test_broader_refuses_in_exact_mode():
    r = resolve_atom(m("broader", eligible=True), semantic_mode="exact")
    assert r.status == "informative-only"


def test_broader_requires_review_and_undercoverage_acceptance():
    no_review = resolve_atom(
        m("broader"), semantic_mode="approximate", accepted_losses={LOSS_UNDER}
    )
    assert no_review.status == "informative-only"

    no_accept = resolve_atom(m("broader", eligible=True), semantic_mode="approximate")
    assert no_accept.status == "informative-only"
    assert no_accept.losses == frozenset({LOSS_UNDER})

    ok = resolve_atom(
        m("broader", eligible=True),
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER},
    )
    assert ok.status == "executable-approximate"
    assert ok.losses == frozenset({LOSS_UNDER})


def test_narrower_requires_overcoverage_acceptance():
    ok = resolve_atom(
        m("narrower", eligible=True),
        semantic_mode="approximate",
        accepted_losses={LOSS_OVER},
    )
    assert ok.status == "executable-approximate"
    assert ok.losses == frozenset({LOSS_OVER})


def test_close_is_informative_only_without_reviewed_loss_contract():
    r = resolve_atom(
        m("close", eligible=True),
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "informative-only"


def test_close_reviewed_direction_still_needs_caller_acceptance():
    mapping = m("close", eligible=True, losses={LOSS_UNDER})
    refused = resolve_atom(mapping, semantic_mode="approximate")
    assert refused.status == "informative-only"
    ok = resolve_atom(
        mapping, semantic_mode="approximate", accepted_losses={LOSS_UNDER}
    )
    assert ok.status == "executable-approximate"


def test_bidirectional_close_requires_both_losses():
    mapping = m("close", eligible=True, losses={LOSS_UNDER, LOSS_OVER})
    one = resolve_atom(
        mapping, semantic_mode="approximate", accepted_losses={LOSS_UNDER}
    )
    assert one.status == "informative-only"
    both = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert both.status == "executable-approximate"
    assert both.losses == frozenset({LOSS_UNDER, LOSS_OVER})


def test_unknown_close_loss_token_fails_closed():
    mapping = m("close", eligible=True, losses={"noise"})
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={"noise"},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "loss" in r.reason


def test_broader_rejects_contradictory_reviewed_loss_contract():
    mapping = m("broader", eligible=True, losses={LOSS_OVER})
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "loss" in r.reason


def test_narrower_rejects_contradictory_reviewed_loss_contract():
    mapping = m("narrower", eligible=True, losses={LOSS_UNDER})
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "loss" in r.reason


def test_negative_control_assessments_never_substitute():
    for assessment in ("related", "ambiguous", "native-only", "unsupported"):
        r = resolve_atom(
            m(assessment, eligible=True, losses={LOSS_UNDER, LOSS_OVER}),
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER, LOSS_OVER},
        )
        assert r.status == "informative-only", assessment
        assert r.native_plan == "", assessment


def test_exact_without_native_plan_is_not_executable():
    r = resolve_atom(m("exact", plan=""))
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "plan" in r.reason


def test_approximate_without_native_plan_is_not_executable():
    r = resolve_atom(
        m("broader", eligible=True, plan=""),
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "plan" in r.reason


def test_unknown_semantic_mode_fails_closed():
    r = resolve_atom(
        m("exact"),
        semantic_mode="best-effort",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "mode" in r.reason


def test_exact_plus_broader_conjunction_reports_undercoverage():
    r = resolve_conjunction(
        [m("exact", mid="a"), m("broader", eligible=True, mid="b")],
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER},
    )
    assert r.status == "executable-approximate"
    assert r.losses == frozenset({LOSS_UNDER})


def test_broader_plus_narrower_conjunction_is_bidirectional():
    r = resolve_conjunction(
        [
            m("broader", eligible=True, mid="a"),
            m("narrower", eligible=True, mid="b"),
        ],
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "executable-approximate"
    assert r.losses == frozenset({LOSS_UNDER, LOSS_OVER})


def test_refused_required_atom_blocks_whole_conjunction():
    r = resolve_conjunction(
        [m("exact", mid="a"), m("close", eligible=True, mid="b")],
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "non-executable"


def test_exact_multi_corpus_comparison_allows_aggregate():
    plans = [resolve_conjunction([m("exact", mid="a")]) for _ in range(2)]
    c = comparison_state(plans)
    assert c == {"state": "exactly-comparable", "aggregate_allowed": True}


def test_approximate_aggregate_is_disabled_by_default():
    plans = [
        resolve_conjunction(
            [m("broader", eligible=True, mid="a")],
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        ),
        resolve_conjunction([m("exact", mid="b")]),
    ]
    c = comparison_state(plans)
    assert c["aggregate_allowed"] is False


def test_approximate_aggregate_requires_explicit_opt_in():
    plans = [
        resolve_conjunction(
            [m("broader", eligible=True, mid="a")],
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        ),
        resolve_conjunction([m("exact", mid="b")]),
    ]
    c = comparison_state(plans, allow_approximate_aggregates=True)
    assert c["aggregate_allowed"] is True


def test_different_loss_shapes_are_heterogeneous():
    plans = [
        resolve_conjunction(
            [m("broader", eligible=True, mid="a")],
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        ),
        resolve_conjunction(
            [m("narrower", eligible=True, mid="b")],
            semantic_mode="approximate",
            accepted_losses={LOSS_OVER},
        ),
    ]
    c = comparison_state(plans)
    assert c["state"] == "heterogeneous-loss"


def test_empty_comparison_is_not_reported_as_comparable():
    assert comparison_state([]) == {
        "state": "partial/non-executable",
        "aggregate_allowed": False,
    }


def test_compileable_native_plan_does_not_make_close_executable():
    mapping = MappingPolicy(
        "line-close",
        "close",
        approximation_eligible=False,
        reviewed_losses=frozenset(),
        native_plan="F.otype.v(n) == 'line'",
    )
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, LOSS_OVER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""


# Fresh adversarial RED regressions after R-015 merge.

def test_approximation_eligibility_must_be_exact_boolean():
    for value in (1, 0, "yes", "false", None, [], {}):
        mapping = m("broader", eligible=value)
        r = resolve_atom(
            mapping,
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        )
        assert r.status == "informative-only", value
        assert r.native_plan == "", value
        assert "boolean" in r.reason, value


def test_unknown_accepted_loss_token_cannot_authorize_execution():
    mapping = m("broader", eligible=True)
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER, "future-loss-token"},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "loss" in r.reason


def test_blocked_upstream_semantic_dependencies_cannot_be_bypassed_by_approximation():
    mapping = m("broader", eligible=True)
    # R-016 must consume an explicit upstream gate from R-003/R-015 rather than
    # treating mapping-level approximation as sufficient execution authority.
    object.__setattr__(mapping, "prerequisites_executable", False)
    r = resolve_atom(
        mapping,
        semantic_mode="approximate",
        accepted_losses={LOSS_UNDER},
    )
    assert r.status == "informative-only"
    assert r.native_plan == ""
    assert "prerequisite" in r.reason


def test_false_like_aggregate_opt_in_never_enables_statistics():
    plans = [
        resolve_conjunction(
            [m("broader", eligible=True, mid="a")],
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        ),
        resolve_conjunction([m("exact", mid="b")]),
    ]
    for value in (1, 0, "true", "false", None, [], {}):
        c = comparison_state(plans, allow_approximate_aggregates=value)
        assert c["aggregate_allowed"] is False, value


def test_heterogeneous_loss_aggregate_stays_disabled_even_with_generic_opt_in():
    plans = [
        resolve_conjunction(
            [m("broader", eligible=True, mid="a")],
            semantic_mode="approximate",
            accepted_losses={LOSS_UNDER},
        ),
        resolve_conjunction(
            [m("narrower", eligible=True, mid="b")],
            semantic_mode="approximate",
            accepted_losses={LOSS_OVER},
        ),
    ]
    c = comparison_state(plans, allow_approximate_aggregates=True)
    assert c["state"] == "heterogeneous-loss"
    assert c["aggregate_allowed"] is False
