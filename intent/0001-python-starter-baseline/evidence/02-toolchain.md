# Task 02: toolchain evidence

Verified on Linux x86_64 on 2026-11-10 using mise 2026.11.2. This implements
[task 02](../tasks/02-toolchain-mise-uv.md); quality checks remain task 03.

## Pins and Q10

| Component | Selection | Evidence |
| --- | --- | --- |
| Python | 3.15.2; package requires `>=3.15` | [Python.org release metadata](https://www.python.org/api/v2/downloads/release/1170/) lists this stable release on 2026-10-25. |
| uv | 0.13.7 | [PyPI release](https://pypi.org/project/uv/0.13.7/) published 2026-11-03. |
| uv build backend | `uv_build==0.13.7` | [PyPI release](https://pypi.org/project/uv-build/0.13.7/); generated with `uv init --package --build-backend uv`, then pinned exactly. |
| pydantic | Range `>=2.14.3,<3`; lock selects 2.14.3 | [PyPI metadata](https://pypi.org/pypi/pydantic/2.14.3/json) declares Python 3.15 support and requires `pydantic-core==2.50.4`. |
| pydantic-core | 2.50.4, transitive | [Release files](https://pypi.org/project/pydantic-core/2.50.4/#files), all three standard CPython 3.15 wheels below are present and not yanked. |

| Platform | Wheel filename |
| --- | --- |
| Linux x86_64 | `pydantic_core-2.50.4-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.whl` |
| Linux arm64 | `pydantic_core-2.50.4-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.whl` |
| macOS arm64 | `pydantic_core-2.50.4-cp315-cp315-macosx_11_0_arm64.whl` |

Q10 answer: use Python 3.15.2. The required wheel coverage and pydantic support
are available, so the 3.14 fallback is unnecessary. Wheel metadata was checked
for all three platforms; actual installation/runtime verification was Linux only.

## Environment wiring

The supported setting on the tested mise is `python.uv_venv_auto = "source"`.
It activates the environment created by uv without creating one itself. Before
the first `setup`, mise may warn that `.venv` does not yet exist; setup creates it.
The earlier boolean form is deprecated; see [mise's Python documentation](https://mise.jdx.dev/lang/python.html#uv-projects).

`UV_PYTHON = { value = "{{ tools.python.path }}/bin/python", tools = true }`
selects mise's interpreter by absolute executable path. `UV_PYTHON_DOWNLOADS =
"never"` prevents uv from fetching a replacement; see [uv's environment reference](https://docs.astral.sh/uv/reference/environment/#uv_python_downloads).
No `.python-version` is necessary: the pin, `UV_PYTHON`, and `requires-python`
provide the interpreter selection and package compatibility requirement.

Runtime assertions confirmed:

- `sys.executable` is `<clone>/.venv/bin/python`.
- `sys.base_prefix` is `<tools>/data/installs/python/3.15.2`.
- `UV_PYTHON` is `<tools>/data/installs/python/3.15.2/bin/python`.
- `VIRTUAL_ENV` is `<clone>/.venv`; downloads are `never`.
- Installed package metadata and `python_starter.__version__` both report `0.1.0`.
- The model accepts typed dictionary input, normalizes names, supplies defaults,
  rejects blank/missing/wrong-type names, and round-trips through `model_dump()`.

## Clean-clone proof

A Git snapshot of the staged implementation was cloned into a fresh directory.
The clone started without `.venv`, with empty mise data/state/cache directories
and an empty uv cache. The process used the existing mise binary, a minimal
`PATH`, an empty global mise configuration, and no agent credentials. The clone's
tracked tree remained clean after verification. Paths below are normalized to
`<clone>` and `<tools>`.

```text
$ mise install
mise by @jdx – installing 2 tools
mise ✓ uv@0.13.7
mise python@3.15.2 Python 3.15.2
mise ✓ python@3.15.2
mise installed 2 tools

$ mise run setup
[setup] $ uv sync --locked
Using CPython 3.15.2 interpreter at: <tools>/data/installs/python/3.15.2/bin/python
Creating virtual environment at: .venv
Resolved 6 packages
Built python-starter @ file://<clone>
Installed 6 packages
 + annotated-types==0.8.0
 + pydantic==2.14.3
 + pydantic-core==2.50.4
 + python-starter==0.1.0
 + typing-extensions==4.16.0
 + typing-inspection==0.4.5

$ mise run run
[run] $ uv run python -m python_starter
python-starter 0.1.0

$ mise exec -- uv sync --locked
Resolved 6 packages
Checked 6 packages

$ mise exec -- uv lock --check
Resolved 6 packages
```

All commands exited 0. Version checks returned Python 3.15.2 and uv 0.13.7.
The runtime proof used `mise exec -- uv run python -c ...`; dependency resolution
and installation selected the versions committed in `uv.lock` from public PyPI.

A second fresh clone of implementation commit
[`2e5e6d7`](https://github.com/darylwalsh/thawktu-umasa/commit/2e5e6d7367f254df03b0ed2850b095030329861c)
passed the same commands and assertions with a new `.venv`, reusing only the
isolated tool/package caches populated by the first test. Its tracked tree also
remained clean. This verifies the committed implementation in addition to the
initial empty-cache provisioning proof.

## Missing-interpreter proof amendment

Task 02's literal PATH-only negative step cannot fail with the required absolute
`UV_PYTHON` binding: hiding Python on `PATH` still uses the bound interpreter.
That positive control succeeded and reported 3.15.2. Two isolated fixtures replace
the negative step without moving, deleting, or modifying the host interpreter:

1. Point `UV_PYTHON` to a nonexistent executable in a scratch directory without
   `.venv`. `uv venv` exits 2: `No interpreter found at path`.
2. Give uv an empty Python search path, empty managed-Python directory, no Python
   on `PATH`, and request `--python 3.15.2`, retaining downloads `never`.
   `uv venv` exits 2 with:

   ```text
   error: No interpreter found for Python 3.15.2 in managed installations or search path
   hint: A managed Python download is available for Python 3.15.2, but Python downloads are set to 'never'
   ```

No managed Python installation or environment was created in the failure fixture.
This tests both the explicit binding and the download prohibition separately.
The amended proof is recorded as D23 in [decisions.md](../decisions.md).

## Verification limits

`git diff --check` passed. `mise run check` and the test/lint/typecheck tasks do
not exist until task 03; agent evals arrive in task 06. No pass for those suites
is claimed. No hooks, CI, or development dependencies were added in task 02.
