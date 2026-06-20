"""Trusted multi-runtime grader. This file is denied to benchmark agents."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: multi_runtime_grader.py WORKSPACE TEST_DIR")
    workspace = pathlib.Path(sys.argv[1]).resolve()
    tests = pathlib.Path(sys.argv[2]).resolve()
    spec = importlib.util.spec_from_file_location("bench_grade", tests / "grade.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load grader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = module.grade(workspace, tests)
    earned = sum(float(check["points"]) for check in checks if check["passed"])
    total = sum(float(check["points"]) for check in checks)
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        detail = check.get("detail", "")
        print(f"{status} {check['name']} ({check['points']} points) {detail}")
    payload = {"earned": earned, "total": total, "checks": checks}
    print("BENCH_POINTS_JSON:" + json.dumps(payload, sort_keys=True))
    return 0 if earned == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
