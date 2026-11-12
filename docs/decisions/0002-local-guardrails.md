---
status: proposed
date: 2026-11-10
decision-makers: repository owner (pending PR approval)
---

# Enforce local changes with pinned hooks and encrypted shared configuration

## Context

Generated projects need local guardrails before CI and agent workflows arrive.
The accepted baseline selects lefthook, Claude Code file-tool hooks, gitleaks,
commitizen, and fnox/age. Ordinary checks must work without credentials.

## Decision

Install exact tool versions through mise. Run Ruff fixes and formatting in
sequence within a parallel pre-commit hook and re-stage their results. Scan the
index, validate staged fnox configuration, enforce Conventional Commits, and run
typing/tests before push. Preserve partially staged changes.

Use stdlib Python for the Claude hooks and fnox checker. File tools protect
generated and human-owned paths, including symlink aliases and parent traversal.
Fix mode protects tests tracked at HEAD; git failures deny the edit. Python edit
formatting is advisory and uses the project's locked Ruff.

Validate all shared fnox profiles as base64 age envelopes with no plaintext
defaults. Checks never decrypt. Extend gitleaks defaults with an age-prefix AND
root-path exception on the generic API key rule only. Keep historical example
exclusions at exact fingerprints with explicit owner approval.

Accept the documented Bash-write gap (Q21). A shell-token denylist cannot cover
arbitrary interpreters reliably and can obstruct legitimate generators. Local
bump always previews; actual releases arrive through task 05's release PR flow.

## Consequences

- Setup/check need no real secrets, and setup safely reinstalls local git hooks.
- Direct file-tool edits are mechanically checked; Bash writes still require
  the documented generators and independent/human review.
- Envelope validation proves storage shape, not successful decryption or the
  authenticity of ciphertext. The owner retains private identities outside git.
- Native hook evaluations and offline tests cover task 04. The hosted eval
  workflow arrives in task 06; its absence must be reported on this PR.

## Links

- [D26–D29](../../intent/0001-python-starter-baseline/decisions.md)
- [Acceptance evidence](../../intent/0001-python-starter-baseline/evidence/04-guardrails.md)
- [Baseline spec](../../intent/0001-python-starter-baseline/spec.md)
