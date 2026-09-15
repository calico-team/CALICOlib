# 1.0.0rc1 TODO

Things to settle before cutting the first 1.0 release candidate, ordered by
how painful they are to change once users depend on them.

## Lock down before rc1

These become breaking changes after rc1.

- **`add_raw_test_NO_VALIDATE` naming.** The plan calls this `add_raw_test`, but
  the method still carries the `_NO_VALIDATE` suffix. Renaming after rc1 breaks
  anyone already using it, so decide now.

- **`MulticaseTestFile` / `TestCaseBase` contract.** Still an open question
  (`write_test_in` line format, `verify_case` naming). They are exported, so
  either stabilize them or clearly mark them experimental.

- **`validate_test_in` semantics.** It is abstract and its body now raises
  `assert False, "Must validate test"`, so validation is mandatory. Decide
  whether that stays (users must implement it) or becomes a concrete no-op
  default for convenience.

- **`Problem.run_cli` shim.** The plan says remove it; `run_cli(p)` is the
  supported entry point. Either delete the deprecated method or keep it and
  document it as deprecated for the whole 1.x line.

## Forward-compat gaps

Signals that the current design will make later work harder.

- **Phase 3 executor seam.** Answer jobs are passed as `(test, file_path)`,
  which ships a user `TestFile` object to the worker. Fine for threads, but not
  picklable for the planned `ProcessPoolExecutor` (Step A2). Move the payload
  to plain data (`infile`, `ansfile`, `run_cmd`) now.

- **Custom `write_test_out` vs. parallelism.** The default answer path
  parallelizes well, but an overridden `write_test_out` runs user code (no
  subprocess, GIL held). Decide whether custom overrides force serial
  generation or are bypassed in the parallel path.

- **`seed` type hint.** Typed as `str | None`, but int seeds work and are
  recommended for cross-version reproducibility. Widen it to `str | int | None`.

## Defer

Non-breaking; can ship after rc1.

- **Sharding API.** `create_all_tests(shard=...)` requires the caller to
  coordinate `clean_test_data()` and `pre_gen_fn()`. It works, but the contract
  is awkward; mark it experimental until it settles.

- **De-globalize module state.** `judge_api.USER`/`CONTEST_ID` and
  `runner.CC`/`_ALL_EXECUTABLES` are process globals. Removing them is a larger
  refactor that does not block rc1.

## Release

- **Bump `__version__`** from `0.1.22` to `1.0.0rc1` before tagging.
