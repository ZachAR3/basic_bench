"""Trusted hidden-test runner. This file is denied to benchmark agents."""
from __future__ import annotations

import pathlib
import sys
import unittest


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: isolated_unittest.py WORKSPACE HIDDEN_TEST_DIR")
    workspace = pathlib.Path(sys.argv[1]).resolve()
    hidden = pathlib.Path(sys.argv[2]).resolve()
    # Python -I ignores PYTHONPATH, user site packages, and the working directory.
    # Add only the exact task and oracle directories after interpreter startup.
    sys.path.insert(0, str(workspace))
    sys.path.insert(0, str(hidden))
    suite = unittest.defaultTestLoader.discover(str(hidden))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
