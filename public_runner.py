#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import bench

ROOT = Path(__file__).resolve().parent
CONFIG = bench.CONFIG


def collect_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from collect_strings(item)
    elif isinstance(value, dict):
        preferred = ("text", "content", "response", "message", "output", "answer")
        for key in preferred:
            if key in value:
                yield from collect_strings(value[key])


def response_text(stdout: str) -> str:
    strings = []
    for line in stdout.splitlines():
        try:
            strings.extend(collect_strings(json.loads(line)))
        except json.JSONDecodeError:
            strings.append(line)
    return "\n".join(s for s in strings if s)


def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def run_polyglot(args):
    selected = CONFIG["polyglot_tasks"]
    if args.language:
        wanted = set(args.language)
        selected = [task for task in selected if task["language"] in wanted]
    run_id = args.run_id or f"polyglot-{args.provider}"
    output = bench.result_file(run_id)
    if output.exists():
        raise SystemExit(f"Result file already exists; choose a new --run-id: {output}")
    for index, task in enumerate(selected, start=1):
        source = (
            ROOT
            / "vendor"
            / "polyglot-benchmark"
            / task["language"]
            / "exercises"
            / "practice"
            / task["task"]
        )
        if not source.exists():
            raise SystemExit(f"Missing benchmark task: {source}")
        workspace = bench.RUNS / run_id / f"{task['language']}-{task['task']}"
        bench.init_workspace(source, workspace)
        bench.install_agent_configs(workspace, args.provider)
        scrub_reference_solutions(workspace)
        instructions = workspace / ".docs" / "instructions.md"
        task_text = instructions.read_text() if instructions.exists() else "Implement the missing exercise."
        prompt = (
            f"Implement this {task['language']} exercise so all existing tests pass. "
            "Make the smallest focused change and do not modify tests.\n\n"
            f"{task_text}"
        )
        command, env = bench.provider_command(args.provider, workspace, prompt)
        print(f"[{index}/{len(selected)}] {task['language']}/{task['task']}")
        agent = bench.run_agent(command, workspace, args.agent_timeout, env, args.unsafe_no_sandbox)
        test = bench.run_cmd(task["test_command"], workspace, args.test_timeout, os.environ.copy())
        patch = bench.git_metrics(workspace)
        record = {
            "suite": "polyglot",
            "run_id": run_id,
            "task_id": f"{task['language']}/{task['task']}",
            "provider": args.provider,
            "agent": agent,
            "score": {"passed": test["exit_code"] == 0, "test": test},
            "patch": patch,
        }
        bench.append_result(output, record)
        print(f"  {'PASS' if record['score']['passed'] else 'FAIL'}")
    print(output)


def import_livecodebench():
    repo = ROOT / "vendor" / "LiveCodeBench"
    sys.path.insert(0, str(repo))
    previous = Path.cwd()
    try:
        os.chdir(repo)
        from lcb_runner.benchmarks.code_generation import load_code_generation_dataset
        from lcb_runner.evaluation import codegen_metrics
        from lcb_runner.prompts.code_generation import (
            PromptConstants,
            get_generic_question_template_answer,
        )
    finally:
        os.chdir(previous)
    return load_code_generation_dataset, codegen_metrics, PromptConstants, get_generic_question_template_answer


def scrub_reference_solutions(workspace: Path) -> None:
    candidates = [
        workspace / ".meta" / "src" / "reference",
        workspace / ".meta" / "example.py",
        workspace / ".meta" / "example.go",
        workspace / ".meta" / "example.rs",
        workspace / ".meta" / "example.cpp",
        workspace / ".meta" / "example.h",
        workspace / ".meta" / "Cargo-example.toml",
    ]
    for path in candidates:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    subprocess.run(["git", "add", "-A"], cwd=workspace, check=True)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "benchmark",
            "GIT_AUTHOR_EMAIL": "benchmark@local",
            "GIT_COMMITTER_NAME": "benchmark",
            "GIT_COMMITTER_EMAIL": "benchmark@local",
        }
    )
    subprocess.run(["git", "commit", "--amend", "--no-edit", "--quiet"], cwd=workspace, env=env, check=True)


def run_livecodebench(args):
    loader, codegen_metrics, constants, formatter = import_livecodebench()
    settings = CONFIG["livecodebench"]
    problems = loader(
        settings["release"],
        start_date=args.start_date or settings["start_date"],
    )
    problems = sorted(problems, key=lambda problem: problem.contest_date, reverse=True)
    problems = problems[: args.count or settings["count"]]
    run_id = args.run_id or f"lcb-{args.provider}"
    result_dir = bench.RESULTS / run_id
    if result_dir.exists():
        raise SystemExit(f"Result directory already exists; choose a new --run-id: {result_dir}")
    generations = []
    records = []
    for index, problem in enumerate(problems, start=1):
        workspace = bench.RUNS / run_id / f"task-{index:02d}"
        bench.init_empty_workspace(workspace)
        bench.install_agent_configs(workspace, args.provider)
        prompt = constants.SYSTEM_MESSAGE_GENERIC + "\n\n" + formatter(problem)
        command, env = bench.provider_command(args.provider, workspace, prompt)
        print(f"[{index}/{len(problems)}] {problem.question_id} {problem.contest_date.date()}")
        agent = bench.run_agent(command, workspace, args.agent_timeout, env, args.unsafe_no_sandbox)
        text = response_text(agent["stdout"])
        code = extract_code(text)
        generations.append([code])
        records.append(
            {
                "question_id": problem.question_id,
                "contest_date": problem.contest_date.isoformat(),
                "agent": agent,
                "code": code,
            }
        )
    samples = [problem.get_evaluation_sample() for problem in problems]
    metrics = codegen_metrics(
        samples,
        generations,
        k_list=[1],
        num_process_evaluate=args.workers,
        timeout=settings["timeout_seconds"],
    )
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "generations.json").write_text(json.dumps(records, indent=2))
    (result_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str))
    print(result_dir)


