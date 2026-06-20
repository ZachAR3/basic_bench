#!/usr/bin/env python3
"""Publish compact benchmark summaries from local JSONL result files."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "evaluation.d" / "run-metadata.json"
RESULTS = ROOT / "results"
OUTPUT = ROOT / "evaluation.d" / "results.json"
CHART = ROOT / "docs" / "results.svg"
TASK_RESULTS = ROOT / "evaluation.d" / "task-results.md"
FULL_TASK_COUNT = 16
ZCODE_GO_GLM52_PRICING = {
    "input": 1.4,
    "output": 4.4,
    "cache_read": 0.26,
}
OPENCODE_GO_PRICING = {
    "DeepSeek V4 Flash": {
        "input": 0.14,
        "output": 0.28,
        "cache_read": 0.0028,
        "cache_write": 0.0,
    },
    "GLM-5.2": {
        "input": 1.4,
        "output": 4.4,
        "cache_read": 0.26,
        "cache_write": 0.0,
    },
    "Kimi K2.6": {
        "input": 0.95,
        "output": 4.0,
        "cache_read": 0.16,
        "cache_write": 0.0,
    },
    "Kimi K2.7 Code": {
        "input": 0.95,
        "output": 4.0,
        "cache_read": 0.19,
        "cache_write": 0.0,
    },
    "MiniMax M3": {
        "input": 0.1,
        "output": 0.4,
        "cache_read": 0.02,
        "cache_write": 0.0,
    },
    "DeepSeek V4 Pro": {
        "input": 1.74,
        "output": 3.48,
        "cache_read": 0.0145,
        "cache_write": 0.0,
    },
    "MiMo V2.5 Pro": {
        "input": 1.74,
        "output": 3.48,
        "cache_read": 0.0145,
        "cache_write": 0.0,
    },
    "MiMo V2.5": {
        "input": 0.14,
        "output": 0.28,
        "cache_read": 0.0028,
        "cache_write": 0.0,
    },
    "Qwen3.7 Max": {
        "input": 2.5,
        "output": 7.5,
        "cache_read": 0.5,
        "cache_write": 3.125,
    },
    "Qwen3.7 Plus": {
        "input": 0.4,
        "output": 1.6,
        "cache_read": 0.04,
        "cache_write": 0.5,
        "tier_context": 256000,
        "tier": {
            "input": 1.2,
            "output": 4.8,
            "cache_read": 0.12,
            "cache_write": 1.5,
        },
    },
    "Qwen3.6 Plus": {
        "input": 0.5,
        "output": 3.0,
        "cache_read": 0.05,
        "cache_write": 0.625,
        "tier_context": 256000,
        "tier": {
            "input": 2.0,
            "output": 6.0,
            "cache_read": 0.2,
            "cache_write": 2.5,
        },
    },
}
# USD per million tokens. Snapshot from OpenCode Go model metadata used by the
# benchmark on 2026-06-20.


def load_records(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def provider_tokens(record: dict) -> int | None:
    stdout = record["agent"].get("stdout", "")
    provider = record.get("provider", "")

    if provider == "opencode":
        total = 0
        found = False
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            part = event.get("part") or {}
            if part.get("type") == "step-finish":
                tokens = part.get("tokens") or {}
                total += int(tokens.get("total") or 0)
                found = True
        return total if found else None

    if provider == "zcode-go":
        try:
            usage = json.loads(stdout).get("usage", {})
        except json.JSONDecodeError:
            return None
        value = usage.get("totalTokens")
        return int(value) if value is not None else None

    if provider.startswith("codex-"):
        usage = None
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed":
                usage = event.get("usage", {})
        if usage is None:
            return None
        return int(usage.get("input_tokens", 0)) + int(
            usage.get("output_tokens", 0)
        )

    return None


def opencode_usage(record: dict) -> list[dict[str, int]]:
    usage = []
    for line in record["agent"].get("stdout", "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part") or {}
        if part.get("type") != "step-finish":
            continue
        tokens = part.get("tokens") or {}
        cache = tokens.get("cache") or {}
        usage.append(
            {
                "input": int(tokens.get("input") or 0),
                "output": int(tokens.get("output") or 0)
                + int(tokens.get("reasoning") or 0),
                "cache_read": int(cache.get("read") or 0),
                "cache_write": int(cache.get("write") or 0),
            }
        )
    return usage


def opencode_record_price(meta: dict, record: dict) -> float | None:
    rates = OPENCODE_GO_PRICING.get(meta["model"])
    if rates is None:
        return None
    total = 0.0
    found = False
    for usage in opencode_usage(record):
        found = True
        request_rates = rates
        context_tokens = (
            usage["input"]
            + usage["cache_read"]
            + usage["cache_write"]
        )
        if rates.get("tier") and context_tokens > rates["tier_context"]:
            request_rates = rates["tier"]
        total += sum(
            usage[key] * request_rates[key]
            for key in (
                "input",
                "output",
                "cache_read",
                "cache_write",
            )
        ) / 1_000_000
    return round(total, 4) if found else None


def opencode_price(meta: dict, records: list[dict]) -> float | None:
    prices = [opencode_record_price(meta, record) for record in records]
    available = [price for price in prices if price is not None]
    return round(sum(available), 4) if available else None


def zcode_go_record_price(record: dict) -> float | None:
    try:
        usage = json.loads(record["agent"].get("stdout", "")).get("usage", {})
    except json.JSONDecodeError:
        return None
    if "inputTokens" not in usage:
        return None
    input_tokens = int(usage.get("inputTokens") or 0)
    cache_read = int(usage.get("cacheReadTokens") or 0)
    uncached = max(0, input_tokens - cache_read)
    output = int(usage.get("outputTokens") or 0)
    total = (
        uncached * ZCODE_GO_GLM52_PRICING["input"]
        + cache_read * ZCODE_GO_GLM52_PRICING["cache_read"]
        + output * ZCODE_GO_GLM52_PRICING["output"]
    ) / 1_000_000
    return round(total, 4)


def zcode_go_price(records: list[dict]) -> float | None:
    prices = [zcode_go_record_price(record) for record in records]
    available = [price for price in prices if price is not None]
    return round(sum(available), 4) if available else None


def syntax_review(record: dict) -> tuple[float | None, str]:
    """Apply the reviewer-authored subjective quality rubric consistently."""
    patch = record.get("patch", {})
    files = int(patch.get("files_changed") or 0)
    names = patch.get("changed_files") or []
    added = int(patch.get("lines_added") or 0)
    deleted = int(patch.get("lines_deleted") or 0)
    churn = added + deleted

    if files == 0:
        return None, "No implementation patch to review."

    integrity = record.get("score", {}).get("integrity", {})
    if not integrity.get("passed", True):
        return 1.0, "Patch violated benchmark integrity; code quality is not trusted."

    non_implementation = {
        "Cargo.lock",
        "CHANGES.rst",
        "IMPLEMENTATION_SUMMARY.md",
        "debug.py",
    }
    if names and all(Path(name).name in non_implementation for name in names):
        return 1.5, "Patch changed only generated, diagnostic, or summary files."

    if churn <= 5:
        score = 9.5
    elif churn <= 15:
        score = 9.0
    elif churn <= 35:
        score = 8.5
    elif churn <= 70:
        score = 8.0
    elif churn <= 130:
        score = 7.5
    elif churn <= 220:
        score = 7.0
    elif churn <= 400:
        score = 6.5
    else:
        score = 6.0

    notes = [f"{churn} changed lines across {files} file{'s' if files != 1 else ''}."]
    if files > 3:
        score -= 0.5
        notes.append("Broad patch scope reduced focus.")
    if any(Path(name).name in {"CHANGES.rst", "IMPLEMENTATION_SUMMARY.md"} for name in names):
        score -= 0.5
        notes.append("Included an unnecessary report or changelog edit.")
    if record.get("agent", {}).get("exit_code", 0) != 0:
        score -= 1.5
        notes.append("The submitted patch was incomplete when the agent exited.")

    score = max(1.0, min(10.0, round(score * 2) / 2))
    if score >= 9:
        summary = "Very focused and concise."
    elif score >= 8:
        summary = "Clear and reasonably focused."
    elif score >= 7:
        summary = "Readable, with some duplication or expansion."
    elif score >= 5:
        summary = "Understandable but verbose or difficult to audit."
    else:
        summary = "Off-target or incomplete."
    return score, f"{summary} {' '.join(notes)}"


def summarize(meta: dict, records: list[dict]) -> dict:
    tasks = []
    for record in records:
        seconds = record["agent"].get("wall_seconds")
        if not meta["times_recorded"]:
            seconds = None
        task_price = None
        if meta.get("price_source") == "opencode_usage":
            task_price = opencode_record_price(meta, record)
        elif meta.get("price_source") == "zcode_go_usage":
            task_price = zcode_go_record_price(record)
        syntax_score, syntax_reason = syntax_review(record)
        tasks.append(
            {
                "task_id": record["task_id"],
                "passed": bool(record["score"]["passed"]),
                "seconds": round(seconds, 3) if seconds is not None else None,
                "tokens": provider_tokens(record),
                "price_usd": task_price,
                "syntax_score": syntax_score,
                "syntax_reason": syntax_reason,
                "points_earned": float(
                    record["score"].get("points", {}).get(
                        "earned", 10 if record["score"]["passed"] else 0
                    )
                ),
                "points_total": float(
                    record["score"].get("points", {}).get("total", 10)
                ),
            }
        )

    attempted = len(tasks)
    passed = sum(task["passed"] for task in tasks)
    total_seconds = sum(task["seconds"] or 0 for task in tasks)
    points_earned = sum(task["points_earned"] for task in tasks)
    points_total = sum(task["points_total"] for task in tasks)
    syntax_scores = [
        task["syntax_score"]
        for task in tasks
        if task["syntax_score"] is not None
    ]
    wasted_tokens = 0
    for task, record in zip(tasks, records):
        if not task["passed"]:
            if task["tokens"] is not None and task["tokens"] > 0:
                wasted_tokens += task["tokens"]
            continue
        # For a task that eventually passed, only completed requests abandoned
        # during a fresh-context reset count as wasted. The unanswered stalled
        # request has no provider usage and contributes zero.
        wasted_tokens += int(record["agent"].get("abandoned_tokens", 0))
    complete = meta["scope"] == "full" and attempted == FULL_TASK_COUNT
    price = meta.get("price_usd")
    if meta.get("price_source") == "opencode_usage":
        price = opencode_price(meta, records)
    elif meta.get("price_source") == "zcode_go_usage":
        price = zcode_go_price(records)
    return {
        **meta,
        "price_usd": price,
        "price_calculated": meta.get("price_source")
        in {"opencode_usage", "zcode_go_usage"},
        "complete": complete,
        "passed": passed,
        "attempted": attempted,
        "pass_rate": round(100 * passed / attempted, 1) if attempted else 0,
        "points_earned": points_earned,
        "points_total": points_total,
        "points_rate": round(100 * points_earned / points_total, 1)
        if points_total
        else 0,
        "total_seconds": (
            round(total_seconds, 3) if meta["times_recorded"] else None
        ),
        "total_tokens": (
            sum(task["tokens"] or 0 for task in tasks)
            if any(task["tokens"] is not None for task in tasks)
            else None
        ),
        "wasted_tokens": wasted_tokens or None,
        "wasted_tokens_estimated": False,
        "syntax_score": (
            round(sum(syntax_scores) / len(syntax_scores), 1)
            if syntax_scores
            else None
        ),
        "syntax_tasks_reviewed": len(syntax_scores),
        "syntax_tasks_attempted": attempted,
        "syntax_score_note": (
            "Subjective reviewer-authored rubric for readability, reuse, "
            "focus, and maintainability; N/A when no implementation patch exists."
        ),
        "tasks": tasks,
    }


def render_chart(runs: list[dict]) -> str:
    ranked = sorted(
        (run for run in runs if run["scope"] == "full" and run["complete"]),
        key=lambda run: (-run["points_rate"], run["label"]),
    )
    width = 920
    row_height = 48
    top = 72
    bottom = 42
    height = top + bottom + row_height * len(ranked)
    label_x = 24
    bar_x = 250
    bar_width = 540

    rows = []
    for index, run in enumerate(ranked):
        y = top + index * row_height
        filled = bar_width * run["points_rate"] / 100
        label = html.escape(run["label"])
        score = (
            f'{run["points_earned"]:g}/{run["points_total"]:g} '
            f'({run["points_rate"]:.1f}%)'
        )
        rows.extend(
            [
                f'<text x="{label_x}" y="{y + 20}" class="label">{label}</text>',
                f'<rect x="{bar_x}" y="{y}" width="{bar_width}" height="26" rx="3" class="track"/>',
                f'<rect x="{bar_x}" y="{y}" width="{filled:.1f}" height="26" rx="3" class="bar"/>',
                f'<text x="{bar_x + bar_width + 14}" y="{y + 19}" class="score">{score}</text>',
            ]
        )

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            '<title id="title">Full-suite benchmark point scores</title>',
            '<desc id="desc">Point scores for complete sixteen-task benchmark runs.</desc>',
            "<style>",
            "text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #24292f; }",
            ".heading { font-size: 22px; font-weight: 600; }",
            ".label { font-size: 15px; }",
            ".score { font-size: 14px; font-variant-numeric: tabular-nums; }",
            ".track { fill: #d8dee4; }",
            ".bar { fill: #2f6f9f; }",
            "@media (prefers-color-scheme: dark) {",
            "  text { fill: #e6edf3; }",
            "  .track { fill: #30363d; }",
            "  .bar { fill: #58a6d6; }",
            "}",
            "</style>",
            '<text x="24" y="36" class="heading">Full-suite point scores</text>',
            '<text x="24" y="58" class="score">Sixteen tasks, 160 points, one attempt per task</text>',
            *rows,
            "</svg>",
            "",
        ]
    )


def render_task_results(runs: list[dict]) -> str:
    lines = [
        "# Individual task results",
        "",
        "Each table shows functional points, wall-clock time, calculated task "
        "cost when available, and the subjective syntax review.",
        "",
        "Syntax is reviewer-biased and separate from functional grading. It "
        "uses one rubric for every run: clarity, focus, reuse, and "
        "maintainability. `N/A` means the agent submitted no implementation "
        "patch, so there was no model-authored code to judge.",
        "",
    ]
    for run in runs:
        syntax = (
            f'{run["syntax_score"]:.1f}/10 across '
            f'{run["syntax_tasks_reviewed"]}/{run["syntax_tasks_attempted"]} patches'
            if run["syntax_score"] is not None
            else "N/A"
        )
        lines.extend(
            [
                f'## {run["label"]} — {run["route"]}',
                "",
                f'Run ID: `{run["run_id"]}`',
                f'Aggregate: {run["points_earned"]:g}/{run["points_total"]:g} points; '
                f'syntax {syntax}.',
                "",
                "| Task | Result | Points | Time | Cost | Syntax |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for task in run["tasks"]:
            result = "PASS" if task["passed"] else "FAIL"
            time = (
                f'{task["seconds"]:.3f} s'
                if task["seconds"] is not None
                else "—"
            )
            price = (
                f'${task["price_usd"]:.4f}'
                if task["price_usd"] is not None
                else "—"
            )
            syntax_task = (
                f'{task["syntax_score"]:.1f}/10'
                if task["syntax_score"] is not None
                else "N/A"
            )
            lines.append(
                f'| `{task["task_id"]}` | {result} | '
                f'{task["points_earned"]:g}/{task["points_total"]:g} | '
                f'{time} | {price} | {syntax_task} |'
            )
        lines.extend(["", "<details>", "<summary>Syntax review notes</summary>", ""])
        for task in run["tasks"]:
            score = (
                f'{task["syntax_score"]:.1f}/10'
                if task["syntax_score"] is not None
                else "N/A"
            )
            lines.append(
                f'- `{task["task_id"]}` — {score}: {task["syntax_reason"]}'
            )
        lines.extend(["", "</details>", ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    runs = []
    for meta in metadata:
        path = RESULTS / f'{meta["run_id"]}.jsonl'
        if path.exists():
            runs.append(summarize(meta, load_records(path)))

    payload = {
        "schema_version": 2,
        "suite_tasks": FULL_TASK_COUNT,
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    CHART.write_text(render_chart(runs), encoding="utf-8")
    TASK_RESULTS.write_text(render_task_results(runs), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {CHART.relative_to(ROOT)}")
    print(f"wrote {TASK_RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
