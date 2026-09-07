from copy import deepcopy
import hashlib

import pytest

from scripts.research.r015_bundle_id import bridge_content_digest, bundle_digest, dependency_states, executable


def _d(label):
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def _scope():
    return {"source_term":"crm-old:E22","target_term":"crm-current:E22","relation":"reviewed-continuity"}


def _refresh_bridge(bridge, *, refresh_review=True):
    bridge["digest"] = bridge_content_digest(bridge)
    if refresh_review:
        bridge["reviewed_content_digest"] = bridge["digest"]


def _bundle():
    bridge={"bridge_id":"crm-bridge","source_lock_id":"crm-old","source_lock_digest":_d("crm-old"),"target_lock_id":"crm-current","target_lock_digest":_d("crm-current"),"scope":_scope(),"review_status":"reviewed","compatibility":"compatible","evidence_id":"evidence:crm-e22-continuity","evidence_digest":_d("evidence"),"runtime_strength":"exact","runtime_limitations":["term-scoped continuity only"],"review_id":"review:r015-crm-e22-001","reviewer_id":"github:independent-reviewer","reviewed_at":"2026-09-07T15:00:00Z"}
    _refresh_bridge(bridge)
    return {"schema_version":1,"profile_contracts":["written-text@1"],"ontology_locks":[{"lock_id":"crm-old","digest":_d("crm-old")},{"lock_id":"crm-current","digest":_d("crm-current")},{"lock_id":"crmtex","digest":_d("crmtex")}],"bridge_locks":[bridge],"dependency_edges":[{"id":"crmtex-crm","consumer":"crmtex","requires":"crm-old","satisfied_by":"bridge:crm-bridge","required_bridge_scope":_scope(),"active":True}],"display_label":"ignored presentation field"}


def test_reordering_set_like_members_does_not_change_digest():
    a=_bundle(); b=deepcopy(a); b["ontology_locks"].reverse(); b["bridge_locks"].reverse(); b["dependency_edges"].reverse(); assert bundle_digest(a)==bundle_digest(b)


def test_presentation_fields_do_not_change_digest():
    a=_bundle(); b=deepcopy(a); b["display_label"]="different"; b["retrieved_at"]="2099-01-01T00:00:00Z"; b["ontology_locks"][0]["licence_note"]="display"; b["bridge_locks"][0]["reviewer_display_name"]="Display"; b["bridge_locks"][0]["review_note"]="display"; b["dependency_edges"][0]["display_label"]="pretty"; assert bundle_digest(a)==bundle_digest(b)


def test_participating_ontology_digest_changes_bundle_identity():
    a=_bundle(); b=deepcopy(a); b["ontology_locks"][0]["digest"]=_d("changed"); assert bundle_digest(a)!=bundle_digest(b)

@pytest.mark.parametrize("value", [None,"sha256:fake","sha256:"+"A"*64])
def test_bad_ontology_digest_is_rejected(value):
    b=_bundle(); b["ontology_locks"][0]["digest"]=value
    with pytest.raises(ValueError,match="digest"): bundle_digest(b)


def test_bridge_semantic_content_change_requires_new_digest():
    b=_bundle(); b["bridge_locks"][0]["scope"]["source_term"]="crm-old:E55"
    with pytest.raises(ValueError,match="content digest mismatch"): bundle_digest(b)


def test_bridge_missing_endpoint_identity_is_rejected():
    b=_bundle(); del b["bridge_locks"][0]["target_lock_digest"]; _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError,match="target_lock_digest"): bundle_digest(b)

@pytest.mark.parametrize("scope", [{},"all terms",{"source_term":"crm-old:E22"}])
def test_bridge_scope_must_be_explicit_term_relation(scope):
    b=_bundle(); b["bridge_locks"][0]["scope"]=scope; b["dependency_edges"][0]["required_bridge_scope"]=deepcopy(scope); _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError,match="scope|target_term"): bundle_digest(b)


def test_bridge_content_changes_change_bundle_identity_after_review_refresh():
    a=_bundle()
    for field,value in (("evidence_digest",_d("new-evidence")),("scope",{"source_term":"crm-old:E55","target_term":"crm-current:E55","relation":"reviewed-continuity"})):
        b=deepcopy(a); b["bridge_locks"][0][field]=value
        if field=="scope": b["dependency_edges"][0]["required_bridge_scope"]=deepcopy(value)
        _refresh_bridge(b["bridge_locks"][0]); assert bundle_digest(a)!=bundle_digest(b)


