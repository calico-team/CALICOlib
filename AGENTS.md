# AGENTS.md

Guidance for agents working in CALICOlib. See `docs/refactor_plan.md` for design
background.

Add docstrings and useful comments where appropriate. Docstrings are good, but
ideally users should be able to go just by the example: sparse comments, or
intuitive API design. Our users are bad at reading. The example is the main
documentation; 90% of users only read it and will not read a comment with more
than a few sentences.

## What this is

CALICOlib is a Python framework that helps create competitive-programming
problems for DOMjudge. It generates test cases (`.in`/`.ans` pairs), validates
them, packages each test set into a DOMjudge problem zip (ICPC problem package
format), and can upload/link problems to a judge via its REST API.

The package itself is `calico_lib/`. The `tests/` and `examples/` directories
are consumers of the library, not a test suite for the library.

## Commands

There is no automated test suite, no pytest, and no CI. We should implement
these soon.

```bash
# Lint and format (ruff, configured in pyproject.toml)
ruff check .
ruff format .

# Run the reference integration problem (generates tests + zips, then prompts via CLI)
python tests/gta6/main.py
```

The Docker image (`Dockerfile`) installs the lib with flit and runs
`python gta6/main.py` from `/workspace/tests`.

## Package layout

- `calico_lib/__init__.py` - re-exports the public API and holds `__version__`
  (single source of truth; flit reads it dynamically).
- `problem.py` - `Problem`, `TestFileBase`, `Subproblem`. Core test generation
  (return-string contract, three-phase `create_all_tests`, declarative
  `solution`, per-test seeding).
- `multicase.py` - `MulticaseTestFile`/`TestCaseBase`: a test file made of N
  repeated cases (writes the case count first). Experimental; see the module
  docstring for the open contract questions.
- `runner.py` - `Runner`, `py_runner`, `cpp_runner`, `compile_all`,
  `configure_cpp_cc`. Runs/compiles contestant-style solutions and validators.
- `judge_api.py` - raw DOMjudge REST calls against
  `https://calicojudge.com/api/v4`.
- `cli.py` - `run_cli` argparse entrypoint for `Problem` and `Contest`.
- `contest.py` - `Contest` dataclass and linking helpers.
- `config.py` - loads `config.toml`/`secrets.toml`.

## Architecture and data flow

A `Problem` owns:
- `test_sets: list[Subproblem]` (name, rank, time/mem limits),
- `test_paths: {subproblem_name: [file_path]}` - the in-memory registry that
  `create_zip` packages from,
- `solution: Runner | None` - the declarative reference solution,
- `seed: str | int` - defaults to `problem_name`; drives per-test seeding,
- `_all_tests` - deferred `(test_or_factory, file_path, subproblems)` jobs.

Adding a test only queues a job in `_all_tests`; nothing is written until
`create_all_tests`, which materializes factories, then per test generates the
input, validates it, and generates the answer via `solution`. Files land in
`data/sample/` / `data/secret/` as `{NN}{_name}_{subproblem}.in/.ans`
(`add_raw_test_NO_VALIDATE` registers an existing path instead).

`create_zip()` packages each test set from `test_paths` into
`{draft_}{problem_name}_{test_set}.zip`; `upload()`/`link_to_contest()` follow.
The CLI defaults to the `_draft` prefix unless `-f/--final` is given.

`run_cli(problem_or_contest)` (imported from `calico_lib`) is the interactive
entry point; it works for both `Problem` and `Contest`.

## Non-obvious gotchas

- **Judge state is global.** `judge_api.USER`, `judge_api.CONTEST_ID`, and
  `runner.CC` are module globals set by `set_user`/`set_contest_id`/
  `configure_cpp_cc`. `Runner.__init__` appends every instance to the module
  global `_ALL_EXECUTABLES`, so `compile_all()` compiles all runners ever
  created in the process.
- **Python version.** The library targets Python 3.12 (see `pyproject.toml`
  and the Dockerfile), which gives `tomllib`, `|` unions, `typing.override`,
  and `NamedTuple` generics. Keep new library code compatible with 3.12.

## Problem directory conventions

A problem (e.g. `tests/gta6/`) contains:
- `main.py` - defines the `Problem`, test sets, runners, and test additions.
- `submissions/{accepted,wrong_answer,time_limit_exceeded,run_time_error}/`
- `templates/` - starter files for contestants.
- `scripts/` - validators (run via `py_runner`, called from `validate_test_in`).
- `data/sample/`, `data/secret/` - generated, gitignored.
- `check` - bash helper to run a submission against generated tests:
  `./check submissions/accepted/gta6.py` runs all `data/**/*.in` and diffs
  against `.ans`. Override interpreter with `PY_CMD`, `JAVA_CMD`, `CPP_CC` env
  vars. Note it globs `data/**/*.in`, which does not enable `globstar` by
  default in bash.

## Conventions

- Test sets are `Subproblem(name, rank, time_limit, mem_limit)`. `rank` maps to
  a DOMjudge color via `RANK_COLOR_MAP` (1..4 only) in `problem.py`.
- Adding a test defaults to all test sets when `subproblems` is omitted.
- Commits use conventional prefixes (`feat:`, `fix:`, `chore:`, `test:`).
  Version bumps are their own `chore: bump version to X.Y.Z` commits (handled
  by `new_release.sh`).
