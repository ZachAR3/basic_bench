Click 8.4 added aggregate parameter-source access for integrations, but the
implementation is not safe or correct once commands dispatch to other commands.
This is causing audit and policy plugins to misclassify values in production.

Fix parameter provenance across `Context.invoke` and `Context.forward` while
preserving their existing callback and parameter behavior:

- Explicit keyword arguments passed directly to `invoke` or explicitly
  overriding a value in `forward` are `ParameterSource.COMMANDLINE`.
- Values copied by `forward` retain their exact source from the current
  context, including command line, prompt, environment, default map, or
  parameter default.
- Parameters filled by the invoked command use `DEFAULT_MAP` when its child
  default map contains that key, including falsy values, `None`, and callable
  defaults. Otherwise they use `DEFAULT`.
- Provenance survives multiple forwarding levels and remains isolated between
  parent and child contexts.
- `Context.parameter_sources` and `@click.pass_parameter_sources` expose an
  immutable snapshot. A callback must not be able to mutate Click's internal
  tracking through it, and later context changes must not alter a snapshot
  already handed out.
- Keep `click.pass_parameter_sources` available from the top-level package.
- Do not regress extra-parameter forwarding, callable defaults, `UNSET`
  handling, callback decorators, or ordinary command-line parsing.

No reproduction or test suite is provided. Diagnose the dispatch, context,
decorator, and public-export paths in the repository. Keep the change focused
and do not add dependencies or modify packaging metadata.
