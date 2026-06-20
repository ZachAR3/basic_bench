# Methodology

## Objective

The benchmark measures whether a coding agent can diagnose a defect, produce a
focused patch, and satisfy held-out behavioral tests without reading the
grader.

It is a diagnostic suite, not a general coding leaderboard.

## Tasks

The suite contains:

- six compact tasks with basic visible regression tests;
- four compact tasks with all tests withheld;
- five multi-language tasks with all tests withheld;
- one repository-scale task generated from Click 8.4.0 with all tests withheld.

Compact tasks cover parsing, configuration precedence, caching, rate limiting,
schema migration, Unicode handling, graph ordering, asynchronous retry logic,
timezone recurrence, and endpoint normalization.

Multi-language tasks cover React concurrent rendering and offline state,
Java backend idempotency, Godot GDScript and C# persistence, low-level C++
memory-bus semantics, and Rust WAL recovery.

The Click task requires changes across command dispatch, context state,
decorators, and public exports.

## Test separation

Agent workspaces never contain the held-out test directories or reference
solutions. Tests are run from the benchmark root after the agent exits.

Visible tests are regression checks only. A task can pass its visible tests
before repair and still fail the held-out tests.

The repository contains the graders for reproducibility. They are hidden from
the agent at execution time, but are not confidential after publication.
Results intended to measure contamination resistance should use newly authored,
unreleased tasks.

## Isolation

Automated runs on macOS use `sandbox-exec` to deny access to:

- the benchmark root;
- held-out tests and reference solutions;
- sibling task workspaces;
- selected external caches.

The harness uses a fresh repository and agent state for each task, terminates
descendant processes, and grades a sealed copy of the final workspace.

Supported provider profiles disable web-search and prior-session tools. The
generic command adapter cannot enforce provider-specific tool settings; users
must disable external retrieval in the agent being evaluated.

Desktop runs cannot receive the same process-level sandbox. They should use one
fresh session per task and open only the generated task directory.

## Integrity checks

A scored workspace is rejected if it changes the trusted Git baseline, provided
tests, agent configuration, or test infrastructure. The grader also rejects
symlinks, import hooks, native extension modules, and oversized files.

## Scoring

A task passes only when:

1. regression tests pass;
2. held-out tests pass;
3. integrity checks pass.

Each task is worth ten points. Existing compact and large tasks award all ten
points only on a full pass. Multi-language tasks contain five independent
two-point checks, allowing partial credit while retaining the strict task-pass
metric.

The primary metrics are task pass rate and points earned. Secondary diagnostics include:

- paired pass and failure outcomes;
- timeout and agent exit status;
- files and lines changed;
- visible versus held-out failures;
- wall-clock time for automated runs;
- provider-reported token use and calculated cost.

Reviewed evaluations may include a ten-point "syntax" score for readability,
reuse, focus, and maintainability. This score is explicitly subjective,
reviewer-biased, and separate from held-out functional grading.

Manual runs do not capture reliable wall-clock time or full agent transcripts.

## Run protocol

For a fair comparison:

- use the same task revision;
- use one attempt per task;
- use a fresh session and workspace per task;
- keep tool permissions consistent;
- record the exact model, provider, agent version, date, timeout, and command;
- do not retry after seeing held-out results.

The paired exact sign test is reported for convenience. Sixteen tasks remain a
small diagnostic suite; repeat comparisons with additional private tasks.

## Benchmark validation

`quality-audit` verifies that every compact task:

- starts with passing regression tests;
- fails held-out tests before repair;
- accepts the trusted reference repair;
- rejects a plausible partial repair.

`quality-audit-large` applies the same checks to the Click task and rejects four
different partial repair strategies.

`security-audit` verifies the automated filesystem isolation boundary.
