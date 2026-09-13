# Suggested Improvements

Fixes and improvements to the gotchas documented in `AGENTS.md`, roughly
ordered by impact-to-risk. None of these are implemented yet.

## High value, low risk

**1. Fix the Python target skew** (`pyproject.toml:21`)

```toml
target-version = "py311"
```

Ruff currently lints as 3.7 while the lib uses `tomllib`, `X | Y`, and the
Dockerfile ships 3.11. This mismatch can let incompatible syntax through.

**2. Stop mutating the package dir when zipping** (`legacy.py:94-103`)

`zip_metadata` writes `calico_lib/domjudge-problem.ini`, zips it, deletes it.
Replace the temp-file round-trip with in-memory content:

```python
zip_file.writestr('domjudge-problem.ini', contents)
```

Removes a write to the source tree, a race if two problems zip concurrently,
and a stale-file risk if the process dies mid-way.

**3. Restore cwd instead of leaking it** (`problem.py:194,216`, `cli.py:96`)

Either wrap the body in `try/finally` restoring the saved cwd, or (better) drop
`chdir` entirely and build paths from `self.problem_dir`. The `try/finally`
version is a one-line-ish change; the path-based version is the real fix but
touches `legacy.py`.

**4. Scope the `F401` ignore** (`pyproject.toml:26`)

Ignoring `F401` globally hides genuinely unused imports. Use `__all__` in
`__init__.py` and move the ignore to per-file:

```toml
[tool.ruff.lint.per-file-ignores]
"calico_lib/__init__.py" = ["F401"]
```

## Medium

**5. Make `add_hidden_test` safe by construction** (`problem.py:167-172`)

Instead of warning when an instance is passed, either:

- accept only `Callable[[], TestFileBase]` and require a factory (deprecate
  instance support), or
- `copy.deepcopy(test_file_or_fn)` per generated test so accidental shared
  state is harmless.

The warning is a code smell that the API invites the wrong usage.

**6. Add a validate bypass** (`problem.py:140`)

`validate_test_in` always runs and is abstract. Add a `validate: bool = True`
param threaded through `_add_test`/`add_hidden_test`, or give
`TestFileBase.validate_test_in` a concrete no-op default so subclasses opt in.
Useful for expensive or redundant validation.

**7. De-hardcode the config paths** (`cli.py:52-53`)

`../secrets.toml` / `../config.toml` assume a fixed layout. Search upward from
cwd until found, or add `--config`/`--secrets` args (the CLI already has `-a`
for auth, so a path flag is consistent). Also means the CLI could run from the
problem dir or a parent.

**8. Fix the `check` glob** (`test/gta6/check:122`)

`data/**/*.in` only works because there happen to be exactly two levels; bash
doesn't interpret `**` without `globstar`. Add `shopt -s globstar` near the top
(or switch to `find`).

**9. Refresh or delete `examples/add/main.py`**

`README.md:17` points users at a file that's broken against the current API
(`Problem[Test]('add')`, no `problem_dir`). Either port it to the `test/gta6`
pattern or point the README at `test/gta6`.

## Bigger refactors

**10. De-globalize judge/runner state** (`judge_api.py:9-11`, `runner.py:11-26`)

`USER`, `CONTEST_ID`, and `CC` as module globals, plus `Runner.__init__`
appending to `_ALL_EXECUTABLES`, make multi-contest or multi-problem-in-one-process
runs fragile. Wrapping these in a `JudgeClient` object passed to `Problem` would
be the clean version; a smaller step is to register runners per-`Problem`
rather than in the global list.

**11. De-duplicate the rank-to-color map** (`problem.py:52`, `contest.py:24`)

Two copies already exist. Export one function (e.g. `rank_color(rank)`) and have
both call it, or move the map to a single constant.
