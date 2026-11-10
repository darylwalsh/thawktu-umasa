"""Exercise the installed module entry point."""

import runpy
import subprocess
import sys
from importlib.metadata import version

import pytest


def test_module_output(capsys: pytest.CaptureFixture[str]) -> None:
    """The entry point prints the installed version in the covered process."""
    runpy.run_module("python_starter", run_name="__main__")

    captured = capsys.readouterr()
    assert captured.out == f"python-starter {version('python-starter')}\n"
    assert captured.err == ""


def test_module_exit_code() -> None:
    """Launching the installed package succeeds with the documented output."""
    result = subprocess.run(
        [sys.executable, "-m", "python_starter"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout == f"python-starter {version('python-starter')}\n"
    assert result.stderr == ""
