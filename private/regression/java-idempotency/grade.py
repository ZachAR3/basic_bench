from __future__ import annotations

import pathlib
import shutil
import subprocess


def grade(workspace: pathlib.Path, _tests: pathlib.Path):
    java = pathlib.Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/javac")
    build = workspace / ".bench-build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir()
    result = subprocess.run(
        [str(java), "-d", str(build), *map(str, (workspace / "src/main/java").rglob("*.java"))],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
    shutil.rmtree(build, ignore_errors=True)
    return [{"name": "Java 21 compilation", "points": 1, "passed": result.returncode == 0, "detail": result.stdout[-2000:]}]
