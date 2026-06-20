from __future__ import annotations

import pathlib
import shutil
import subprocess


def grade(workspace: pathlib.Path, tests: pathlib.Path):
    build = workspace / ".bench-build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir()
    binary = build / "checks"
    compile_result = subprocess.run(
        [
            "clang++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", workspace / "include",
            workspace / "src/memory_bus.cpp",
            tests / "checks.cpp",
            "-o", binary,
        ],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120,
    )
    names = [
        ("endian", "cross-page endian and wrap"),
        ("fault", "precise permission faults"),
        ("tlb", "TLB invalidation"),
        ("mmio", "MMIO width and isolation"),
        ("atomic", "atomic fetch-add and cycles"),
    ]
    if compile_result.returncode != 0:
        return [{"name": name, "points": 2, "passed": False, "detail": compile_result.stdout[-2500:]} for _, name in names]
    checks = []
    for mode, name in names:
        result = subprocess.run(
            [binary, mode],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20,
        )
        checks.append({"name": name, "points": 2, "passed": result.returncode == 0, "detail": result.stdout[-2500:]})
    shutil.rmtree(build, ignore_errors=True)
    return checks
