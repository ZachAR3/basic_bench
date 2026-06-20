from __future__ import annotations

import os
import pathlib
import shutil
import subprocess


def grade(workspace: pathlib.Path, tests: pathlib.Path):
    target = workspace / "tests"
    target.mkdir(exist_ok=True)
    shutil.copy2(tests / "hidden.rs", target / "hidden.rs")
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = str(workspace / ".bench-target")
    checks = []
    for test, name in [
        ("replay", "WAL replay"),
        ("truncated_and_corrupt", "truncation and checksum"),
        ("idempotent_across_ack", "global task idempotency"),
        ("lease_tokens_and_concurrency", "lease tokens and concurrency"),
        ("compaction_preserves_all_states", "atomic compaction"),
    ]:
        result = subprocess.run(
            ["cargo", "test", "--quiet", "--test", "hidden", test, "--", "--exact"],
            cwd=workspace, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
        )
        checks.append({"name": name, "points": 2, "passed": result.returncode == 0, "detail": result.stdout[-2500:]})
    shutil.rmtree(target, ignore_errors=True)
    shutil.rmtree(workspace / ".bench-target", ignore_errors=True)
    return checks
