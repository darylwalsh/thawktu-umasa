"""Scan all refs plus only tracked working-tree contents with pinned gitleaks."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    """Preserve filenames for path-scoped rules and never follow tracked symlinks."""
    git = shutil.which("git")
    gitleaks = shutil.which("gitleaks")
    if git is None or gitleaks is None:
        raise RuntimeError("git and gitleaks must be installed; run `mise install`")
    root = Path.cwd()
    options = [
        "--redact",
        "--no-banner",
        "--config",
        str(root / ".gitleaks.toml"),
        "--gitleaks-ignore-path",
        str(root / ".gitleaksignore"),
    ]
    result = subprocess.run(  # noqa: S603  # Resolved pinned binary and fixed scan options.
        [gitleaks, "git", "--log-opts=--all", *options], check=False
    )
    if result.returncode:
        return result.returncode
    tracked = subprocess.check_output([git, "ls-files", "-z"])  # noqa: S603  # Resolved git and fixed arguments.
    with tempfile.TemporaryDirectory(prefix="starter-tracked-") as directory:
        for name in tracked.split(b"\0"):
            if not name:
                continue
            relative = Path(os.fsdecode(name))
            source = root / relative
            if not source.is_symlink() and not source.is_file():
                continue
            target = Path(directory) / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                target.write_text(os.readlink(source), encoding="utf-8")
            else:
                shutil.copyfile(source, target)
        return subprocess.run(  # noqa: S603  # Scan a private tracked-file snapshot with fixed options.
            [gitleaks, "dir", ".", *options], cwd=directory, check=False
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
