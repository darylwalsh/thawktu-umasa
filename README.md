# Python starter

A Python starter for reproducible tooling, shared local and CI quality checks,
and agent-maintained development workflows. The accepted design uses mise for
tools and tasks, uv for Python dependencies, and reviewed intent-driven changes.
The baseline provides a small typed pydantic package, quality checks, repository
guidance, and planning templates. Hooks and agent workflows arrive in later tasks.

Status: under construction, see [`intent/0001-python-starter-baseline/`](intent/0001-python-starter-baseline/).

## Local setup

Install [mise](https://mise.jdx.dev/getting-started.html), review the repository
configuration, and trust it with `mise trust`. Then run:

```sh
mise install
mise run setup
mise run run
mise run check
```

The demo prints `python-starter 0.1.0`. Mise provisions Python and uv; uv installs
locked dependencies in `.venv`. Python downloads by uv are disabled. See the
[task 02 evidence](intent/0001-python-starter-baseline/evidence/02-toolchain.md)
for verified pins and interpreter ownership.

## Quality checks

`mise run check` runs formatting, lint, strict typing, tests, and lockfile
verification in order, stopping at the first failure. It needs no secrets.

| Command | Purpose |
| --- | --- |
| `mise run fmt` / `mise run fmt:check` | Format Python / check formatting |
| `mise run lint` / `mise run lint:fix` | Lint Python / apply safe fixes |
| `mise run typecheck` | Run pyright in strict mode against `src` and `tests` |
| `mise run test` | Run pytest with branch coverage and a 95% minimum |
| `mise run lock:check` | Reject dependency metadata that disagrees with `uv.lock` |

The pinned dev tools come from `uv.lock`. Pyright's Node binary is installed
with its `nodejs` extra during setup; typing works offline afterward. Pytest
blocks Python socket calls and treats unexpected warnings as errors. The socket
guard applies inside the pytest process; subprocess tests must use local commands.
CI can disable pytest's cache with `mise run test -- -p no:cacheprovider`.
See [task 03 evidence](intent/0001-python-starter-baseline/evidence/03-quality.md)
for the rule selection, coverage baseline, and negative proofs.
