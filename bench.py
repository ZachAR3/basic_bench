#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import random
import re
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".bench-state"
RUNS = Path(
    os.environ.get("BENCH_RUN_ROOT", "/private/tmp/private-code-agent-bench-runs")
)
RESULTS = ROOT / "results"
PRIVATE = ROOT / "private"
CONFIG = json.loads((ROOT / "config" / "bench.json").read_text())
LARGE_TASK = json.loads((PRIVATE / "large_manifest.json").read_text())
ZCODE_JS = Path("/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs")
DIRECT_AUTH_ROOT = Path(
    os.environ.get(
        "ZCODE_DIRECT_AUTH_ROOT",
        str(Path.home() / ".zcode-benchmark-auth"),
    )
).expanduser()
AGENT_POLICY = """Benchmark isolation rules:
- Work only inside the current repository.
- Do not access the network, external directories, prior sessions, benchmark harness files, caches, or git objects/refs beyond the checked-out baseline.
- Do not modify any provided tests, agent configuration, import hooks, or test infrastructure.
- Solve the task from the issue text and repository contents. Run local tests if the repository provides them.

"""
IMPLEMENTATION_FILES = {
    "lru-update": "lru.py",
    "config-precedence": "config_loader.py",
    "rate-window": "rate_limiter.py",
    "quoted-tokenizer": "tokenizer.py",
    "schema-migration": "migration.py",
    "csv-unicode": "csv_utils.py",
    "stable-toposort": "toposort.py",
    "async-retry": "retry.py",
    "dst-recurrence": "recurrence/expand.py",
    "webdav-endpoint": "webdav/parser.py",
}
PROVIDER_CHOICES = ["command", "zcode-direct", "zcode-go", "zcode", "opencode"]


def load_tasks() -> list[dict]:
    return json.loads((PRIVATE / "manifest.json").read_text())


def provider_label(provider: str) -> str:
    if provider == "command":
        return os.environ.get("BENCH_AGENT_LABEL", provider)
    return provider


def grader_for(task: dict) -> Path:
    return PRIVATE / "oracle" / task.get("test_runner", "isolated_unittest.py")


def regression_tests_for(task: dict) -> Path:
    custom = task.get("regression_dir")
    if custom:
        return PRIVATE / custom
    return PRIVATE / "tasks" / task["id"] / "tests"


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def zcode_command() -> list[str]:
    override = os.environ.get("ZCODE_COMMAND")
    if override:
        return override.split()
    if ZCODE_JS.exists() and command_exists("node"):
        return ["node", str(ZCODE_JS)]
    return ["zcode"]


def codex_executable() -> str:
    override = os.environ.get("CODEX_CLI")
    if override:
        return str(Path(override).expanduser())
    discovered = shutil.which("codex")
    if discovered:
        return discovered
    macos_bundle = Path("/Applications/Codex.app/Contents/Resources/codex")
    if macos_bundle.is_file():
        return str(macos_bundle)
    return "codex"


def run_cmd(
    command: list[str],
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
    kill_descendants: bool = False,
) -> dict:
    started = time.monotonic()
    proc = None
    try:
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=kill_descendants,
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        timed_out = False
        code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if proc is not None:
            if kill_descendants:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                proc.kill()
            trailing_out, trailing_err = proc.communicate()
            stdout += trailing_out or ""
            stderr += trailing_err or ""
    finally:
        if kill_descendants and proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    return {
        "command": command,
        "exit_code": code,
        "timed_out": timed_out,
        "wall_seconds": round(time.monotonic() - started, 3),
        "stdout": stdout,
        "stderr": stderr,
    }


def git_metrics(workspace: Path) -> dict:
    diff = run_cmd(["git", "diff", "HEAD", "--no-ext-diff", "--binary"], workspace, 30)
    text = diff["stdout"]
    untracked = run_cmd(
        ["git", "ls-files", "--others", "--exclude-standard"],
        workspace,
        30,
    )
    generated = {"PROMPT.md", "zcode.json", "opencode.jsonc"}
    for path in untracked["stdout"].splitlines():
        if path in generated:
            continue
        addition = run_cmd(
            ["git", "diff", "--no-index", "--binary", "--", "/dev/null", path],
            workspace,
            30,
        )
        text += addition["stdout"]
    changed_files = []
    added = deleted = 0
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            changed_files.append(line[6:])
        elif re.match(r"^\+(?!\+\+)", line):
            added += 1
        elif re.match(r"^-(?!--)", line):
            deleted += 1
    return {
        "changed_files": sorted(set(changed_files)),
        "files_changed": len(set(changed_files)),
        "lines_added": added,
        "lines_deleted": deleted,
        "patch": text,
    }


def init_workspace(source: Path, destination: Path, expose_tests: bool = True) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if not expose_tests:
        tests = destination / "tests"
        if tests.exists():
            shutil.rmtree(tests)
    run_cmd(["git", "init", "-q"], destination, 30)
    run_cmd(["git", "add", "."], destination, 30)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "benchmark",
            "GIT_AUTHOR_EMAIL": "benchmark@local",
            "GIT_COMMITTER_NAME": "benchmark",
            "GIT_COMMITTER_EMAIL": "benchmark@local",
        }
    )
    run_cmd(["git", "commit", "-qm", "baseline"], destination, 30, env)


def init_empty_workspace(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    run_cmd(["git", "init", "-q"], destination, 30)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "benchmark",
            "GIT_AUTHOR_EMAIL": "benchmark@local",
            "GIT_COMMITTER_NAME": "benchmark",
            "GIT_COMMITTER_EMAIL": "benchmark@local",
        }
    )
    run_cmd(["git", "commit", "--allow-empty", "-qm", "baseline"], destination, 30, env)
    install_agent_configs(destination)


def zcode_profile(provider: str) -> Path:
    if provider == "zcode-manual":
        return ROOT / "config" / "zcode-manual.json"
    if provider in {"zcode", "zcode-direct"}:
        return ROOT / "config" / "zcode-direct.json"
    if provider == "zcode-go":
        return ROOT / "config" / "zcode-go.json"
    return ROOT / "zcode.json"


def agent_config_sources(provider: str) -> dict[str, Path]:
    if provider in {"zcode", "zcode-direct", "zcode-go", "zcode-manual"}:
        return {"zcode.json": zcode_profile(provider)}
    if provider == "opencode":
        return {"opencode.jsonc": ROOT / "opencode.jsonc"}
    return {}


def direct_auth_sources() -> tuple[Path, Path]:
    return (
        DIRECT_AUTH_ROOT / "storage" / "cli" / "config.json",
        DIRECT_AUTH_ROOT / "data" / ".zcode" / "v2" / "credentials.json",
    )


def seed_direct_oauth(workspace: Path) -> bool:
    config_source, credentials_source = direct_auth_sources()
    if not config_source.exists() or not credentials_source.exists():
        return False
    storage = workspace / ".agent-state" / "zcode"
    config_target = storage / "cli" / "config.json"
    config_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_source, config_target)
    return True


