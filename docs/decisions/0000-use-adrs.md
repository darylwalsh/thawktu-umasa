---
status: accepted
date: 2026-11-09
decision-makers: repository owner
---

# Use architectural decision records for inherited choices

## Context and Problem Statement

Projects generated from this starter inherit its tooling and architecture.
Configuration shows the chosen tools but cannot explain alternatives, trade-offs,
or why the defaults fit. Future maintainers need that reasoning in the repository.

## Decision Drivers

- Preserve rationale alongside the configuration generated projects inherit.
- Keep task-specific execution history separate from durable design decisions.
- Make reconsideration possible without rewriting past decisions.

## Considered Options

- Keep rationale only in pull requests and conversations.
- Keep every decision only in an intent's `decisions.md`.
- Store inherited architectural choices as version-controlled ADRs.

## Decision Outcome

Use lightweight MADR records in `docs/decisions/`, numbered `NNNN-slug.md`,
starting with this record. Each record states context, drivers, considered
options, the decision, and consequences. Mark records proposed until approved;
retain superseded records with links to their replacements.

Task-specific choices and open questions remain in the intent's `decisions.md`.
When a choice affects generated projects, add an ADR and link the two records.
This implements the accepted baseline's existing ADR requirement.

### Consequences

- Good: generated projects retain searchable rationale and rejected alternatives.
- Good: future changes can reference or supersede an explicit decision.
- Bad: maintainers must keep decision status and cross-links current.
- Bad: trivial task details can create noise; reserve ADRs for inherited choices.

## Pros and Cons of the Options

- PRs and conversations require no extra file, but are difficult to carry into
  generated projects and can lose context.
- Intent logs capture chronological decisions, but mix implementation questions
  with architecture and require readers to reconstruct the rationale.
- ADRs add documentation work, but keep durable reasoning next to the starter.

## Links

- [Accepted intent](../../intent/0001-python-starter-baseline/intent.md)
- [Baseline decision log](../../intent/0001-python-starter-baseline/decisions.md)
