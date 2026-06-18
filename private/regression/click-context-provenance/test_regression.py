from __future__ import annotations

import unittest

import click
from click.testing import CliRunner


class ExistingBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_ordinary_parameter_sources_still_work(self) -> None:
        @click.command()
        @click.option("--value", default="fallback", envvar="VALUE")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            click.echo(f"{value}:{ctx.get_parameter_source('value').name}")

        result = self.runner.invoke(cli, ["--value", "cli"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "cli:COMMANDLINE\n")

        result = self.runner.invoke(cli, [], env={"VALUE": "env"})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "env:ENVIRONMENT\n")

    def test_invoke_still_fills_defaults_and_calls_callback(self) -> None:
        @click.command()
        @click.option("--count", default=3, type=int)
        def target(count: int):
            click.echo(count)

        @click.command()
        @click.pass_context
        def cli(ctx: click.Context):
            ctx.invoke(target)

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "3\n")

    def test_forward_keeps_extra_parameters_for_kwargs_callbacks(self) -> None:
        @click.command()
        @click.option("--left")
        def target(**kwargs):
            click.echo(",".join(sorted(kwargs)))

        @click.command()
        @click.option("--left")
        @click.option("--right")
        @click.pass_context
        def cli(ctx: click.Context, left: str | None, right: str | None):
            ctx.forward(target)

        result = self.runner.invoke(cli, ["--left", "L", "--right", "R"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "left,right\n")

    def test_aggregate_decorator_is_public_and_receives_mapping(self) -> None:
        @click.command()
        @click.option("--value", default="x")
        @click.pass_parameter_sources
        def cli(sources, value: str):
            click.echo(f"{value}:{sources['value'].name}")

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "x:DEFAULT\n")


if __name__ == "__main__":
    unittest.main()
