from __future__ import annotations

import os
import pathlib
import shutil
import subprocess


def run(command, cwd):
    env = os.environ.copy()
    env["CI"] = "1"
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    return result.returncode == 0, result.stdout[-2000:]


def grade(workspace: pathlib.Path, tests: pathlib.Path):
    target = workspace / ".bench-tests"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir()
    checks = []
    for name, label in [
        ("snapshot.test.ts", "stable immutable snapshots"),
        ("optimistic.test.ts", "overlapping optimistic synchronization"),
        ("url.test.ts", "deterministic URL state"),
        ("search.test.tsx", "React request lifecycle"),
    ]:
        shutil.copy2(tests / name, target / name)
        passed, detail = run(
            [
                str(workspace / "node_modules" / ".bin" / "vitest"),
                "run",
                str(target / name),
                "--environment",
                "jsdom",
            ],
            workspace,
        )
        checks.append(
            {"name": label, "points": 2, "passed": passed, "detail": detail}
        )
    passed, detail = run(["npm", "run", "build", "--silent"], workspace)
    checks.append(
        {"name": "Vite production build", "points": 2, "passed": passed, "detail": detail}
    )
    shutil.rmtree(target, ignore_errors=True)
    return checks
