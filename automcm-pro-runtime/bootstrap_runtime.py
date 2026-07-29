"""Copy AutoMCM-Pro runtime assets into the active modeling workspace."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


RUNTIME_ROOT = Path(__file__).resolve().parent
RUNTIME_DIRS = ("scripts", "templates")
RUNTIME_FILES = ("AutoMCM_SOP.md",)


def copy_file(source: Path, destination: Path, force: bool) -> str:
    if destination.exists() and not force:
        return "kept"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return "copied"


def bootstrap(target: Path, force: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    kept = 0

    for directory in RUNTIME_DIRS:
        source_root = RUNTIME_ROOT / directory
        for source in source_root.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(RUNTIME_ROOT)
            result = copy_file(source, target / relative, force)
            copied += result == "copied"
            kept += result == "kept"

    for filename in RUNTIME_FILES:
        result = copy_file(RUNTIME_ROOT / filename, target / filename, force)
        copied += result == "copied"
        kept += result == "kept"

    print(f"AutoMCM-Pro runtime ready at {target}")
    print(f"Copied: {copied}; preserved existing files: {kept}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".", help="Modeling workspace directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing runtime files instead of preserving them",
    )
    args = parser.parse_args()
    bootstrap(Path(args.target).resolve(), args.force)


if __name__ == "__main__":
    main()
