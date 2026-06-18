from __future__ import annotations

import unittest

import click
from click.core import ParameterSource
from click.testing import CliRunner


class ProvenanceDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @staticmethod
    def source_command(name: str = "value", **option_kwargs):
        @click.command()
        @click.option(f"--{name}", **option_kwargs)
        @click.pass_context
        def target(ctx: click.Context, **kwargs):
            value = kwargs[name]
            source = ctx.get_parameter_source(name)
            click.echo(f"{value!r}:{source.name if source else 'NONE'}")

        return target

    def test_invoke_child_default_map_tracks_falsy_and_none(self) -> None:
        for mapped, rendered in (
            (0, "'0'"),
            (False, "'False'"),
            ("", "''"),
            (None, "None"),
        ):
            target = self.source_command(default="parameter")

            @click.command()
            @click.pass_context
            def cli(ctx: click.Context):
                ctx.invoke(target)

            result = self.runner.invoke(
                cli,
                [],
                default_map={target.name: {"value": mapped}},
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(result.output, f"{rendered}:DEFAULT_MAP\n")

    def test_invoke_callable_default_map_called_once(self) -> None:
        calls = []
        target = self.source_command(default="parameter")

        @click.command()
        @click.pass_context
        def cli(ctx: click.Context):
            ctx.invoke(target)

        def factory():
            calls.append("called")
            return "lazy"

        result = self.runner.invoke(
            cli,
            [],
            default_map={target.name: {"value": factory}},
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "'lazy':DEFAULT_MAP\n")
        self.assertEqual(calls, ["called"])

    def test_invoke_explicit_override_is_commandline(self) -> None:
        target = self.source_command(default="parameter")

        @click.command()
        @click.pass_context
        def cli(ctx: click.Context):
            ctx.invoke(target, value="override")

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "'override':COMMANDLINE\n")

    def test_forward_preserves_each_parsed_source(self) -> None:
        cases = [
            (["--value", "cli"], {}, None, "'cli':COMMANDLINE\n"),
            ([], {"VALUE": "env"}, None, "'env':ENVIRONMENT\n"),
            ([], {}, {"value": "mapped"}, "'mapped':DEFAULT_MAP\n"),
            ([], {}, None, "'parameter':DEFAULT\n"),
        ]

        for args, env, default_map, expected in cases:
            target = self.source_command(default="target")

            @click.command()
            @click.option(
                "--value",
                default="parameter",
                envvar="VALUE",
            )
            @click.pass_context
            def cli(ctx: click.Context, value: str):
                ctx.forward(target)

            result = self.runner.invoke(
                cli,
                args,
                env=env,
                default_map=default_map,
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(result.output, expected)

    def test_forward_prompt_source_survives(self) -> None:
        target = self.source_command(default="target")

        @click.command()
        @click.option("--value", prompt=True)
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            ctx.forward(target)

        result = self.runner.invoke(cli, input="prompted\n")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(result.output.endswith("'prompted':PROMPT\n"))

    def test_forward_explicit_override_is_commandline(self) -> None:
        target = self.source_command(default="target")

        @click.command()
        @click.option("--value", envvar="VALUE")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            ctx.forward(target, value="override")

        result = self.runner.invoke(cli, env={"VALUE": "environment"})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "'override':COMMANDLINE\n")

    def test_target_only_default_map_gets_its_own_source(self) -> None:
        @click.command()
        @click.option("--shared", default="target-shared")
        @click.option("--target-only", default="target-default")
        @click.pass_context
        def target(ctx: click.Context, shared: str, target_only: str):
            click.echo(ctx.get_parameter_source("shared").name)
            click.echo(ctx.get_parameter_source("target_only").name)

        @click.command()
        @click.option("--shared", default="parent")
        @click.pass_context
        def cli(ctx: click.Context, shared: str):
            ctx.forward(target)

        result = self.runner.invoke(
            cli,
            default_map={"target": {"target_only": "mapped"}},
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "DEFAULT\nDEFAULT_MAP\n")

    def test_multi_hop_forward_retains_environment_source(self) -> None:
        @click.command()
        @click.option("--value")
        @click.pass_context
        def final(ctx: click.Context, value: str):
            click.echo(ctx.get_parameter_source("value").name)

        @click.command()
        @click.option("--value")
        @click.pass_context
        def middle(ctx: click.Context, value: str):
            ctx.forward(final)

        @click.command()
        @click.option("--value", envvar="VALUE")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            ctx.forward(middle)

        result = self.runner.invoke(cli, env={"VALUE": "from-env"})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "ENVIRONMENT\n")

    def test_parent_and_child_source_maps_are_isolated(self) -> None:
        observed = {}

        @click.command()
        @click.option("--value", default="child")
        @click.pass_context
        def target(ctx: click.Context, value: str):
            ctx.set_parameter_source("value", ParameterSource.PROMPT)

        @click.command()
        @click.option("--value", default="parent")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            ctx.forward(target)
            observed["parent"] = ctx.get_parameter_source("value")

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(observed["parent"], ParameterSource.DEFAULT)


class AggregateSourceSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_context_property_is_immutable(self) -> None:
        errors = []

        @click.command()
        @click.option("--value", default="x")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            try:
                ctx.parameter_sources["value"] = ParameterSource.PROMPT
            except TypeError:
                errors.append("immutable")

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(errors, ["immutable"])

    def test_property_returns_a_stable_snapshot(self) -> None:
        observed = {}

        @click.command()
        @click.option("--value", default="x")
        @click.pass_context
        def cli(ctx: click.Context, value: str):
            snapshot = ctx.parameter_sources
            ctx.set_parameter_source("value", ParameterSource.PROMPT)
            observed["snapshot"] = snapshot["value"]
            observed["current"] = ctx.get_parameter_source("value")

        result = self.runner.invoke(cli)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(observed["snapshot"], ParameterSource.DEFAULT)
        self.assertEqual(observed["current"], ParameterSource.PROMPT)

    def test_decorator_passes_immutable_stable_snapshot(self) -> None:
        observed = {}

        @click.command()
        @click.option("--value", envvar="VALUE")
        @click.pass_parameter_sources
        @click.pass_context
        def cli(ctx: click.Context, sources, value: str):
            observed["source"] = sources["value"]
            try:
                sources["value"] = ParameterSource.DEFAULT
            except TypeError:
                observed["immutable"] = True
            ctx.set_parameter_source("value", ParameterSource.PROMPT)
            observed["stable"] = sources["value"]

        result = self.runner.invoke(cli, env={"VALUE": "env"})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(observed["source"], ParameterSource.ENVIRONMENT)
        self.assertTrue(observed["immutable"])
        self.assertEqual(observed["stable"], ParameterSource.ENVIRONMENT)


if __name__ == "__main__":
    unittest.main()
