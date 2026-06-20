from __future__ import annotations

import pathlib
import shutil
import subprocess


GODOT = pathlib.Path("/Applications/Godot.app/Contents/MacOS/Godot")


def run(command, cwd, timeout=120):
    result = subprocess.run(
        list(map(str, command)),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return result.returncode == 0, result.stdout[-2500:]


def grade(workspace: pathlib.Path, tests: pathlib.Path):
    checks = []
    shutil.rmtree(workspace / "csharp" / "bin", ignore_errors=True)
    shutil.rmtree(workspace / "csharp" / "obj", ignore_errors=True)
    passed, detail = run([GODOT, "--headless", "--path", workspace, "--editor", "--quit"], workspace)
    checks.append({"name": "Godot typed-script parse", "points": 2, "passed": passed, "detail": detail})
    for mode, name in [
        ("coalesce", "GDScript deep-copy coalescing"),
        ("stale", "GDScript generation ordering"),
    ]:
        passed, detail = run(
            [GODOT, "--headless", "--path", workspace, "--script", tests / "test_runner.gd", "--", mode],
            workspace,
        )
        checks.append({"name": name, "points": 2, "passed": passed, "detail": detail})

    target = workspace / ".bench-csharp"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir()
    shutil.copy2(tests / "Program.cs", target / "Program.cs")
    shutil.copy2(tests / "Test.csproj", target / "Test.csproj")
    for mode, name in [
        ("atomic", "C# atomic save and slot safety"),
        ("migration", "C# migration and isolation"),
    ]:
        passed, detail = run(
            ["dotnet", "run", "--project", target / "Test.csproj", "--", mode],
            workspace,
            180,
        )
        checks.append({"name": name, "points": 2, "passed": passed, "detail": detail})
    shutil.rmtree(target, ignore_errors=True)
    return checks
