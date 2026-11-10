"""Print the installed starter package version."""

from python_starter import __version__


def main() -> None:
    """Run the demonstration entry point."""
    print(f"python-starter {__version__}")


if __name__ == "__main__":
    main()