def load_swe_dataset():
    from datasets import load_dataset
    return load_dataset("princeton-nlp/SWE-bench_Lite", split="test")


def run_swe(args):
    dataset = load_swe_dataset()
    by_id = {row["instance_id"]: row for row in dataset}
    ids = args.instance or CONFIG["swebench_instance_ids"]
    run_id = args.run_id or f"swe-{args.provider}"
    predictions_path = bench.RESULTS / f"{run_id}-predictions.jsonl"
    if predictions_path.exists():
        raise SystemExit(f"Predictions already exist; choose a new --run-id: {predictions_path}")
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    with predictions_path.open("w") as predictions:
        for index, instance_id in enumerate(ids, start=1):
            row = by_id[instance_id]
            workspace = bench.RUNS / run_id / f"task-{index:02d}"
            if workspace.exists():
                shutil.rmtree(workspace)
            workspace.parent.mkdir(parents=True, exist_ok=True)
            workspace.mkdir()
            subprocess.run(["git", "init", "--quiet"], cwd=workspace, check=True)
            subprocess.run(
                ["git", "remote", "add", "origin", f"https://github.com/{row['repo']}.git"],
                cwd=workspace,
                check=True,
            )
            subprocess.run(
                ["git", "fetch", "--quiet", "--depth", "1", "origin", row["base_commit"]],
                cwd=workspace,
                check=True,
            )
            subprocess.run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=workspace, check=True)
            subprocess.run(["git", "remote", "remove", "origin"], cwd=workspace, check=True)
            subprocess.run(
                ["git", "reflog", "expire", "--expire=now", "--all"],
                cwd=workspace,
                check=True,
            )
            bench.install_agent_configs(workspace, args.provider)
            prompt = (
                "Resolve the issue below in the checked-out repository. Inspect the code and tests, "
                "make the smallest correct patch, and do not commit changes.\n\n" + row["problem_statement"]
            )
            command, env = bench.provider_command(args.provider, workspace, prompt)
            print(f"[{index}/{len(ids)}] {instance_id}")
            bench.run_agent(command, workspace, args.agent_timeout, env, args.unsafe_no_sandbox)
            patch = bench.git_metrics(workspace)["patch"]
            predictions.write(
                json.dumps(
                    {
                        "instance_id": instance_id,
                        "model_name_or_path": args.provider,
                        "model_patch": patch,
                    }
                )
                + "\n"
            )
    print(predictions_path)


def eval_swe(args):
    repo = ROOT / "vendor" / "SWE-bench"
    command = [
        sys.executable,
        "-m",
        "swebench.harness.run_evaluation",
        "--dataset_name",
        "princeton-nlp/SWE-bench_Lite",
        "--predictions_path",
        str(Path(args.predictions).resolve()),
        "--max_workers",
        str(args.workers),
        "--run_id",
        args.run_id,
        "--instance_ids",
        *(args.instance or CONFIG["swebench_instance_ids"]),
    ]
    if sys.platform == "darwin" and os.uname().machine == "arm64":
        command.extend(["--namespace", ""])
    raise SystemExit(subprocess.call(command, cwd=repo))


def parser():
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    poly = commands.add_parser("polyglot")
    poly.add_argument("--provider", choices=bench.PROVIDER_CHOICES, required=True)
    poly.add_argument("--language", action="append")
    poly.add_argument("--run-id")
    poly.add_argument("--agent-timeout", type=int, default=900)
    poly.add_argument("--test-timeout", type=int, default=600)
    poly.add_argument("--unsafe-no-sandbox", action="store_true")
    poly.set_defaults(func=run_polyglot)
    lcb = commands.add_parser("livecodebench")
    lcb.add_argument("--provider", choices=bench.PROVIDER_CHOICES, required=True)
    lcb.add_argument("--count", type=int)
    lcb.add_argument("--start-date")
    lcb.add_argument("--run-id")
    lcb.add_argument("--workers", type=int, default=2)
    lcb.add_argument("--agent-timeout", type=int, default=600)
    lcb.add_argument("--unsafe-no-sandbox", action="store_true")
    lcb.set_defaults(func=run_livecodebench)
    swe = commands.add_parser("swe")
    swe.add_argument("--provider", choices=bench.PROVIDER_CHOICES, required=True)
    swe.add_argument("--instance", action="append")
    swe.add_argument("--run-id")
    swe.add_argument("--agent-timeout", type=int, default=1800)
    swe.add_argument("--unsafe-no-sandbox", action="store_true")
    swe.set_defaults(func=run_swe)
    evaluate = commands.add_parser("eval-swe")
    evaluate.add_argument("--predictions", required=True)
    evaluate.add_argument("--instance", action="append")
    evaluate.add_argument("--workers", type=int, default=1)
    evaluate.add_argument("--run-id", required=True)
    evaluate.set_defaults(func=eval_swe)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    args.func(args)
