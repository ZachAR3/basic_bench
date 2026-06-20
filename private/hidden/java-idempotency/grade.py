from __future__ import annotations

import os
import pathlib
import shutil
import subprocess


JAVA_HOME = pathlib.Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")


def grade(workspace: pathlib.Path, tests: pathlib.Path):
    build = workspace / ".bench-build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir()
    sources = list((workspace / "src/main/java").rglob("*.java")) + [tests / "JavaChecks.java"]
    env = os.environ.copy()
    env["JAVA_HOME"] = str(JAVA_HOME)
    compile_result = subprocess.run(
        [str(JAVA_HOME / "bin/javac"), "-d", str(build), *map(str, sources)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        env=env,
    )
    if compile_result.returncode != 0:
        return [
            {"name": name, "points": 2, "passed": False, "detail": compile_result.stdout[-2000:]}
            for name in ("concurrent dedupe", "conflict and retry", "expiry and capacity", "defensive ETag", "validation and lock scope")
        ]
    checks = []
    for mode, name in [
        ("dedupe", "concurrent dedupe"),
        ("conflict", "conflict and retry"),
        ("expiry", "expiry and capacity"),
        ("etag", "defensive ETag"),
        ("validation", "validation and lock scope"),
    ]:
        result = subprocess.run(
            [str(JAVA_HOME / "bin/java"), "-cp", str(build), "JavaChecks", mode],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            env=env,
        )
        checks.append({"name": name, "points": 2, "passed": result.returncode == 0, "detail": result.stdout[-2000:]})
    shutil.rmtree(build, ignore_errors=True)
    return checks
