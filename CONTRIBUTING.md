# Contributing to TFont

TFont uses issue-driven research, design, TDD implementation, and independent review.

## Ticket types

- **Research (`R`)** — evidence gathering and an explicit recommendation; no production implementation.
- **Plan/design (`P`)** — architecture and contracts derived from completed research.
- **Implementation (`I`)** — TDD changes against an approved plan or sufficiently narrow existing contract.
- **Review/follow-up** — defects or questions found by independent review.

## Pull-request contract

Every PR must:

1. name its parent issue;
2. state the gate it satisfies (research, design, implementation);
3. list acceptance criteria and evidence that each is satisfied;
4. preserve native corpus semantics and provenance;
5. document unsupported or approximate mappings rather than hiding them;
6. receive independent skeptical review before merge when it changes research conclusions, architecture, mappings, schemas, runtime behavior, or public documentation.

## Research PRs

A research PR should normally add one document under `docs/research/`. It may add small reproducibility scripts or machine-readable inventories only when needed to reproduce the research; it must not commit the future production mapping architecture before that architecture is decided.

Each research document should contain:

- scope and question;
- sources/evidence inspected, including exact corpus/ontology versions where possible;
- observed requirements and constraints;
- alternatives considered;
- licensing and redistribution implications;
- effects on agent and human users;
- recommendation;
- rejected alternatives;
- unresolved questions;
- acceptance-criteria traceability.

## Design PRs

Designs belong in `docs/plans/`. They must define stable contracts before code, including version compatibility, error behavior, provenance, extensibility, serialization, and how approximate mappings are represented.

The initial POC architecture always requires a design PR after R-001 through R-005 are complete. Later changes to distribution, public mapping semantics, manifests/schemas, or MCP-facing behavior also require design first.

## Implementation PRs

Use TDD. Tests should make semantic compatibility claims executable. For corpus mappings, include negative tests proving that non-equivalent native concepts are not accidentally treated as exact equivalents.

## Review

The final reviewer should work from the issue, research/design artifact, diff, and upstream evidence rather than trusting the PR description. A mergeable review must address semantic fidelity, licensing, versioning, distribution, ergonomics, and test adequacy where applicable.

The required independent reviewer must be a different person or a separately instantiated review agent/context that did not author the changes. An authoring agent's self-audit does not satisfy this gate. Material changes after the final review require another independent review of the new PR head.
