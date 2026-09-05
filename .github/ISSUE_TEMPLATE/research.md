---
name: Research ticket
about: Evidence-first investigation that produces a research artifact, not production code
title: "R-XXX: "
labels: ""
assignees: ""
---

## Type
Research only. No production implementation.

## Question

What exact decision or uncertainty must this research resolve?

## Scope

Define included corpora, ontology standards, repositories, versions, and explicit exclusions.

## Required evidence

- Authoritative upstream corpus/schema evidence.
- Authoritative ontology/specification evidence.
- Current version, maintenance, URI/versioning, and licensing evidence where relevant.
- Competing alternatives, not only the preferred design.
- Reproducible corpus/schema inspection when practical.

## Deliverable

`docs/research/R-XXX-<slug>.md`

The report must distinguish observed facts, external requirements, project recommendations, rejected alternatives, and unresolved assumptions.

## Acceptance criteria

- [ ] Exact versions/commits inspected are recorded where possible.
- [ ] Relevant alternatives are compared.
- [ ] Licensing/distribution implications are addressed.
- [ ] Agent and human ergonomics are addressed where relevant.
- [ ] Recommendation is explicit enough to inform a later design ticket.
- [ ] Unsupported/uncertain semantics are recorded rather than guessed.
- [ ] Research PR receives independent skeptical review before merge.
