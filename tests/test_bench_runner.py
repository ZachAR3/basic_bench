import subprocess
import unittest
from pathlib import Path
from unittest import mock

import bench


class OpenCodeRecoveryTests(unittest.TestCase):
    def result(self, **overrides):
        result = {
            "command": [],
            "exit_code": 0,
            "timed_out": False,
            "stalled": False,
            "wall_seconds": 1.0,
            "stdout": "",
            "stderr": "",
        }
        result.update(overrides)
        return result

    def test_stalled_session_is_continued(self):
        attempts = [
            self.result(
                exit_code=124,
                stalled=True,
                stdout='{"sessionID":"ses_test"}\n',
            ),
            self.result(stdout='{"sessionID":"ses_test","type":"step_finish"}\n'),
        ]
        commands = []

        def fake_run(command, *args, **kwargs):
            commands.append(command)
            return attempts.pop(0)

        with (
            mock.patch.object(bench, "run_cmd_with_idle_timeout", fake_run),
            mock.patch.object(bench.time, "sleep"),
        ):
            result = bench.run_opencode_agent(
                ["opencode", "run", "--format", "json", "task prompt"],
                Path("."),
                30,
                {},
                True,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["continuations"], 1)
        self.assertEqual(commands[1][-3:-1], ["--session", "ses_test"])
        self.assertEqual(result["fresh_starts"], 0)

    def test_lost_context_starts_fresh_in_same_workspace(self):
        attempts = [
            self.result(
                exit_code=124,
                stalled=True,
                stdout=(
                    '{"sessionID":"ses_test"}\n'
                    '{"part":{"type":"step-finish","tokens":{"total":123}}}\n'
                ),
            ),
            self.result(
                stdout=(
                    '{"sessionID":"ses_test","type":"text",'
                    '"part":{"text":"CONTEXT_LOST"}}\n'
                )
            ),
            self.result(stdout='{"sessionID":"ses_fresh","type":"step_finish"}\n'),
        ]
        commands = []

        def fake_run(command, *args, **kwargs):
            commands.append(command)
            return attempts.pop(0)

        original = ["opencode", "run", "--format", "json", "task prompt"]
        with (
            mock.patch.object(bench, "run_cmd_with_idle_timeout", fake_run),
            mock.patch.object(bench.time, "sleep"),
        ):
            result = bench.run_opencode_agent(
                original,
                Path("."),
                30,
                {},
                True,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["fresh_starts"], 1)
        self.assertEqual(result["abandoned_tokens"], 123)
        self.assertEqual(commands[2], original)

    def test_second_silence_starts_fresh(self):
        attempts = [
            self.result(
                exit_code=124,
                stalled=True,
                stdout='{"sessionID":"ses_test"}\n',
            ),
            self.result(
                exit_code=124,
                stalled=True,
                stdout='{"sessionID":"ses_test"}\n',
            ),
            self.result(stdout='{"sessionID":"ses_fresh","type":"step_finish"}\n'),
        ]
        commands = []

        def fake_run(command, *args, **kwargs):
            commands.append(command)
            return attempts.pop(0)

        original = ["opencode", "run", "task prompt"]
        with (
            mock.patch.object(bench, "run_cmd_with_idle_timeout", fake_run),
            mock.patch.object(bench.time, "sleep"),
        ):
            result = bench.run_opencode_agent(
                original,
                Path("."),
                30,
                {},
                True,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["fresh_starts"], 1)
        self.assertEqual(commands[2], original)

    def test_retryable_api_error_is_continued(self):
        attempts = [
            self.result(
                exit_code=1,
                stdout=(
                    '{"sessionID":"ses_test","error":{"data":'
                    '{"statusCode":503,"isRetryable":true}}}\n'
                ),
            ),
            self.result(stdout='{"sessionID":"ses_test","type":"step_finish"}\n'),
        ]

        with (
            mock.patch.object(
                bench,
                "run_cmd_with_idle_timeout",
                side_effect=attempts,
            ),
            mock.patch.object(bench.time, "sleep"),
        ):
            result = bench.run_opencode_agent(
                ["opencode", "run", "task prompt"],
                Path("."),
                30,
                {},
                True,
            )

        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["continuations"], 1)

    def test_nonretryable_api_error_is_returned(self):
        attempt = self.result(
            exit_code=1,
            stdout=(
                '{"sessionID":"ses_test","error":{"data":'
                '{"statusCode":401,"isRetryable":false}}}\n'
            ),
        )

        with mock.patch.object(
            bench,
            "run_cmd_with_idle_timeout",
            return_value=attempt,
        ) as run:
            result = bench.run_opencode_agent(
                ["opencode", "run", "task prompt"],
                Path("."),
                30,
                {},
                True,
            )

        self.assertEqual(result["exit_code"], 1)
        self.assertFalse(result["timed_out"])
        run.assert_called_once()


class CommandTimeoutTests(unittest.TestCase):
    def test_timeout_output_accepts_bytes(self):
        process = mock.Mock()
        process.pid = 123
        process.communicate.side_effect = [
            subprocess.TimeoutExpired(
                ["agent"],
                1,
                output=b"partial stdout",
                stderr=b"partial stderr",
            ),
            (" trailing stdout", " trailing stderr"),
        ]

        with (
            mock.patch.object(subprocess, "Popen", return_value=process),
            mock.patch.object(bench.os, "killpg"),
        ):
            result = bench.run_cmd(
                ["agent"],
                Path("."),
                1,
                kill_descendants=True,
            )

        self.assertTrue(result["timed_out"])
        self.assertIn("partial stdout", result["stdout"])
        self.assertIn("trailing stderr", result["stderr"])


class PointScoringTests(unittest.TestCase):
    def test_parses_multi_runtime_points(self):
        score = bench.parse_point_score(
            {
                "stdout": (
                    'detail\nBENCH_POINTS_JSON:{"earned":6,"total":10,'
                    '"checks":[{"name":"one","points":2,"passed":true}]}\n'
                )
            },
            False,
        )
        self.assertEqual(score["earned"], 6)
        self.assertEqual(score["total"], 10)

    def test_legacy_task_uses_all_or_nothing_points(self):
        self.assertEqual(
            bench.parse_point_score({"stdout": ""}, True)["earned"],
            10,
        )
        self.assertEqual(
            bench.parse_point_score({"stdout": ""}, False)["earned"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
