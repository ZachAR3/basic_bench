#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "vendor" / "click"
DESTINATION = ROOT / "private" / "tasks" / "click-context-provenance"
PATCH = ROOT / "private" / "fixtures" / "click-context-provenance.patch"
UPSTREAM = ROOT / "private" / "fixtures" / "click-context-provenance.UPSTREAM.md"
EXPECTED_COMMIT = "41f410fb7528305d7e87c8cfa704f6c2456f57fc"


def command(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the large private task from the pinned Click submodule."
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not (SOURCE / ".git").exists():
        raise SystemExit(
            "Click submodule is missing. Run: git submodule update --init --recursive"
        )

    actual_commit = command("git", "rev-parse", "HEAD", cwd=SOURCE)
    if actual_commit != EXPECTED_COMMIT:
        raise SystemExit(
            f"Click submodule is at {actual_commit}; expected {EXPECTED_COMMIT}."
        )

    if DESTINATION.exists():
        if not args.force:
            print(f"Large task already initialized: {DESTINATION}")
            return 0
        shutil.rmtree(DESTINATION)

    shutil.copytree(
        SOURCE,
        DESTINATION,
        ignore=shutil.ignore_patterns(
            ".git",
            ".github",
            ".readthedocs.yaml",
            "tests",
            "__pycache__",
            "*.pyc",
        ),
    )
    command("patch", "-p1", "-i", str(PATCH), cwd=DESTINATION)
    shutil.copy2(UPSTREAM, DESTINATION / "UPSTREAM.md")
    print(f"Initialized large task: {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
