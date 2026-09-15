# 1.0.0rc1 TODO

Outstanding work before cutting the first 1.0 release candidate. Ordered by
how hard each item is to change after rc1.

## Before rc1 (breaking to change later)

- [ ] `Problem.__init__`: fix mutable default `test_sets=[]` → `None`.
- [ ] Rename `add_raw_test_NO_VALIDATE` → `add_raw_test` (or keep it).
- [ ] Stabilize or mark experimental `MulticaseTestFile` / `TestCaseBase`.
- [ ] Make `validate_test_in` a concrete no-op default.
- [ ] Decide whether to remove deprecated `Problem.run_cli`.

## Forward-compat gaps

- [ ] Phase 3 jobs as data (`infile`, `ansfile`, `run_cmd`) for the A2 process switch.
- [ ] Custom `write_test_out` + parallelism behavior.
- [ ] `seed` type hint: `str | int | None`.

## Defer (non-breaking)

- [ ] Mark sharding API as experimental.
- [ ] De-globalize `judge_api` / `runner` module state.

## Release

- [ ] Bump `__version__` to `1.0.0rc1`.
