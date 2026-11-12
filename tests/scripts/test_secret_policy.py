"""Exercise the actual pinned scanner against both sides of the age exception."""

import base64
import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "filename,plaintext,expected",
    [
        ("fnox.toml", False, 0),
        ("other.toml", False, 1),
        ("nested/fnox.toml", False, 1),
        ("fnox.toml", True, 1),
    ],
)
def test_age_exception_is_scoped_to_one_path_and_payload(
    filename: str, plaintext: bool, expected: int, tmp_path: Path
) -> None:
    gitleaks = shutil.which("gitleaks")
    assert gitleaks is not None, "Run tests via mise after `mise install`."
    config = Path(__file__).resolve().parents[2] / ".gitleaks.toml"
    value = base64.b64encode(
        b"age-encryption.org/v1\n-> example\n--- example\n" + bytes(range(256))
    ).decode()
    contents = f'api_key = "{value}"\n'
    if plaintext:
        # Synthetic token shape built at runtime; never a real credential.
        contents += (
            "# " + "ghp_" + hashlib.sha256(b"synthetic fixture").hexdigest()[:36] + "\n"
        )
    fixture = tmp_path / filename
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(contents)
    result = subprocess.run(
        [gitleaks, "dir", ".", "--config", str(config), "--no-banner", "--redact"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == expected, result.stderr
