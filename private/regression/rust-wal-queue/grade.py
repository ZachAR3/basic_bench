from __future__ import annotations

import os
import pathlib
import shutil
import subprocess


def grade(workspace: pathlib.Path, _tests: pathlib.Path):
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(workspace / ".bench-target")
    result = subprocess.run(
        ["cargo", "check", "--quiet"],
        cwd=workspace, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    shutil.rmtree(workspace / ".bench-target", ignore_errors=True)
    return [{"name": "stable Rust compilation", "points": 1, "passed": result.returncode == 0, "detail": result.stdout[-2500:]}]
