---
status: proposed
date: 2026-11-10
decision-makers: repository owner (pending PR approval)
---

# Run a sequential Python quality gate with offline tests

## Context and Problem Statement

Generated projects need the same reproducible checks locally and in CI. The
approved baseline selects Ruff, strict pyright, and pytest; task 03 must choose
an explicit lint policy, a measured coverage floor, and a network guard.

## Decision Drivers

- Catch common Python mistakes without enabling every lint family.
- Validate Pydantic constructors and fields without source suppressions.
- Reject accidental network access and unexpected warnings in unit tests.
- Stop at the first failed check and preserve dependency lockfile freshness.

## Considered Options

- An explicit Ruff rule list or every available rule.
- A local socket fixture or the maintained pytest-socket plugin.
- A 90% floor or a tighter floor supported by meaningful behavior tests.

## Decision Outcome

Use the explicit families and reasons recorded in [D24 and the task evidence](../../intent/0001-python-starter-baseline/evidence/03-quality.md#q11-rules-and-coverage).
Set a 95% coverage minimum against the measured 96% baseline, including branches.
Allow S101 only in tests for assertions, and S603 only in tests for fixed local
interpreter/module commands. Keep production lint checks intact.

Install pyright with its packaged Node extra through uv. Run strict typing on
existing source and test directories, with stale type suppressions rejected.
Enable pytest-socket globally and treat unexpected warnings as errors. Keep the
socket guard regression explicit about the plugin's expected warning/exception.

Run formatting, lint, typing, tests, and lock verification sequentially through
mise tasks. Use locked uv runs so checks cannot silently repair stale metadata.
Later tasks extend the gate with scripts and secrets checks.

### Consequences

- Good: the gate works without secrets or runtime downloads after setup.
- Good: tests cover CLI behavior, model validation, and the network guard.
- Good: fixed tool pins make rule and diagnostic changes reviewable.
- Bad: Python socket patching does not isolate child processes or native network
  libraries; subprocess tests require local-only commands and review.
- Bad: the coverage floor must be reconsidered when meaningful package behavior
  grows; adding trivial tests solely to retain the number is inappropriate.

## Links

- [Baseline spec](../../intent/0001-python-starter-baseline/spec.md)
- [D24 / D25](../../intent/0001-python-starter-baseline/decisions.md)
