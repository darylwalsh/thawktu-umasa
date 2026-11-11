"""Offline hook evaluations using the actual JSON-on-stdin entrypoints."""

import io
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import format_edited
import guard_paths
import pytest
from hook_input import edited_paths


def event(path: str, cwd: Path, tool: str = "Edit") -> str:
    """Build the native file-tool event shape."""
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return json.dumps({"tool_name": tool, "cwd": str(cwd), "tool_input": {key: path}})


def feed(monkeypatch: pytest.MonkeyPatch, raw: str, root: Path) -> None:
    """Set the runtime contract without reading personal Claude configuration."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(root))
    monkeypatch.setattr("sys.stdin", io.StringIO(raw))


@pytest.mark.parametrize(
    "path,way_forward",
    [
        ("uv.lock", "uv lock"),
        ("CHANGELOG.md", "mise run bump"),
        (".github/workflows/watch.lock.yml", "gh aw compile"),
        ("reports/tooling-watch/2026-11-10.facts.json", "collector"),
        ("tooling/watchlist.toml", "issue"),
        ("fnox.toml", "fnox set"),
    ],
)
@pytest.mark.parametrize("tool", ["Edit", "Write", "MultiEdit", "NotebookEdit"])
def test_guard_denies_protected_paths(
    path: str,
    way_forward: str,
    tool: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    feed(monkeypatch, event(path, tmp_path, tool), tmp_path)
    assert guard_paths.main() == 2
    message = capsys.readouterr().err
    assert path in message and way_forward in message


@pytest.mark.parametrize(
    "path",
    [
        "src/new.py",
        ".github/workflows/ci.yml",
        "reports/tooling-watch/README.md",
        "nested/uv.lock",
    ],
)
def test_guard_allows_ordinary_edits(
    path: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    feed(monkeypatch, event(path, tmp_path), tmp_path)
    assert guard_paths.main() == 0
    assert capsys.readouterr().err == ""


def test_guard_normalizes_subdirectory_and_symlinks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    subdir = tmp_path / "src"
    subdir.mkdir()
    feed(monkeypatch, event("../uv.lock", subdir), tmp_path)
    assert guard_paths.main() == 2
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path / "fnox.toml")
    feed(monkeypatch, event(str(alias), tmp_path), tmp_path)
    assert guard_paths.main() == 2
    assert guard_paths.denial(tmp_path.parent / "external.py", tmp_path) is None
    (tmp_path / "uv.lock").symlink_to(tmp_path.parent / "external.lock")
    feed(monkeypatch, event("../uv.lock", subdir), tmp_path)
    assert guard_paths.main() == 2


def test_multiedit_checks_every_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = json.dumps(
        {
            "cwd": str(tmp_path),
            "tool_input": {"edits": [{"file_path": "ok.py"}, {"file_path": "uv.lock"}]},
        }
    )
    feed(monkeypatch, raw, tmp_path)
    assert guard_paths.main() == 2
    assert edited_paths(event("x.py", tmp_path), tmp_path) == [tmp_path / "x.py"]
    raw = json.dumps(
        {"tool_input": {"file_path": "x.py", "edits": [{"file_path": "x.py"}]}}
    )
    assert edited_paths(raw, tmp_path) == [tmp_path / "x.py"]


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        "[]",
        '{"tool_input": []}',
        '{"tool_input": {}}',
        '{"cwd":"relative", "tool_input":{}}',
        '{"cwd":1, "tool_input":{}}',
        '{"tool_input":{"edits":[1]}}',
    ],
)
def test_guard_fails_closed_on_malformed_events(
    raw: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    feed(monkeypatch, raw, tmp_path)
    assert guard_paths.main() == 2
    assert "cannot validate" in capsys.readouterr().err


@pytest.mark.parametrize(
    "status,tracked,expected", [(0, True, 2), (0, False, 0), (1, False, 2)]
)
def test_fix_mode_uses_head(
    status: int,
    tracked: bool,
    expected: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("STARTER_FIX_MODE", "1")
    monkeypatch.setattr(guard_paths.shutil, "which", Mock(return_value="/usr/bin/git"))

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert args == [
            "/usr/bin/git",
            "ls-tree",
            "-r",
            "--name-only",
            "-z",
            "HEAD",
            "--",
            "tests/test_models.py",
        ]
        assert kwargs["cwd"] == tmp_path
        return subprocess.CompletedProcess(
            args, status, stdout="tests/test_models.py\0" if tracked else ""
        )

    monkeypatch.setattr(guard_paths.subprocess, "run", run)
    feed(monkeypatch, event("tests/test_models.py", tmp_path), tmp_path)
    assert guard_paths.main() == expected
    if tracked:
        assert "preserve the reproducing assertion" in capsys.readouterr().err


def test_fix_mode_missing_git_and_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STARTER_FIX_MODE", "1")
    monkeypatch.setattr(guard_paths.shutil, "which", Mock(return_value=None))
    feed(monkeypatch, event("tests/test_models.py", tmp_path), tmp_path)
    assert guard_paths.main() == 2
    monkeypatch.setattr(guard_paths.shutil, "which", Mock(return_value="/usr/bin/git"))

    def timeout(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired("git", 1)

    monkeypatch.setattr(guard_paths.subprocess, "run", timeout)
    feed(monkeypatch, event("tests/test_models.py", tmp_path), tmp_path)
    assert guard_paths.main() == 2


@pytest.mark.parametrize("status", [0, 1])
def test_formatter_runs_both_commands_and_reports_findings(
    status: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "space ; name.py"
    path.write_text("x=1\n")
    calls: list[list[str]] = []

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        assert kwargs["cwd"] == tmp_path
        return subprocess.CompletedProcess(
            args, status, stdout="lint finding", stderr=""
        )

    monkeypatch.setattr(format_edited.subprocess, "run", run)
    feed(monkeypatch, event(str(path), tmp_path), tmp_path)
    assert format_edited.main() == 0
    assert calls == [
        [str(tmp_path / ".venv/bin/ruff"), "check", "--fix", "--", str(path)],
        [str(tmp_path / ".venv/bin/ruff"), "format", "--", str(path)],
    ]
    output = capsys.readouterr().out
    if status:
        assert (
            json.loads(output)["hookSpecificOutput"]["additionalContext"].count(
                "lint finding"
            )
            == 2
        )
    else:
        assert output == ""


@pytest.mark.parametrize("path", ["README.md", "missing.py", "outside"])
def test_formatter_skips_non_python_missing_and_outside(
    path: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / path
    if path == "outside":
        external = tmp_path.parent / "external.py"
        external.write_text("x=1\n")
        target.symlink_to(external)
    elif path != "missing.py":
        target.write_text("text\n")
    feed(monkeypatch, event(str(target), tmp_path), tmp_path)
    assert format_edited.main() == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "failure", [OSError("missing Ruff"), subprocess.TimeoutExpired("ruff", 1)]
)
def test_formatter_errors_are_advisory(
    failure: Exception,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "x.py").write_text("x=1\n")

    def fail(*args: object, **kwargs: object) -> None:
        raise failure

    monkeypatch.setattr(format_edited.subprocess, "run", fail)
    feed(monkeypatch, event("x.py", tmp_path), tmp_path)
    assert format_edited.main() == 0
    assert "formatting unavailable" in capsys.readouterr().out


def test_formatter_handles_malformed_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    feed(monkeypatch, "broken", tmp_path)
    assert format_edited.main() == 0
    assert "formatting unavailable" in capsys.readouterr().out