def test_dependency_binding_change_changes_bundle_identity_even_if_not_executable():
    a=_bundle(); b=deepcopy(a); b["dependency_edges"][0]["requires"]="crm-current"; assert bundle_digest(a)!=bundle_digest(b)


def test_inactive_dependency_diagnostics_do_not_change_bundle_identity():
    a=_bundle(); b=deepcopy(a); b["dependency_edges"].append({"id":"optional","consumer":"missing","requires":"missing","satisfied_by":"bridge:missing","required_bridge_scope":{"diagnostic":"one"},"active":False}); before=bundle_digest(b); b["dependency_edges"][-1]["required_bridge_scope"]={"diagnostic":"changed"}; assert bundle_digest(a)==before==bundle_digest(b); assert dependency_states(b)[-1]=={"id":"optional","state":"inactive"}


def test_activating_optional_dependency_changes_bundle_identity():
    a=_bundle(); b=deepcopy(a); b["dependency_edges"].append({"id":"optional","consumer":"crmtex","requires":"crm-old","satisfied_by":"bridge:crm-bridge","required_bridge_scope":_scope(),"active":False}); inactive=bundle_digest(b); b["dependency_edges"][-1]["active"]=True; assert inactive==bundle_digest(a); assert bundle_digest(b)!=inactive


def test_unreferenced_or_inactive_only_bridge_is_rejected():
    for active in (None,False):
        b=_bundle(); extra=deepcopy(b["bridge_locks"][0]); extra["bridge_id"]="extra"; b["bridge_locks"].append(extra)
        if active is not None: b["dependency_edges"].append({"id":"extra-edge","consumer":"crmtex","requires":"crm-old","satisfied_by":"bridge:extra","required_bridge_scope":_scope(),"active":active})
        with pytest.raises(ValueError,match="not referenced by an active dependency"): bundle_digest(b)


def test_active_missing_bridge_fails_closed():
    b=_bundle(); b["bridge_locks"]=[]; assert dependency_states(b)==[{"id":"crmtex-crm","state":"missing-bridge"}]; assert not executable(b)


def test_inactive_optional_dependency_does_not_fail():
    b=_bundle(); b["bridge_locks"]=[]; b["dependency_edges"][0]["active"]=False; assert dependency_states(b)==[{"id":"crmtex-crm","state":"inactive"}]; assert executable(b)


def test_stale_bridge_detects_lock_digest_change():
    b=_bundle(); b["ontology_locks"][0]["digest"]=_d("new-crm-old"); assert dependency_states(b)==[{"id":"crmtex-crm","state":"stale-bridge"}]; assert not executable(b)


def test_unreviewed_bridge_cannot_execute():
    b=_bundle(); b["bridge_locks"][0]["review_status"]="draft"; assert dependency_states(b)==[{"id":"crmtex-crm","state":"unreviewed-bridge"}]; assert not executable(b)


def test_review_is_bound_to_bridge_content_digest_after_semantic_edit():
    b=_bundle(); new_scope={"source_term":"crm-old:E55","target_term":"crm-current:E55","relation":"reviewed-continuity"}; b["bridge_locks"][0]["scope"]=new_scope; b["dependency_edges"][0]["required_bridge_scope"]=deepcopy(new_scope); _refresh_bridge(b["bridge_locks"][0],refresh_review=False); assert dependency_states(b)==[{"id":"crmtex-crm","state":"unreviewed-bridge"}]; assert not executable(b)

@pytest.mark.parametrize("compatibility,state", [("incompatible","incompatible-bridge"),(None,"unknown-bridge-compatibility"),("unknown","unknown-bridge-compatibility")])
def test_bridge_compatibility_fails_closed(compatibility,state):
    b=_bundle()
    if compatibility is None: del b["bridge_locks"][0]["compatibility"]
    else: b["bridge_locks"][0]["compatibility"]=compatibility
    _refresh_bridge(b["bridge_locks"][0]); assert dependency_states(b)==[{"id":"crmtex-crm","state":state}]; assert not executable(b)


def test_exact_locked_dependency_needs_no_bridge():
    b=_bundle(); b["bridge_locks"]=[]; b["dependency_edges"][0]={"id":"crmtex-crm","consumer":"crmtex","requires":"crm-old","satisfied_by":"lock:crm-old","required_lock_digest":_d("crm-old"),"active":True}; assert dependency_states(b)==[{"id":"crmtex-crm","state":"satisfied-exact-lock"}]; assert executable(b)