def install_agent_configs(workspace: Path, provider: str = "zcode-direct") -> None:
    excluded = []
    sources = agent_config_sources(provider)
    for name, source in sources.items():
        if source.exists():
            shutil.copy2(source, workspace / name)
            excluded.append(name)
    exclude_file = workspace / ".git" / "info" / "exclude"
    if excluded and exclude_file.exists():
        with exclude_file.open("a") as handle:
            handle.write("\n# Benchmark-local agent configuration\n")
            handle.write("\n".join(excluded) + "\n")
            handle.write(".agent-state/\n")


def agent_can_see_tests(task: dict) -> bool:
    return task.get("agent_visible_tests", True)


def init_agent_workspace(task: dict, destination: Path) -> None:
    source = PRIVATE / "tasks" / task["id"]
    if not source.exists():
        if task["id"] == LARGE_TASK["id"]:
            raise SystemExit(
                "Large task is not initialized. Run: "
                "git submodule update --init --recursive && "
                "python3 scripts/init_large_task.py"
            )
        raise SystemExit(f"Missing task source: {source}")
    init_workspace(
        source,
        destination,
        expose_tests=agent_can_see_tests(task),
    )


def run_regression_tests(task: dict, workspace: Path, env: dict[str, str]) -> dict:
    if agent_can_see_tests(task):
        result = run_cmd(task["visible_test_command"], workspace, 120, env)
    else:
        grader = grader_for(task)
        trusted_tests = regression_tests_for(task)
        result = run_cmd(
            ["python3", "-I", str(grader), str(workspace), str(trusted_tests)],
            ROOT,
            120,
            env,
        )
    result["agent_visible"] = agent_can_see_tests(task)
    return result


def sandbox_profile(workspace: Path) -> Path:
    profile_root = Path("/private/tmp/private-code-agent-bench-profiles")
    profile_root.mkdir(parents=True, exist_ok=True)
    denied = [
        ROOT,
        Path.home() / ".cache" / "huggingface",
    ]
    if RUNS.exists():
        denied.extend(path for path in RUNS.glob("*/*") if path.resolve() != workspace.resolve())
    lines = ["(version 1)", "(allow default)"]
    for path in denied:
        lines.append(f'(deny file-read* (subpath {json.dumps(str(path.resolve()))}))')
        lines.append(f'(deny file-write* (subpath {json.dumps(str(path.resolve()))}))')
    profile = profile_root / f"{workspace.parent.name}-{workspace.name}.sb"
    profile.write_text("\n".join(lines) + "\n")
    return profile


def sandboxed_agent_command(command: list[str], workspace: Path) -> list[str]:
    if platform.system() != "Darwin" or not Path("/usr/bin/sandbox-exec").exists():
        raise RuntimeError(
            "Private benchmarks require macOS sandbox-exec. "
            "Use --unsafe-no-sandbox only if the agent is already container-isolated."
        )
    return ["/usr/bin/sandbox-exec", "-f", str(sandbox_profile(workspace)), *command]


def run_agent(command: list[str], workspace: Path, timeout: int, env: dict[str, str], unsafe: bool) -> dict:
    if not unsafe:
        command = sandboxed_agent_command(command, workspace)
    return run_cmd(command, workspace, timeout, env, kill_descendants=True)


def provider_command(provider: str, workspace: Path, prompt: str) -> tuple[list[str], dict[str, str]]:
    env = os.environ.copy()
    # Some agent CLIs inspect PWD instead of querying their actual process cwd.
    # Keep it inside the isolated workspace so configuration discovery cannot
    # touch the denied benchmark root.
    env["PWD"] = str(workspace)
    prompt = AGENT_POLICY + prompt
    if provider == "command":
        raw = os.environ.get("BENCH_AGENT_COMMAND")
        if not raw:
            raise SystemExit(
                "BENCH_AGENT_COMMAND is required for --provider command. "
                "Set it to a JSON array containing {workspace} and {prompt} placeholders."
            )
        try:
            template = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit("BENCH_AGENT_COMMAND must be a JSON array.") from exc
        if not isinstance(template, list) or not all(
            isinstance(part, str) for part in template
        ):
            raise SystemExit(
                "BENCH_AGENT_COMMAND must be a JSON array of strings."
            )
        command = [
            part.replace("{root}", str(ROOT))
            .replace("{codex}", codex_executable())
            .replace("{workspace}", str(workspace))
            .replace("{prompt}", prompt)
            for part in template
        ]
        return command, env
    if provider in {"zcode", "zcode-direct", "zcode-go"}:
        project_config = zcode_profile(provider)
        command = zcode_command() + [
            "--prompt",
            prompt,
            "--cwd",
            str(workspace),
            "--mode",
            "yolo",
            "--json",
            "--no-color",
        ]
        if not project_config.exists():
            env["ZCODE_BENCH_CONFIG_MISSING"] = "1"
        env["ZCODE_STORAGE_DIR"] = str(workspace / ".agent-state" / "zcode")
        if provider in {"zcode", "zcode-direct"}:
            if not seed_direct_oauth(workspace):
                env["ZCODE_DIRECT_LOGIN_MISSING"] = "1"
        return command, env
    if provider == "opencode":
        model = os.environ.get("OPENCODE_MODEL")
        env["XDG_DATA_HOME"] = str(workspace / ".agent-state" / "opencode-data")
        env["XDG_CACHE_HOME"] = str(workspace / ".agent-state" / "opencode-cache")
        env["XDG_CONFIG_HOME"] = str(workspace / ".agent-state" / "opencode-config")
        command = [
            "opencode",
            "run",
            "--pure",
            "--dir",
            str(workspace),
            "--format",
            "json",
            "--dangerously-skip-permissions",
        ]
        if model:
            command.extend(["--model", model])
        command.append(prompt)
        return command, env
    raise ValueError(f"Unknown provider: {provider}")


def git_head(workspace: Path) -> str:
    result = run_cmd(["git", "rev-parse", "HEAD"], workspace, 30)
    return result["stdout"].strip() if result["exit_code"] == 0 else ""


