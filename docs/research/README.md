# Research index

TFont begins with research-only tickets. Production mappings and runtime code are intentionally blocked until the foundational architecture questions are resolved.

## Required initial research

The initial research phase must establish:

1. **Distribution architecture** — where mappings live, how they bind to parent corpus versions, whether they are TF feature modules or semantic sidecars, whether one central repository or per-corpus repositories are preferable, and what Agora should own.
2. **Ontology governance** — supported ontology set, openness/licensing requirements, version pinning, deprecation, term stability, optional profiles, and policy for local concepts.
3. **Agent and human ergonomics** — semantic query discovery, capability reporting, mapping confidence/strength, explainability, error behavior, reproducibility, and scholar-facing inspection/editing workflows.
4. **Documentation architecture** — normative specifications versus generated reference material, per-corpus mapping documentation, ontology/version manifests, examples, machine-readable schemas, and how docs stay synchronized with mappings.
5. **Cross-corpus coverage baseline** — empirical inventory of the initial target corpora so later architecture is tested against real TF node/feature/edge semantics rather than BHSA alone.

Each completed ticket should produce `R-XXX-*.md` with a recommendation and rejected alternatives. A later design ticket will reconcile the research into the POC architecture.
