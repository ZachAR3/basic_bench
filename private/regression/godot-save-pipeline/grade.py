from __future__ import annotations

import pathlib
import subprocess


def grade(workspace: pathlib.Path, _tests: pathlib.Path):
    godot = "/Applications/Godot.app/Contents/MacOS/Godot"
    parse = subprocess.run(
        [godot, "--headless", "--path", workspace, "--editor", "--quit"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120,
    )
    build = subprocess.run(
        ["dotnet", "build", workspace / "csharp/SaveLogic.csproj", "--nologo"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    return [{
        "name": "Godot and C# baseline compile",
        "points": 1,
        "passed": parse.returncode == 0 and build.returncode == 0,
        "detail": (parse.stdout + build.stdout)[-2500:],
    }]