def test_exact_lock_without_required_digest_fails_closed():
    b=_bundle(); b["bridge_locks"]=[]; b["dependency_edges"][0]={"id":"crmtex-crm","consumer":"crmtex","requires":"crm-old","satisfied_by":"lock:crm-old","active":True}; assert dependency_states(b)==[{"id":"crmtex-crm","state":"unbound-exact-lock"}]; assert not executable(b)


def test_exact_lock_must_match_edge_requires():
    b=_bundle(); b["bridge_locks"]=[]; b["dependency_edges"][0]={"id":"crmtex-crm","consumer":"crmtex","requires":"crm-old","satisfied_by":"lock:crm-current","required_lock_digest":_d("crm-current"),"active":True}; assert dependency_states(b)==[{"id":"crmtex-crm","state":"dependency-lock-mismatch"}]


def test_bridge_source_lock_must_match_edge_requires():
    b=_bundle(); b["dependency_edges"][0]["requires"]="crm-current"; assert dependency_states(b)==[{"id":"crmtex-crm","state":"bridge-requires-mismatch"}]


def test_active_edge_consumer_must_be_participating_lock():
    b=_bundle(); b["dependency_edges"][0]["consumer"]="missing-consumer"; assert dependency_states(b)==[{"id":"crmtex-crm","state":"missing-consumer-lock"}]


def test_bridge_scope_must_match_dependency_scope():
    b=_bundle(); b["dependency_edges"][0]["required_bridge_scope"]={"source_term":"crm-old:E55","target_term":"crm-current:E55","relation":"reviewed-continuity"}; assert dependency_states(b)==[{"id":"crmtex-crm","state":"bridge-scope-mismatch"}]


def test_bridge_without_explicit_required_scope_is_schema_invalid():
    b=_bundle(); del b["dependency_edges"][0]["required_bridge_scope"]
    with pytest.raises(ValueError,match="required_bridge_scope"): dependency_states(b)

@pytest.mark.parametrize("collection", ["profile_contracts","ontology_locks","bridge_locks","dependency_edges"])
def test_duplicate_semantic_ids_are_rejected(collection):
    b=_bundle(); b[collection].append(deepcopy(b[collection][0]))
    with pytest.raises(ValueError,match="duplicate"): bundle_digest(b)


def test_same_namespace_does_not_override_content_identity():
    a=_bundle(); b=deepcopy(a); a["ontology_locks"][0]["namespace"]="http://example.org/model/"; b["ontology_locks"][0]["namespace"]="http://example.org/model/"; b["ontology_locks"][0]["digest"]=_d("different-release"); assert bundle_digest(a)!=bundle_digest(b)


def _enrich_lock(lock, *, ontology_id, term_namespace, release, terms_used):
    lock.update({
        "ontology_id": ontology_id,
        "support_tier": "core",
        "term_namespace": term_namespace,
        "release": release,
        "source_uri": f"https://example.org/{ontology_id}/{release}",
        "content_digest": lock["digest"],
        "license": "CC-BY-4.0",
        "terms_used": list(terms_used),
    })


def _bundle_with_i002_lock_identity():
    b = _bundle()
    _enrich_lock(b["ontology_locks"][0], ontology_id="crm-old", term_namespace="crm-old:", release="7.1.2", terms_used=["crm-old:E22"])
    _enrich_lock(b["ontology_locks"][1], ontology_id="crm-current", term_namespace="crm-current:", release="7.1.3", terms_used=["crm-current:E22"])
    _enrich_lock(b["ontology_locks"][2], ontology_id="crmtex", term_namespace="crmtex:", release="2.0", terms_used=["crmtex:TX1"])
    return b


def test_i002_semantic_lock_fields_change_bundle_identity_when_payload_digest_is_stable():
    a = _bundle_with_i002_lock_identity()
    b = deepcopy(a)
    b["ontology_locks"][0]["terms_used"] = ["crm-old:E22", "crm-old:E55"]
    assert b["ontology_locks"][0]["content_digest"] == a["ontology_locks"][0]["content_digest"]
    assert bundle_digest(a) != bundle_digest(b)


def test_bridge_terms_must_be_declared_by_corresponding_pinned_locks():
    b = _bundle_with_i002_lock_identity()
    b["bridge_locks"][0]["scope"]["source_term"] = "crm-old:E288"
    b["dependency_edges"][0]["required_bridge_scope"]["source_term"] = "crm-old:E288"
    _refresh_bridge(b["bridge_locks"][0])
    with pytest.raises(ValueError, match="terms_used|source_term"):
        bundle_digest(b)
