from __future__ import annotations

import pathlib
import shutil
import subprocess


def grade(workspace: pathlib.Path, _tests: pathlib.Path):
    build = workspace / ".bench-build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir()
    result = subprocess.run(
        ["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", "-I", workspace / "include", "-c", workspace / "src/memory_bus.cpp", "-o", build / "memory_bus.o"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120,
    )
    shutil.rmtree(build, ignore_errors=True)
    return [{"name": "C++20 compilation", "points": 1, "passed": result.returncode == 0, "detail": result.stdout[-2500:]}]
