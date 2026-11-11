"""Regression for filesystem traversal through a directory symlink and '..'."""

import io
import json
from pathlib import Path

import guard_paths
import pytest


def test_symlink_parent_traversal_keeps_actual_protected_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "uv.lock").write_text("generated\n")
    (tmp_path / "src/alias").symlink_to(tmp_path / "subdir", target_is_directory=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(
            json.dumps(
                {
                    "cwd": str(tmp_path),
                    "tool_name": "Edit",
                    "tool_input": {"file_path": "src/alias/../uv.lock"},
                }
            )
        ),
    )

    assert guard_paths.main() == 2
    assert "Blocked uv.lock" in capsys.readouterr().err
