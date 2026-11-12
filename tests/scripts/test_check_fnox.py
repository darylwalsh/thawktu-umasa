"""Reject plaintext in shared fnox configuration, including staged-only changes."""

import base64
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts import check_fnox


def envelope() -> str:
    """A synthetic envelope shape, without a credential or private key."""
    return base64.b64encode(
        b"age-encryption.org/v1\n-> X25519 example\n--- example\npayload"
    ).decode()


@pytest.mark.parametrize(
    "value",
    [
        None,
        42,
        "plaintext",
        "!!!",
        "é",
        base64.b64encode(b"not age").decode(),
        base64.b64encode(b"age-encryption.org/v1\n-> incomplete").decode(),
    ],
)
def test_rejects_non_ciphertext(value: object) -> None:
    assert not check_fnox.ciphertext(value)


def test_accepts_age_and_empty_configuration() -> None:
    assert check_fnox.ciphertext(envelope())
    assert check_fnox.violations({}) == []
    assert (
        check_fnox.violations(
            {"secrets": {"EXAMPLE": {"provider": "age", "value": envelope()}}}
        )
        == []
    )


@pytest.mark.parametrize(
    "entry",
    [
        "plain",
        {},
        {"value": "not-encrypted"},
        {"value": envelope(), "default": "fallback"},
        {"provider": "plaintext", "value": envelope()},
    ],
)
def test_rejects_plaintext_and_fallbacks(entry: object) -> None:
    errors = check_fnox.violations({"secrets": {"EXAMPLE": entry}})
    assert len(errors) == 1 and "fnox set EXAMPLE" in errors[0]
    assert "not-encrypted" not in errors[0]


def test_checks_all_profiles_and_provider_inheritance() -> None:
    assert check_fnox.violations({"profiles": {"ci": {"secrets": {"KEY": "plain"}}}})
    assert check_fnox.violations(
        {
            "default_provider": "plaintext",
            "profiles": {"ci": {"secrets": {"KEY": {"value": envelope()}}}},
        }
    )
    assert (
        check_fnox.violations(
            {
                "profiles": {
                    "ci": {
                        "default_provider": "age",
                        "secrets": {"KEY": {"value": envelope()}},
                    }
                }
            }
        )
        == []
    )


@pytest.mark.parametrize(
    "config", [{"secrets": []}, {"profiles": []}, {"profiles": {"ci": 1}}]
)
def test_rejects_malformed_tables(config: dict[str, object]) -> None:
    assert check_fnox.violations(config)


def test_working_file_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert check_fnox.main([]) == 1
    (tmp_path / "fnox.toml").write_text("invalid [toml")
    assert check_fnox.main([]) == 1
    (tmp_path / "fnox.toml").write_text('[secrets]\nKEY = "private-fixture-value"\n')
    assert check_fnox.main([]) == 1
    assert "private-fixture-value" not in capsys.readouterr().err
    (tmp_path / "fnox.toml").write_text("[secrets]\n")
    assert check_fnox.main([]) == 0


def test_staged_cli_reads_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_fnox.shutil, "which", Mock(return_value="/usr/bin/git"))

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert args == ["/usr/bin/git", "show", ":fnox.toml"]
        return subprocess.CompletedProcess(
            args, 0, stdout='[secrets]\nKEY="plaintext"\n'
        )

    monkeypatch.setattr(check_fnox.subprocess, "run", run)
    assert check_fnox.main(["--staged"]) == 1


def test_staged_missing_git_or_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_fnox.shutil, "which", Mock(return_value=None))
    assert check_fnox.main(["--staged"]) == 1
    monkeypatch.setattr(check_fnox.shutil, "which", Mock(return_value="/usr/bin/git"))

    def fail(*args: object, **kwargs: object) -> None:
        raise subprocess.CalledProcessError(128, "git show")

    monkeypatch.setattr(check_fnox.subprocess, "run", fail)
    assert check_fnox.main(["--staged"]) == 1
