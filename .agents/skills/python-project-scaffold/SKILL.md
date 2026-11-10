---
name: python-project-scaffold
description: Impose a standard shape on a Python project - uv, ruff, pyright strict, pre-commit, GitHub CI, one self-check, and a CLAUDE.md that governs docs and comments. Use when starting a Python project, when adding lint, type-check or CI tooling to an existing one, or when asked to scaffold, standardize, or "impose order on" a Python repo.
---

# python-project-scaffold

Every file below is the whole thing, not a starting point. Add a config key when a run fails without it, never in advance.

## Steps

1. Read the repo first. An existing project already has a layout, and the job is to make the tooling fit it, not to move code.
2. Get the current version of every pinned tool from the registry (`npm view`, `pip index versions`, `curl https://pypi.org/pypi/<name>/json`, the GitHub releases API). The versions written below are stale by the time you read them.
3. Get the latest stable Python from `curl -s https://endoflife.date/api/python.json`. The first entry is the newest cycle. Read it, and do not answer from memory: a cycle ships every October, later than the assistant's knowledge cutoff.
4. Write the files.
5. Run `uvx ruff@<ver> check .`, `uvx ruff@<ver> format .`, `uvx pyright@<ver>`, then the self-check. Fix what they report before you hand back.
6. Stage the files and run `uvx pre-commit@<ver> run --all-files`. Pre-commit only sees tracked files, so an unstaged scaffold reports a false pass.

## The three Python versions

They answer different questions, so do not set them to the same number by reflex.

- `requires-python` is the floor. Set it to the oldest cycle the code really runs on, and leave it there. The newest release is the wrong answer for a library.
- `[tool.pyright] pythonVersion` matches that floor. Pyright then rejects syntax and stdlib calls the floor does not have, which keeps the floor honest without a CI matrix.
- `python-version` in CI is the latest stable cycle. It catches a deprecation on the way in. Add a matrix only after a real break, not in advance.

## Layout

- One flat package at the root, named for the distribution with dashes as underscores. `viwoods-sync` gives `viwoods_sync/`. Hold to that and hatchling needs no build config beyond one line.
- No `src/` and no workspace until a second distribution exists.
- One test file at the root, run as `python3 test_<name>.py`. It uses `assert` and prints `ok`. Reach for pytest when fixtures or parametrization start to hurt, not before.
- No runtime dependency without a reason that a few lines of stdlib cannot cover. Dev tools are pinned; runtime stays empty as long as it can.

## pyproject.toml

```toml
[project]
name = "<dist-name>"
version = "0.1.0"
description = "<one line>"
requires-python = ">=3.10"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["<package>"]

[dependency-groups]
dev = ["ruff>=0.16.1", "pyright>=1.1.411", "pre-commit>=4.6.1"]

[tool.ruff]
# Ruff formats Python blocks inside markdown, which rewrites quoted snippets.
extend-exclude = ["*.md", ".claude"]

[tool.ruff.lint]
extend-select = ["I", "B", "UP"]

[tool.pyright]
include = ["<package>", "test_<name>.py"]
typeCheckingMode = "strict"
pythonVersion = "3.10"
```

## .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.1
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.411
    hooks:
      - id: pyright
  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.23.2
    hooks:
      - id: markdownlint-cli2
        args: [--fix]
  # mdformat runs after markdownlint-cli2, so its normalization is the last word on layout.
  - repo: https://github.com/hukkin/mdformat
    rev: 1.0.0
    hooks:
      - id: mdformat
        args: [--wrap, "no", --number]
        additional_dependencies:
          - mdformat-gfm
  - repo: https://github.com/mit-d/check-unicode
    rev: v0.6.0
    hooks:
      - id: check-unicode
        args: [--fix]
