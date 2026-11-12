"""The tree scanner reads tracked content only and preserves path scoping."""

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts import scan_secrets


def tool_path(name: str) -> str:
    return f"/bin/{name}"


def test_scans_history_and_tracked_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scan_secrets.shutil, "which", tool_path)
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir/space name.txt").write_text("current working content")
    (tmp_path / "untracked.txt").write_text("excluded")
    (tmp_path / "alias").symlink_to("untracked.txt")
    monkeypatch.setattr(
        scan_secrets.subprocess,
        "check_output",
        Mock(return_value=b"dir/space name.txt\0alias\0deleted\0"),
    )
    calls: list[list[str]] = []

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args[1] == "dir":
            assert args[2] == "."  # Keep root-relative names for the fnox allowlist.
            snapshot = Path(str(kwargs["cwd"]))
            assert (
                snapshot / "dir/space name.txt"
            ).read_text() == "current working content"
            assert (snapshot / "alias").read_text() == "untracked.txt"
            assert not (snapshot / "alias").is_symlink()
            assert not (snapshot / "untracked.txt").exists()
            assert not (snapshot / "deleted").exists()
        assert "--redact" in args
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(scan_secrets.subprocess, "run", run)
    assert scan_secrets.main() == 0
    assert [args[1] for args in calls] == ["git", "dir"]
    assert "--log-opts=--all" in calls[0]


def test_history_failure_stops_tree_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scan_secrets.shutil, "which", tool_path)
    monkeypatch.setattr(
        scan_secrets.subprocess,
        "run",
        Mock(return_value=subprocess.CompletedProcess[str]("gitleaks", 1)),
    )
    assert scan_secrets.main() == 1


@pytest.mark.parametrize("missing", ["git", "gitleaks"])
def test_requires_scan_tools(missing: str, monkeypatch: pytest.MonkeyPatch) -> None:
    def lookup(name: str) -> str | None:
        return None if name == missing else tool_path(name)

    monkeypatch.setattr(
        scan_secrets.shutil,
        "which",
        lookup,
    )
    with pytest.raises(RuntimeError, match="mise install"):
        scan_secrets.main()
