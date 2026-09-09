from __future__ import annotations

# Keep the RED fixture builder self-contained while satisfying the current
# I-001 ontology-lock schema. The submodule is loaded here before test modules
# import its helpers, then its source builder is wrapped with the one required
# packaging locator field that is structurally mandatory but semantically
# irrelevant to I-005.
from . import _fixtures as _fixture_module

_original_noun_sources = _fixture_module.noun_sources


def _noun_sources_with_snapshot(*args, **kwargs):
    sources = _original_noun_sources(*args, **kwargs)
    for lock in sources["locks"]:
        lock.setdefault("snapshot_artifact", "fixtures/ontology-fixture.ttl")
    return sources


_fixture_module.noun_sources = _noun_sources_with_snapshot