```

The hook id is `ruff-check`. `ruff` is a deprecated alias. Exempt any directory that quotes foreign output or vendors third-party text, and say why in CLAUDE.md.

Plain ASCII enforcement is one stdlib call, `open(f, 'rb').read().isascii()`, and a local hook running that is enough for a project that only wants the rule. `check-unicode` earns the dependency by also catching Trojan Source bidi overrides and zero-width characters, and by rewriting smart quotes and em dashes under `--fix` instead of only refusing the commit. It is a small single-maintainer package, so pin the `rev`.

## .markdownlint-cli2.jsonc

```jsonc
{
  "config": {
    "MD013": false,
    "MD033": false,
    // mdformat pads every table to aligned and runs last, so a table-style rule here
    // only ever loses the argument. Let the formatter own table layout.
    "MD060": false
  },
  // Vendored markdown is not yours to reformat.
  "ignores": [".claude/**", ".agents/**"]
}
```

Run `npx markdownlint-cli2@<ver> --fix "**/*.md"` once and read the diff. What is left is MD040, one bare code fence at a time, and the fix is a language tag, not a disabled rule. Use `text` for output, paths and pseudo-code.

Take both, because they do different jobs. `markdownlint-cli2` is a linter: it evaluates sixty numbered rules and reports each violation by id. `mdformat` is a formatter: it parses to a CommonMark AST and reprints it, the way `ruff format` reprints Python. A formatter cannot report what it will not rewrite. Run mdformat alone and a fence with no language tag, a heading that skips a level, a bare URL and a duplicate heading all survive untouched, because none of them is a layout question.

The order matters. markdownlint-cli2 fixes first, mdformat normalizes second, and mdformat wins any disagreement about layout. Reverse them and the two hooks rewrite each other on every run.

mdformat needs `mdformat-gfm` before it will keep a table intact, and it flattens any dialect its parser does not model - MDX, Liquid tags, directive syntax. Reach for `--wrap no` unless the project wants reflowed prose. Among linters, `markdownlint-cli` is the same ruleset as cli2 with a weaker config story. `pymarkdown` is Python, which is worth taking only when a Node toolchain in the hook chain is unacceptable, and then remember `extensions.front-matter.enabled`, without which it reads a skill file's YAML header as a setext heading.

## .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      # Runs ruff and pyright from .pre-commit-config.yaml, so versions live in one place.
      - uses: pre-commit/action@v3.0.1
      - name: Self-check
        run: python3 test_<name>.py
```

CI must not duplicate the tool versions. If a fixture the self-check needs is gitignored, guard the step with a `[ -d <dir> ]` test that prints why it skipped. A silent skip reads as a pass.

## .gitignore

```
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/
.venv/
venv/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
```

## .vscode/settings.json

```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/.ruff_cache": true,
    "**/.venv": true
  }
}
```

## CLAUDE.md

Write these sections, in this order, with nothing that the repo itself already says.

- **Docs and comments.** Point at the `ste-writing` and `terse-comments` skills and say they apply to every comment and docstring, not only on request. Say that `ste-writing` also governs every design document, at document scale: short sentences, one claim each, and a bullet list wherever prose carries a set. A document written as an essay is the shape the rule exists to stop. Vendor both skills under `.claude/skills/` in the same commit, or the reference dangles. State the ASCII rule and name its exemptions. Ban historical narration: git holds it.
- **Layout.** The package name, why there is no `src/`, the runtime-dependency rule, and any directory that is gitignored on purpose.
- **Workflow.** The self-check command, the three tool commands, and the commit policy: commit freely when autonomous, wait for the user when interactive.
- **A domain section.** The two or three facts that bite anyone who works here and that no file states. A device that sleeps, an API with no delete, a rate limit. This section is why the file exists. Skip it and CLAUDE.md is a restatement of the config.

## Pyright strict friction

- A dict alias as a dataclass default needs `field(default_factory=lambda: Alias())`. A bare `dict` infers `dict[Unknown, Unknown]`.
- An explicit `-> Any` return, such as `json.loads`, passes. Unannotated inference does not. Annotate the local that receives it and the rest of the file types itself.
- Define a `Protocol` for a seam a test fakes. It replaces a run of `# pyright: ignore` comments with the interface that was already implied.
