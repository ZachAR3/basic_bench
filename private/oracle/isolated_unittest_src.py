"""Trusted hidden-test runner for src-layout repositories."""

from __future__ import annotations

import pathlib
import sys
import unittest


workspace = pathlib.Path(sys.argv[1]).resolve()
tests = pathlib.Path(sys.argv[2]).resolve()

sys.path.insert(0, str(workspace / "src"))
sys.path.insert(0, str(tests))

suite = unittest.defaultTestLoader.discover(str(tests))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