def workspace_digest(workspace: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(workspace.rglob("*")):
        relative = path.relative_to(workspace)
        if any(part in {".git", ".agent-state", "__pycache__"} for part in relative.parts):
            continue
        digest.update(str(relative).encode())
        if path.is_symlink():
            digest.update(b"SYMLINK")
            digest.update(os.readlink(path).encode())
        elif path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def integrity_checks(
    task: dict,
    workspace: Path,
    expected_head: str | None = None,
    provider: str = "command",
) -> dict:
    violations = []
    if expected_head is not None and git_head(workspace) != expected_head:
        violations.append("Git HEAD changed from the trusted baseline")
    changed = run_cmd(["git", "status", "--porcelain", "--untracked-files=all"], workspace, 30)
    for line in changed["stdout"].splitlines():
        path = line[3:]
        if "__pycache__" in Path(path).parts or path.endswith(".pyc"):
            continue
        if agent_can_see_tests(task) and (path.startswith("tests/") or "/tests/" in path):
            violations.append(f"test file changed: {path}")
        if path in {"zcode.json", "opencode.jsonc"}:
            violations.append(f"agent configuration changed: {path}")
        name = Path(path).name
        if name in {
            "sitecustomize.py",
            "usercustomize.py",
            "unittest.py",
            "pytest.py",
            "conftest.py",
        }:
            violations.append(f"import/test hook added: {path}")
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        if any(part in {".git", ".agent-state", "__pycache__"} for part in relative.parts):
            continue
        if path.is_symlink():
            violations.append(f"symlink present: {relative}")
        if path.is_file() and path.stat().st_size > 1_000_000:
            violations.append(f"oversized file: {relative}")
        if path.name.endswith(".pth"):
            violations.append(f"Python path hook present: {relative}")
        if path.suffix.lower() in {".so", ".dylib", ".dll", ".pyd"}:
            violations.append(f"native executable module present: {relative}")

    if agent_can_see_tests(task):
        trusted_tests = regression_tests_for(task)
        expected = {
            path.relative_to(trusted_tests): path.read_bytes()
            for path in trusted_tests.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        actual_tests = workspace / "tests"
        actual = {
            path.relative_to(actual_tests): path.read_bytes()
            for path in actual_tests.rglob("*")
            if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts
        }
        if actual != expected:
            violations.append("visible test tree differs from trusted baseline")
    trusted_configs = agent_config_sources(provider)
    for name, trusted in trusted_configs.items():
        candidate = workspace / name
        if trusted.exists() and (
            not candidate.is_file()
            or candidate.is_symlink()
            or candidate.read_bytes() != trusted.read_bytes()
        ):
            violations.append(f"agent configuration differs from trusted baseline: {name}")
    return {"passed": not violations, "violations": violations}


def score_private(task: dict, workspace: Path) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    visible = run_regression_tests(task, workspace, env)
    hidden_dir = PRIVATE / "hidden" / task["id"]
    grader = grader_for(task)
    hidden = run_cmd(
        ["python3", "-I", str(grader), str(workspace), str(hidden_dir)],
        ROOT,
        120,
        env,
    )
    integrity = integrity_checks(task, workspace)
    return {
        "passed": (
            visible["exit_code"] == 0
            and hidden["exit_code"] == 0
            and integrity["passed"]
        ),
        "visible": visible,
        "hidden": hidden,
        "integrity": integrity,
    }


def score_agent_workspace(
    task: dict,
    workspace: Path,
    seal_id: str,
    expected_head: str,
    provider: str,
) -> dict:
    before_digest = workspace_digest(workspace)
    integrity = integrity_checks(task, workspace, expected_head, provider)
    sealed = STATE / "grading" / seal_id
    if sealed.exists():
        shutil.rmtree(sealed)
    sealed.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        workspace,
        sealed,
        ignore=shutil.ignore_patterns(".git", ".agent-state", "__pycache__", "*.pyc"),
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    visible = run_regression_tests(task, sealed, env)
    hidden_dir = PRIVATE / "hidden" / task["id"]
    grader = grader_for(task)
    hidden = run_cmd(
        ["python3", "-I", str(grader), str(sealed), str(hidden_dir)],
        ROOT,
        120,
        env,
    )
    after_digest = workspace_digest(workspace)
    if after_digest != before_digest:
        integrity["passed"] = False
        integrity["violations"].append("workspace changed after agent exit during sealed grading")
    return {
        "passed": (
            visible["exit_code"] == 0
            and hidden["exit_code"] == 0
            and integrity["passed"]
        ),
        "visible": visible,
        "hidden": hidden,
        "integrity": integrity,
    }


def result_file(run_id: str) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    return RESULTS / f"{run_id}.jsonl"


def append_result(path: Path, record: dict) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def result_has_task(path: Path, task_id: str) -> bool:
    if not path.exists():
        return False
    return any(
        json.loads(line).get("task_id") == task_id
        for line in path.read_text().splitlines()
        if line.strip()
    )


def run_private(args: argparse.Namespace) -> int:
    tasks = [t for t in load_tasks() if t["id"] in CONFIG["private_task_ids"]]
    if args.task:
        selected = set(args.task)
        tasks = [t for t in tasks if t["id"] in selected]
    if args.limit:
        tasks = tasks[: args.limit]
    run_id = args.run_id or f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{args.provider}"
    output = result_file(run_id)
    if output.exists():
        print(f"Result file already exists; choose a new --run-id: {output}", file=sys.stderr)
        return 2
    print(f"run_id={run_id} tasks={len(tasks)} provider={args.provider}")
    for index, task in enumerate(tasks, start=1):
        workspace = RUNS / run_id / task["id"]
        init_agent_workspace(task, workspace)
        install_agent_configs(workspace, args.provider)
        expected_head = git_head(workspace)
        prompt = (PRIVATE / "prompts" / f"{task['id']}.md").read_text()
        command, env = provider_command(args.provider, workspace, prompt)
        if env.get("ZCODE_BENCH_CONFIG_MISSING"):
            print("Missing ./zcode.json. Copy config/zcode.example.json and authenticate first.", file=sys.stderr)
            return 2
        if env.get("ZCODE_DIRECT_LOGIN_MISSING"):
            print(
                "Direct ZCode OAuth state is missing. Authenticate the CLI in "
                "ZCODE_DIRECT_AUTH_ROOT before running this provider.",
                file=sys.stderr,
            )
            return 2
        print(f"[{index}/{len(tasks)}] {task['id']}")
        agent = run_agent(command, workspace, args.agent_timeout, env, args.unsafe_no_sandbox)
        patch = git_metrics(workspace)
        score = score_agent_workspace(
            task,
            workspace,
            f"{run_id}-{task['id']}",
            expected_head,
            args.provider,
        )
        record = {
            "suite": "private",
            "run_id": run_id,
            "task_id": task["id"],
            "provider": provider_label(args.provider),
            "agent": agent,
            "score": score,
            "patch": patch,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        append_result(output, record)
        print(f"  {'PASS' if score['passed'] else 'FAIL'} {agent['wall_seconds']}s {patch['files_changed']} files")
    print(f"results={output}")
    return 0


def run_paired_private(args: argparse.Namespace) -> int:
    tasks = [t for t in load_tasks() if t["id"] in CONFIG["private_task_ids"]]
    if args.task:
        selected = set(args.task)
        tasks = [t for t in tasks if t["id"] in selected]
    if args.limit:
        tasks = tasks[: args.limit]
    if args.seed is not None:
        random.Random(args.seed).shuffle(tasks)
    pair_id = args.run_id or f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-paired"
    outputs = [result_file(f"{pair_id}-zcode"), result_file(f"{pair_id}-opencode")]
    existing = [path for path in outputs if path.exists()]
    if existing:
        print(f"Result file already exists; choose a new --run-id: {existing[0]}", file=sys.stderr)
        return 2
    for index, task in enumerate(tasks):
        first = ["opencode", "zcode"] if args.opencode_first else ["zcode", "opencode"]
        order = first if index % 2 == 0 else list(reversed(first))
        for provider in order:
            run_id = f"{pair_id}-{provider}"
            workspace = RUNS / run_id / task["id"]
            init_agent_workspace(task, workspace)
            install_agent_configs(workspace, provider)
            expected_head = git_head(workspace)
            prompt = (PRIVATE / "prompts" / f"{task['id']}.md").read_text()
            command, env = provider_command(provider, workspace, prompt)
            if env.get("ZCODE_BENCH_CONFIG_MISSING"):
                print("Missing provider configuration.", file=sys.stderr)
                return 2
            if env.get("ZCODE_DIRECT_LOGIN_MISSING"):
                print("Direct ZCode OAuth state is missing.", file=sys.stderr)
                return 2
            print(f"[{index + 1}/{len(tasks)}] {task['id']} via {provider}")
            agent = run_agent(command, workspace, args.agent_timeout, env, args.unsafe_no_sandbox)
            patch = git_metrics(workspace)
            score = score_agent_workspace(
                task,
                workspace,
                f"{run_id}-{task['id']}",
                expected_head,
                provider,
            )
            append_result(
                result_file(run_id),
                {
                    "suite": "private",
                    "pair_id": pair_id,
                    "run_id": run_id,
                    "task_id": task["id"],
                    "provider": provider,
                    "order": order.index(provider) + 1,
                    "agent": agent,
                    "score": score,
                    "patch": patch,
                    "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                },
            )
            print(f"  {'PASS' if score['passed'] else 'FAIL'}")
    print(f"Compare with: python3 bench.py compare --run-a {pair_id}-zcode --run-b {pair_id}-opencode")
    return 0


def prepare_private(args: argparse.Namespace) -> int:
    task = next((t for t in load_tasks() if t["id"] == args.task), None)
    if not task:
        raise SystemExit(f"Unknown task: {args.task}")
    destination = RUNS / (args.run_id or "manual") / task["id"]
    init_agent_workspace(task, destination)
    print(destination)
    print((PRIVATE / "prompts" / f"{task['id']}.md").read_text())
    return 0


def prepare_manual_run(args: argparse.Namespace) -> int:
    output = result_file(args.run_id)
    if output.exists():
        print(f"Result file already exists; choose a new --run-id: {output}", file=sys.stderr)
        return 2
    tasks = [task for task in load_tasks() if task["id"] in CONFIG["private_task_ids"]]
    run_root = RUNS / args.run_id
    manual_provider = "zcode-manual" if args.profile == "zcode" else "command"
    agent_name = "ZCode desktop" if args.profile == "zcode" else "desktop agent"
    instructions = [
        f"# Manual agent run: {args.run_id}",
        "",
        f"Complete every task below in a separate fresh {agent_name} session.",
        "Open only the listed task folder, paste its PROMPT.md, and do not use web search.",
        "Run local tests only when the task includes them. Do not modify provided tests or agent configuration.",
        "",
    ]
    baselines = {}
    for index, task in enumerate(tasks, start=1):
        workspace = run_root / task["id"]
        init_agent_workspace(task, workspace)
        install_agent_configs(workspace, manual_provider)
        baselines[task["id"]] = git_head(workspace)
        prompt = AGENT_POLICY + (PRIVATE / "prompts" / f"{task['id']}.md").read_text()
        (workspace / "PROMPT.md").write_text(prompt)
        instructions.extend(
            [
                f"## {index}. {task['id']}",
                "",
                f"Folder: `{workspace}`",
                f"Prompt: `{workspace / 'PROMPT.md'}`",
                f"Tests visible to agent: `{'yes' if agent_can_see_tests(task) else 'no'}`",
                "",
            ]
        )
    guide = run_root / "MANUAL_RUN.md"
    guide.write_text("\n".join(instructions))
    baseline_path = STATE / "manual-runs" / f"{args.run_id}.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(
        json.dumps(
            {
                "provider": manual_provider,
                "agent_name": agent_name,
                "tasks": baselines,
            },
            indent=2,
        )
    )
    print(f"Prepared {len(tasks)} manual task workspaces.")
    print(f"Instructions: {guide}")
    print(f"When all tasks are complete, run:")
    print(f"  python3 bench.py finalize-manual-run --run-id {args.run_id}")
    return 0


def finalize_manual_run(args: argparse.Namespace) -> int:
    output = result_file(args.run_id)
    if output.exists():
        print(f"Result file already exists; choose a new --run-id: {output}", file=sys.stderr)
        return 2
    tasks = [task for task in load_tasks() if task["id"] in CONFIG["private_task_ids"]]
    run_root = RUNS / args.run_id
    baseline_path = STATE / "manual-runs" / f"{args.run_id}.json"
    if not baseline_path.exists():
        print(f"Missing trusted baseline manifest: {baseline_path}", file=sys.stderr)
        return 2
    baseline_data = json.loads(baseline_path.read_text())
    if "tasks" in baseline_data:
        baselines = baseline_data["tasks"]
        manual_provider = baseline_data.get("provider", "command")
        agent_name = baseline_data.get("agent_name", "desktop agent")
    else:
        baselines = baseline_data
        manual_provider = "zcode-manual"
        agent_name = "ZCode desktop application"
    missing = [task["id"] for task in tasks if not (run_root / task["id"]).exists()]
    if missing:
        print(f"Missing manual workspaces: {', '.join(missing)}", file=sys.stderr)
        return 2
    for index, task in enumerate(tasks, start=1):
        workspace = run_root / task["id"]
        expected_head = baselines.get(task["id"], "")
        if not expected_head:
            print(f"Missing trusted baseline for {task['id']}", file=sys.stderr)
            return 2
        patch = git_metrics(workspace)
        score = score_agent_workspace(
            task,
            workspace,
            f"{args.run_id}-{task['id']}",
            expected_head,
            manual_provider,
        )
        append_result(
            output,
            {
                "suite": "private",
                "run_id": args.run_id,
                "task_id": task["id"],
                "provider": manual_provider,
                "agent": {
                    "command": [agent_name],
                    "exit_code": 0,
                    "timed_out": False,
                    "wall_seconds": 0,
                    "stdout": "",
                    "stderr": "",
                },
                "score": score,
                "patch": patch,
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        )
        print(f"[{index}/{len(tasks)}] {task['id']}: {'PASS' if score['passed'] else 'FAIL'}")
    print(f"Saved manual results: {output}")
    return 0


def large_manual_baseline_path(run_id: str) -> Path:
    return STATE / "manual-runs" / f"{run_id}.large.json"


def prepare_large_manual(args: argparse.Namespace) -> int:
    task = LARGE_TASK
    run_root = RUNS / args.run_id
    original_baseline = STATE / "manual-runs" / f"{args.run_id}.json"
    output = result_file(args.run_id)
    workspace = run_root / task["id"]
    baseline_path = large_manual_baseline_path(args.run_id)

    if not original_baseline.exists():
        print(
            f"Missing the original ten-task baseline manifest: {original_baseline}",
            file=sys.stderr,
        )
        return 2
    original_data = json.loads(original_baseline.read_text())
    manual_provider = original_data.get("provider", "zcode-manual")
    agent_name = original_data.get("agent_name", "ZCode desktop")
    if result_has_task(output, task["id"]):
        print(f"{task['id']} is already saved in {output}", file=sys.stderr)
        return 2
    if workspace.exists() or baseline_path.exists():
        print(
            "The large-task workspace or baseline already exists. Refusing to "
            "overwrite possible manual work.",
            file=sys.stderr,
        )
        return 2

    init_agent_workspace(task, workspace)
    install_agent_configs(workspace, manual_provider)
    baseline_path.write_text(
        json.dumps(
            {
                "task_id": task["id"],
                "head": git_head(workspace),
                "provider": manual_provider,
                "agent_name": agent_name,
            },
            indent=2,
        )
    )
    prompt = AGENT_POLICY + (PRIVATE / "prompts" / f"{task['id']}.md").read_text()
    (workspace / "PROMPT.md").write_text(prompt)
    guide = run_root / "LARGE_TASK.md"
    guide.write_text(
        "\n".join(
            [
                f"# Final large task for {args.run_id}",
                "",
                f"Task: `{task['id']}`",
                f"Folder: `{workspace}`",
                f"Prompt: `{workspace / 'PROMPT.md'}`",
                "Tests visible to agent: `no`",
                "",
                f"Open only this folder in a fresh {agent_name} session.",
                "Select the model being evaluated, paste PROMPT.md, use one attempt, and do not use web search.",
                "Do not open the benchmark source directory or any of the ten earlier task folders.",
                "",
            ]
        )
    )
    files = sum(1 for path in workspace.rglob("*") if path.is_file())
    lines = sum(
        len(path.read_text(errors="ignore").splitlines())
        for path in workspace.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.suffix in {".py", ".rst", ".md", ".toml"}
    )
    print("Added the final task without modifying the ten existing task folders.")
    print(f"Workspace: {workspace}")
    print(f"Instructions: {guide}")
    print(f"Approximate context: {files} files, {lines} Python/docs/config lines")
    return 0


def finalize_large_manual(args: argparse.Namespace) -> int:
    task = LARGE_TASK
    output = result_file(args.run_id)
    workspace = RUNS / args.run_id / task["id"]
    baseline_path = large_manual_baseline_path(args.run_id)

    if not output.exists():
        print(
            "Finalize the original ten tasks first with "
            f"`python3 bench.py finalize-manual-run --run-id {args.run_id}`.",
            file=sys.stderr,
        )
        return 2
    if result_has_task(output, task["id"]):
        print(f"{task['id']} is already saved in {output}", file=sys.stderr)
        return 2
    if not workspace.exists() or not baseline_path.exists():
        print("Prepare and complete the large manual task first.", file=sys.stderr)
        return 2

    baseline = json.loads(baseline_path.read_text())
    manual_provider = baseline.get("provider", "zcode-manual")
    agent_name = baseline.get("agent_name", "ZCode desktop application")
    patch = git_metrics(workspace)
    score = score_agent_workspace(
        task,
        workspace,
        f"{args.run_id}-{task['id']}",
        baseline["head"],
        manual_provider,
    )
    append_result(
        output,
        {
            "suite": "private-large",
            "run_id": args.run_id,
            "task_id": task["id"],
            "provider": manual_provider,
            "agent": {
                "command": [agent_name],
                "exit_code": 0,
                "timed_out": False,
                "wall_seconds": 0,
                "stdout": "",
                "stderr": "",
            },
            "score": score,
            "patch": patch,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
    )
    print(f"{task['id']}: {'PASS' if score['passed'] else 'FAIL'}")
    print(f"Appended the final task to: {output}")
    return 0


def run_large(args: argparse.Namespace) -> int:
    task = LARGE_TASK
    output = result_file(args.run_id)
    workspace = RUNS / args.run_id / task["id"]

    if not output.exists():
        print(
            "Run and save the original ten automated tasks first, then append "
            "the final large task with this command.",
            file=sys.stderr,
        )
        return 2
    if result_has_task(output, task["id"]):
        print(f"{task['id']} is already saved in {output}", file=sys.stderr)
        return 2
    if workspace.exists():
        print(
            f"Refusing to overwrite an existing large-task workspace: {workspace}",
            file=sys.stderr,
        )
        return 2

    init_agent_workspace(task, workspace)
    install_agent_configs(workspace, args.provider)
    expected_head = git_head(workspace)
    prompt = (PRIVATE / "prompts" / f"{task['id']}.md").read_text()
    command, env = provider_command(args.provider, workspace, prompt)
    if env.get("ZCODE_BENCH_CONFIG_MISSING"):
        print("Missing provider configuration.", file=sys.stderr)
        return 2
    if env.get("ZCODE_DIRECT_LOGIN_MISSING"):
        print("Direct OAuth login is missing.", file=sys.stderr)
        return 2

    print(f"Running final large task via {args.provider}; timeout={args.agent_timeout}s")
    agent = run_agent(
        command,
        workspace,
        args.agent_timeout,
        env,
        args.unsafe_no_sandbox,
    )
    patch = git_metrics(workspace)
    score = score_agent_workspace(
        task,
        workspace,
        f"{args.run_id}-{task['id']}",
        expected_head,
        args.provider,
    )
    append_result(
        output,
        {
            "suite": "private-large",
            "run_id": args.run_id,
            "task_id": task["id"],
            "provider": provider_label(args.provider),
            "agent": agent,
            "score": score,
            "patch": patch,
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
    )
    print(
        f"{task['id']}: {'PASS' if score['passed'] else 'FAIL'} "
        f"{agent['wall_seconds']}s {patch['files_changed']} files"
    )
    print(f"Appended the final task to: {output}")
    return 0


def score_command(args: argparse.Namespace) -> int:
    task = next((t for t in load_tasks() if t["id"] == args.task), None)
    if not task:
        raise SystemExit(f"Unknown task: {args.task}")
    workspace = Path(args.workspace).resolve()
    score = score_private(task, workspace)
    print(json.dumps(score, indent=2))
    return 0 if score["passed"] else 1


def doctor(_: argparse.Namespace) -> int:
    checks = {
        "benchmark": "Private Code Agent Benchmark",
        "platform": f"{platform.system()} {platform.machine()}",
        "python": sys.version.split()[0],
        "git": shutil.which("git"),
        "node": shutil.which("node"),
        "opencode": shutil.which("opencode"),
        "zcode_bundle": str(ZCODE_JS) if ZCODE_JS.exists() else None,
        "docker": shutil.which("docker"),
        "uv": shutil.which("uv"),
        "go": shutil.which("go"),
        "cargo": shutil.which("cargo"),
        "java": shutil.which("java"),
        "cmake": shutil.which("cmake"),
        "zcode_config": str(ROOT / "zcode.json") if (ROOT / "zcode.json").exists() else None,
        "opencode_config": str(ROOT / "opencode.jsonc") if (ROOT / "opencode.jsonc").exists() else None,
        "zcode_direct_oauth_ready": all(path.exists() for path in direct_auth_sources()),
        "opencode_model": os.environ.get("OPENCODE_MODEL", "zcode-route/GLM-5.2"),
        "generic_agent_command_set": bool(os.environ.get("BENCH_AGENT_COMMAND")),
    }
    print(json.dumps(checks, indent=2))
    return 0


def list_command(_: argparse.Namespace) -> int:
    print("Private:")
    for task in load_tasks():
        print(f"  {task['id']}: {task['title']}")
    print("\nFinal large add-on:")
    print(f"  {LARGE_TASK['id']}: {LARGE_TASK['title']} (tests withheld)")
    print("\nPolyglot:")
    for task in CONFIG["polyglot_tasks"]:
        print(f"  {task['language']}/{task['task']}")
    print("\nSWE-bench Lite:")
    for task_id in CONFIG["swebench_instance_ids"]:
        print(f"  {task_id}")
    print(f"\nLiveCodeBench: newest {CONFIG['livecodebench']['count']} from {CONFIG['livecodebench']['start_date']}")
    return 0


def report(_: argparse.Namespace) -> int:
    rows = []
    for path in sorted(RESULTS.glob("*.jsonl")) if RESULTS.exists() else []:
        for line in path.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        print("No results yet.")
        return 0
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["run_id"], row["provider"]), []).append(row)
    print("| run | provider | passed | attempted | pass rate | compile/tool errors | avg seconds |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for (run_id, provider), group in sorted(grouped.items()):
        passed = sum(bool(r["score"]["passed"]) for r in group)
        errors = sum(r["agent"]["exit_code"] != 0 for r in group)
        avg = sum(r["agent"]["wall_seconds"] for r in group) / len(group)
        print(f"| {run_id} | {provider} | {passed} | {len(group)} | {passed/len(group):.1%} | {errors} | {avg:.1f} |")
    return 0


def show_results(args: argparse.Namespace) -> int:
    path = result_file(args.run_id)
    if not path.exists():
        print(f"Missing result file: {path}", file=sys.stderr)
        return 2
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0


def exact_sign_p_value(a_only: int, b_only: int) -> float:
    discordant = a_only + b_only
    if discordant == 0:
        return 1.0
    smaller = min(a_only, b_only)
    tail = sum(math.comb(discordant, k) for k in range(smaller + 1)) / (2**discordant)
    return min(1.0, 2 * tail)


def compare(args: argparse.Namespace) -> int:
    def read_run(run_id):
        path = result_file(run_id)
        if not path.exists():
            raise SystemExit(f"Missing result file: {path}")
        return {row["task_id"]: row for row in map(json.loads, path.read_text().splitlines())}

    left = read_run(args.run_a)
    right = read_run(args.run_b)
    task_ids = sorted(set(left) & set(right))
    if not task_ids:
        raise SystemExit("The runs have no tasks in common.")
    a_pass = b_pass = a_only = b_only = both = neither = 0
    print("| task | A | B | A files/lines | B files/lines |")
    print("|---|---:|---:|---:|---:|")
    for task_id in task_ids:
        a = left[task_id]
        b = right[task_id]
        ap = bool(a["score"]["passed"])
        bp = bool(b["score"]["passed"])
        a_pass += ap
        b_pass += bp
        if ap and bp:
            both += 1
        elif ap:
            a_only += 1
        elif bp:
            b_only += 1
        else:
            neither += 1
        am = a["patch"]
        bm = b["patch"]
        print(
            f"| {task_id} | {'PASS' if ap else 'FAIL'} | {'PASS' if bp else 'FAIL'} | "
            f"{am['files_changed']}/{am['lines_added'] + am['lines_deleted']} | "
            f"{bm['files_changed']}/{bm['lines_added'] + bm['lines_deleted']} |"
        )
    total = len(task_ids)
    print()
    print(f"A={args.run_a}: {a_pass}/{total} ({a_pass/total:.1%})")
    print(f"B={args.run_b}: {b_pass}/{total} ({b_pass/total:.1%})")
    print(f"paired outcomes: both={both}, A-only={a_only}, B-only={b_only}, neither={neither}")
    print(f"pass-rate delta A-B: {(a_pass-b_pass)/total:+.1%}")
    print(f"two-sided exact sign test on discordant tasks: p={exact_sign_p_value(a_only, b_only):.4f}")
    if total < 30:
        print("Caution: this is a small diagnostic battery; repeat with fresh private tasks before claiming a backend difference.")
    return 0


def mutate_partial_fix(task_id: str, source: str) -> str:
    replacements = {
        "lru-update": (
            "if node is not None:",
            "if node is not None and len(self.items) < self.capacity:",
        ),
        "config-precedence": (
            "result.update(source)",
            "result.update({key: value for key, value in source.items() if value})",
        ),
        "rate-window": (
            "self.events[0] <= cutoff",
            "self.events[0] < cutoff",
        ),
        "quoted-tokenizer": (
            "if quoted:\n        raise ValueError",
            "if False and quoted:\n        raise ValueError",
        ),
        "schema-migration": (
            "from copy import deepcopy",
            "from copy import copy as deepcopy",
        ),
        "csv-unicode": (
            'writer = csv.writer(output, lineterminator="\\n")',
            "writer = csv.writer(output)",
        ),
        "stable-toposort": (
            "node = ready.pop(0)",
            "node = sorted(ready)[0]\n        ready.remove(node)",
        ),
        "async-retry": (
            """        except Exception:
            if attempt == max_attempts - 1:
                raise
            await sleep(base_delay * (2**attempt))""",
            """        except Exception:
            await sleep(base_delay * (2**attempt))
            if attempt == max_attempts - 1:
                raise""",
        ),
        "dst-recurrence": (
            "overlap_policy=rule.overlap_policy",
            'overlap_policy="earliest"',
        ),
        "webdav-endpoint": (
            "if parsed.query or parsed.fragment:",
            "if parsed.fragment:",
        ),
    }
    old, new = replacements[task_id]
    if old not in source:
        raise RuntimeError(f"Mutation anchor missing for {task_id}")
    return source.replace(old, new, 1)


def hidden_test_count(hidden_dir: Path) -> int:
    return sum(
        1
        for path in hidden_dir.glob("test*.py")
        for line in path.read_text().splitlines()
        if re.match(r"^\s+def test_|^\s+async def test_", line)
    )


def quality_audit(_: argparse.Namespace) -> int:
    audit_root = Path("/private/tmp/private-code-agent-bench-quality-audit")
    failures = []
    print("| task | tests visible to agent | regression baseline | baseline rejected | reference passes | partial fix rejected | hidden edge tests |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for task in load_tasks():
        task_id = task["id"]
        implementation = IMPLEMENTATION_FILES[task_id]
        baseline_workspace = audit_root / task_id / "baseline"
        init_workspace(PRIVATE / "tasks" / task_id, baseline_workspace)
        baseline = score_private(task, baseline_workspace)

        reference_source = (PRIVATE / "oracle" / "reference" / f"{task_id}.py").read_text()
        reference_workspace = audit_root / task_id / "reference"
        init_workspace(PRIVATE / "tasks" / task_id, reference_workspace)
        (reference_workspace / implementation).write_text(reference_source)
        reference = score_private(task, reference_workspace)

        mutant_workspace = audit_root / task_id / "partial-fix"
        init_workspace(PRIVATE / "tasks" / task_id, mutant_workspace)
        (mutant_workspace / implementation).write_text(mutate_partial_fix(task_id, reference_source))
        mutant = score_private(task, mutant_workspace)

        count = hidden_test_count(PRIVATE / "hidden" / task_id)
        regression_green = baseline["visible"]["exit_code"] == 0
        baseline_rejected = not baseline["passed"]
        reference_passes = reference["passed"]
        mutant_rejected = not mutant["passed"]
        print(
            f"| {task_id} | {agent_can_see_tests(task)} | {regression_green} | "
            f"{baseline_rejected} | {reference_passes} | {mutant_rejected} | {count} |"
        )
        if not all((regression_green, baseline_rejected, reference_passes, mutant_rejected, count >= 5)):
            failures.append(task_id)
    if failures:
        print(f"Quality audit failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("Quality audit passed: exposed or withheld regression tests start green, every baseline fails private edge tests, reference fixes pass, and plausible partial fixes fail.")
    return 0


def install_large_reference(workspace: Path) -> None:
    patch = PRIVATE / "oracle" / "reference" / f"{LARGE_TASK['id']}.patch"
    result = run_cmd(["patch", "-p1", "-i", str(patch)], workspace, 30)
    if result["exit_code"] != 0:
        raise RuntimeError(result["stdout"] + result["stderr"])


def quality_audit_large(_: argparse.Namespace) -> int:
    task = LARGE_TASK
    task_id = task["id"]
    source_root = PRIVATE / "tasks" / task_id
    if not source_root.exists():
        print(
            "Large task is not initialized. Run `make setup` first.",
            file=sys.stderr,
        )
        return 2
    audit_root = Path("/private/tmp/private-code-agent-bench-large-quality-audit")

    baseline_workspace = audit_root / "baseline"
    init_agent_workspace(task, baseline_workspace)
    baseline = score_private(task, baseline_workspace)

    reference_workspace = audit_root / "reference"
    init_agent_workspace(task, reference_workspace)
    install_large_reference(reference_workspace)
    reference = score_private(task, reference_workspace)

    mutants = {}

    snapshot_only = audit_root / "snapshot-only"
    init_agent_workspace(task, snapshot_only)
    core_path = snapshot_only / "src" / "click" / "core.py"
    core = core_path.read_text()
    core = core.replace(
        "from types import TracebackType",
        "from types import MappingProxyType\nfrom types import TracebackType",
        1,
    ).replace(
        "        return self._parameter_source\n\n\nclass Command:",
        "        return MappingProxyType(self._parameter_source.copy())\n\n\nclass Command:",
        1,
    )
    core_path.write_text(core)
    decorator_path = snapshot_only / "src" / "click" / "decorators.py"
    decorator_path.write_text(
        decorator_path.read_text().replace(
            "get_current_context()._parameter_source",
            "get_current_context().parameter_sources",
            1,
        )
    )
    mutants["snapshot-only"] = score_private(task, snapshot_only)

    dispatch_only = audit_root / "dispatch-only"
    init_agent_workspace(task, dispatch_only)
    install_large_reference(dispatch_only)
    core_path = dispatch_only / "src" / "click" / "core.py"
    core_path.write_text(
        core_path.read_text().replace(
            "return MappingProxyType(self._parameter_source.copy())",
            "return self._parameter_source",
            1,
        )
    )
    decorator_path = dispatch_only / "src" / "click" / "decorators.py"
    decorator_path.write_text(
        decorator_path.read_text().replace(
            "get_current_context().parameter_sources",
            "get_current_context()._parameter_source",
            1,
        )
    )
    mutants["dispatch-only"] = score_private(task, dispatch_only)

    loses_forwarded_sources = audit_root / "loses-forwarded-sources"
    init_agent_workspace(task, loses_forwarded_sources)
    install_large_reference(loses_forwarded_sources)
    core_path = loses_forwarded_sources / "src" / "click" / "core.py"
    core = core_path.read_text().replace(
        "        return self._invoke_command(cmd, args, kwargs, sources)",
        "        return self.invoke(cmd, *args, **kwargs)",
        1,
    )
    core_path.write_text(core)
    mutants["loses-forwarded-sources"] = score_private(
        task, loses_forwarded_sources
    )

    ignores_child_default_map = audit_root / "ignores-child-default-map"
    init_agent_workspace(task, ignores_child_default_map)
    install_large_reference(ignores_child_default_map)
    core_path = ignores_child_default_map / "src" / "click" / "core.py"
    core = core_path.read_text().replace(
        """                resolved_sources[param.name] = (
                    ParameterSource.DEFAULT_MAP
                    if ctx._default_map_has(param.name)
                    else ParameterSource.DEFAULT
                )""",
        "                resolved_sources[param.name] = ParameterSource.DEFAULT",
        1,
    )
    core_path.write_text(core)
    mutants["ignores-child-default-map"] = score_private(
        task, ignores_child_default_map
    )

    file_count = sum(
        1
        for path in source_root.rglob("*")
        if path.is_file() and "tests" not in path.parts
    )
    line_count = sum(
        len(path.read_text(errors="ignore").splitlines())
        for path in source_root.rglob("*")
        if path.is_file()
        and "tests" not in path.parts
        and path.suffix in {".py", ".rst", ".md", ".toml"}
    )
    hidden_count = hidden_test_count(PRIVATE / "hidden" / task_id)
    regression_green = baseline["visible"]["exit_code"] == 0
    baseline_rejected = not baseline["passed"]
    reference_passes = reference["passed"]
    mutants_rejected = all(not score["passed"] for score in mutants.values())
    tests_withheld = not (baseline_workspace / "tests").exists()

    print("| check | result |")
    print("|---|---:|")
    print(f"| repository files exposed | {file_count} |")
    print(f"| Python/docs/config lines exposed | {line_count} |")
    print(f"| tests visible to agent | {not tests_withheld} |")
    print(f"| withheld regression baseline passes | {regression_green} |")
    print(f"| buggy baseline rejected privately | {baseline_rejected} |")
    print(f"| trusted reference passes | {reference_passes} |")
    print(f"| hidden test methods | {hidden_count} |")
    for name, score in mutants.items():
        print(f"| partial fix rejected: {name} | {not score['passed']} |")

    passed = all(
        (
            file_count >= 100,
            line_count >= 20_000,
            tests_withheld,
            regression_green,
            baseline_rejected,
            reference_passes,
            mutants_rejected,
            hidden_count >= 10,
        )
    )
    if not passed:
        print("Large-task quality audit failed.", file=sys.stderr)
        return 1
    print(
        "Large-task quality audit passed: the agent sees a substantial real "
        "repository but no tests, the reference fix passes, and four plausible "
        "partial fixes are rejected."
    )
    return 0


def security_audit(_: argparse.Namespace) -> int:
    workspace = RUNS / "security-audit" / "current"
    sibling = RUNS / "security-audit" / "sibling"
    init_workspace(PRIVATE / "tasks" / "lru-update", workspace)
    init_workspace(PRIVATE / "tasks" / "lru-update", sibling)
    probe = (
        "from pathlib import Path\n"
        "checks = {\n"
        f"'own': Path({str(workspace / 'lru.py')!r}),\n"
        f"'root': Path({str(ROOT / 'bench.py')!r}),\n"
        f"'hidden': Path({str(PRIVATE / 'hidden' / 'lru-update' / 'test_hidden.py')!r}),\n"
        f"'sibling': Path({str(sibling / 'lru.py')!r}),\n"
        "}\n"
        "results = {}\n"
        "for name, path in checks.items():\n"
        "    try:\n"
        "        path.read_bytes()\n"
        "        results[name] = True\n"
        "    except PermissionError:\n"
        "        results[name] = False\n"
        "print(results)\n"
        "raise SystemExit(0 if results == {'own': True, 'root': False, 'hidden': False, 'sibling': False} else 1)\n"
    )
    command = sandboxed_agent_command(["python3", "-c", probe], workspace)
    result = run_cmd(command, workspace, 30)
    print(result["stdout"] or result["stderr"])
    if result["exit_code"] != 0:
        print("Security audit failed; do not run private benchmarks.", file=sys.stderr)
        return 1
    print("Security audit passed: the agent can read only its current task among benchmark assets.")
    return 0


def smoke_provider(args: argparse.Namespace) -> int:
    workspace = RUNS / "provider-smoke" / args.provider
    init_empty_workspace(workspace)
    install_agent_configs(workspace, args.provider)
    command, env = provider_command(
        args.provider,
        workspace,
        "Reply with exactly OK. Do not edit files or use tools.",
    )
    if env.get("ZCODE_DIRECT_LOGIN_MISSING"):
        print("Direct ZCode OAuth state is missing.", file=sys.stderr)
        return 2
    result = run_agent(command, workspace, args.timeout, env, args.unsafe_no_sandbox)
    print(result["stdout"])
    if result["stderr"]:
        print(result["stderr"], file=sys.stderr)
    if result["exit_code"] != 0:
        print(f"{args.provider} smoke test failed.", file=sys.stderr)
        return result["exit_code"] or 1
    print(f"{args.provider} smoke test completed successfully.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Private repository-level code agent benchmark"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor").set_defaults(func=doctor)
    sub.add_parser("list").set_defaults(func=list_command)
    run = sub.add_parser("run-private")
    run.add_argument("--provider", choices=PROVIDER_CHOICES, required=True)
    run.add_argument("--run-id")
    run.add_argument("--task", action="append")
    run.add_argument("--limit", type=int)
    run.add_argument("--agent-timeout", type=int, default=900)
    run.add_argument("--unsafe-no-sandbox", action="store_true")
    run.set_defaults(func=run_private)
    paired = sub.add_parser("run-paired-private")
    paired.add_argument("--run-id")
    paired.add_argument("--task", action="append")
    paired.add_argument("--limit", type=int)
    paired.add_argument("--agent-timeout", type=int, default=900)
    paired.add_argument("--unsafe-no-sandbox", action="store_true")
    paired.add_argument("--seed", type=int)
    paired.add_argument("--opencode-first", action="store_true")
    paired.set_defaults(func=run_paired_private)
    prepare = sub.add_parser("prepare-private")
    prepare.add_argument("--task", required=True)
    prepare.add_argument("--run-id")
    prepare.set_defaults(func=prepare_private)
    manual = sub.add_parser("prepare-manual-run")
    manual.add_argument("--run-id", required=True)
    manual.add_argument("--profile", choices=["none", "zcode"], default="none")
    manual.set_defaults(func=prepare_manual_run)
    finalize = sub.add_parser("finalize-manual-run")
    finalize.add_argument("--run-id", required=True)
    finalize.set_defaults(func=finalize_manual_run)
    prepare_large = sub.add_parser("prepare-large-manual")
    prepare_large.add_argument("--run-id", required=True)
    prepare_large.set_defaults(func=prepare_large_manual)
    finalize_large = sub.add_parser("finalize-large-manual")
    finalize_large.add_argument("--run-id", required=True)
    finalize_large.set_defaults(func=finalize_large_manual)
    run_large_parser = sub.add_parser("run-large")
    run_large_parser.add_argument("--provider", choices=PROVIDER_CHOICES, required=True)
    run_large_parser.add_argument("--run-id", required=True)
    run_large_parser.add_argument("--agent-timeout", type=int, default=3600)
    run_large_parser.add_argument("--unsafe-no-sandbox", action="store_true")
    run_large_parser.set_defaults(func=run_large)
    score = sub.add_parser("score-private")
    score.add_argument("--task", required=True)
    score.add_argument("--workspace", required=True)
    score.set_defaults(func=score_command)
    sub.add_parser("report").set_defaults(func=report)
    show = sub.add_parser("show-results")
    show.add_argument("--run-id", required=True)
    show.set_defaults(func=show_results)
    comparison = sub.add_parser("compare")
    comparison.add_argument("--run-a", required=True)
    comparison.add_argument("--run-b", required=True)
    comparison.set_defaults(func=compare)
    sub.add_parser("quality-audit").set_defaults(func=quality_audit)
    sub.add_parser("quality-audit-large").set_defaults(func=quality_audit_large)
    sub.add_parser("security-audit").set_defaults(func=security_audit)
    smoke = sub.add_parser("smoke-provider")
    smoke.add_argument("--provider", choices=PROVIDER_CHOICES, required=True)
    smoke.add_argument("--timeout", type=int, default=180)
    smoke.add_argument("--unsafe-no-sandbox", action="store_true")
    smoke.set_defaults(func=smoke_provider)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    sys.exit(parsed.func(parsed))
