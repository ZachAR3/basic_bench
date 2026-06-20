from __future__ import annotations

import pathlib
import subprocess


def grade(workspace: pathlib.Path, _tests: pathlib.Path):
    result = subprocess.run(
        ["npm", "run", "build", "--silent"],
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    return [{
        "name": "baseline production build",
        "points": 1,
        "passed": result.returncode == 0,
        "detail": result.stdout[-2000:],
    }]
