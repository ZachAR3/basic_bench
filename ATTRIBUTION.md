# Attribution

## Click

The repository-scale task is based on
[Pallets Click](https://github.com/pallets/click), release 8.4.0, commit
`41f410fb7528305d7e87c8cfa704f6c2456f57fc`.

Click is included as the `vendor/click` Git submodule and remains under its
BSD-3-Clause license. Copyright belongs to the Pallets project and its
contributors.

## Optional public benchmarks

The optional public benchmark runner integrates:

- [Aider Polyglot Benchmark](https://github.com/Aider-AI/polyglot-benchmark)
- [LiveCodeBench](https://github.com/LiveCodeBench/LiveCodeBench)
- [SWE-bench](https://github.com/SWE-bench/SWE-bench)

These projects are not bundled in the main repository. Their setup script
clones pinned revisions listed in `config/vendor-lock.json`. Each project keeps
its own license and attribution requirements.

## Original material

The compact private tasks, prompts, held-out tests, reference repairs, harness,
and reports in this repository are original project material unless a file
states otherwise.

The multi-language tasks are original material informed by the public API and
tooling documentation for:

- [React](https://react.dev/) and [Vite](https://vite.dev/)
- [Java 21](https://docs.oracle.com/en/java/javase/21/)
- [Godot](https://docs.godotengine.org/) and [.NET](https://learn.microsoft.com/dotnet/)
- [C++](https://isocpp.org/) and [Rust](https://doc.rust-lang.org/)

No third-party application source code is included in those tasks. Their npm
development dependencies retain their own licenses under `node_modules` after
local setup and are not committed.
