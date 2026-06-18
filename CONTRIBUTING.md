# Contributing

Contributions should keep the benchmark reproducible and easy to audit.

For a new task:

1. add a minimal buggy repository under `private/tasks`;
2. add the issue prompt under `private/prompts`;
3. add held-out tests under `private/hidden`;
4. add a trusted reference repair under `private/oracle/reference`;
5. add a plausible partial repair to the quality audit;
6. verify that the baseline fails and the reference passes;
7. document third-party sources and licenses.

Do not commit credentials, generated workspaces, raw results, virtual
environments, or provider state.

Before opening a change:

```bash
make setup
make audit
python3 -m py_compile bench.py public_runner.py scripts/init_large_task.py
```
