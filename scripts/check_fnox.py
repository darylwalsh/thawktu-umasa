"""Check shared fnox values without loading keys, providers, or secrets."""

import argparse
import base64
import binascii
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import cast


def ciphertext(value: object) -> bool:
    """Recognize fnox's base64-encoded age envelope, without decrypting it."""
    if not isinstance(value, str):
        return False
    try:
        decoded = base64.b64decode(value, validate=True)
    except ValueError, binascii.Error:
        return False
    return decoded.startswith(b"age-encryption.org/v1\n-> ") and b"\n--- " in decoded


def violations(config: dict[str, object], label: str = "fnox") -> list[str]:
    """Reject plaintext, fallback values, and non-age providers in every profile."""
    errors: list[str] = []
    secrets = config.get("secrets", {})
    if not isinstance(secrets, dict):
        return [f"{label}.secrets must be a table"]
    for name, raw in cast(dict[str, object], secrets).items():
        entry = cast(dict[str, object], raw) if isinstance(raw, dict) else {}
        if (
            not ciphertext(entry.get("value"))
            or entry.get("provider", config.get("default_provider", "age")) != "age"
            or "default" in entry
        ):
            errors.append(
                f"{label}.secrets.{name}: require age ciphertext and no plaintext default; use `fnox set {name} --provider age` (hidden prompt)"
            )
    profiles = config.get("profiles", {})
    if not isinstance(profiles, dict):
        return [*errors, f"{label}.profiles must be a table"]
    for name, profile in cast(dict[str, object], profiles).items():
        if not isinstance(profile, dict):
            errors.append(f"{label}.profiles.{name} must be a table")
        else:
            child = {
                "default_provider": config.get("default_provider", "age"),
                **cast(dict[str, object], profile),
            }
            errors.extend(violations(child, f"{label}.profiles.{name}"))
    return errors


def main(argv: list[str] | None = None) -> int:
    """Validate the working file, or the index when used by pre-commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.staged:
            git = shutil.which("git")
            if git is None:
                raise OSError("git unavailable")
            result = subprocess.run(  # noqa: S603  # Resolved git with fixed arguments; never a shell.
                [git, "show", ":fnox.toml"], capture_output=True, text=True, check=True
            )
            raw = result.stdout
        else:
            raw = Path("fnox.toml").read_text(encoding="utf-8")
        errors = violations(tomllib.loads(raw))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"fnox check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("fnox: all shared values are age ciphertext (no decryption required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
