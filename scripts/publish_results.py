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
FULL_TASK_COUNT = 11


def load_records(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize(meta: dict, records: list[dict]) -> dict:
    tasks = []
    for record in records:
        seconds = record["agent"].get("wall_seconds")
        if not meta["times_recorded"]:
            seconds = None
        tasks.append(
            {
                "task_id": record["task_id"],
                "passed": bool(record["score"]["passed"]),
                "seconds": round(seconds, 3) if seconds is not None else None,
            }
        )

    attempted = len(tasks)
    passed = sum(task["passed"] for task in tasks)
    total_seconds = sum(task["seconds"] or 0 for task in tasks)
    complete = meta["scope"] == "full" and attempted == FULL_TASK_COUNT
    return {
        **meta,
        "complete": complete,
        "passed": passed,
        "attempted": attempted,
        "pass_rate": round(100 * passed / attempted, 1) if attempted else 0,
        "total_seconds": (
            round(total_seconds, 3) if meta["times_recorded"] else None
        ),
        "tasks": tasks,
    }


def render_chart(runs: list[dict]) -> str:
    ranked = sorted(
        (run for run in runs if run["scope"] == "full" and run["complete"]),
        key=lambda run: (-run["pass_rate"], run["label"]),
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
        filled = bar_width * run["pass_rate"] / 100
        label = html.escape(run["label"])
        score = f'{run["passed"]}/{run["attempted"]} ({run["pass_rate"]:.1f}%)'
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
            '<title id="title">Full-suite benchmark pass rates</title>',
            '<desc id="desc">Pass rates for complete eleven-task benchmark runs.</desc>',
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
            '<text x="24" y="36" class="heading">Full-suite pass rates</text>',
            '<text x="24" y="58" class="score">Eleven tasks, one attempt per task</text>',
            *rows,
            "</svg>",
            "",
        ]
    )


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    runs = []
    for meta in metadata:
        path = RESULTS / f'{meta["run_id"]}.jsonl'
        if path.exists():
            runs.append(summarize(meta, load_records(path)))

    payload = {
        "schema_version": 1,
        "suite_tasks": FULL_TASK_COUNT,
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    CHART.write_text(render_chart(runs), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {CHART.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
