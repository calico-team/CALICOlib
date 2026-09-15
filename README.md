# CALICOlib
CALICOlib is a framework to help facilitate problem creation on DOMjudge. Currently, the library helps with test generation and creating problem zip, which is based on the ICPC problem package specification

## Installing
```sh
python -m pip install calico_lib
# or use uv
uv pip install calico_lib
```
Alternatively, install the development version using flit.
```sh
brew install flit # or another package manager like pip or pipx
git clone https://github.com/calico-team/CALICOlib.git
cd CALICOlib

PIP_BREAK_SYSTEM_PACKAGES=1 flit install --symlink
# or use uv
uv pip install -e .
# to install to another project's venv
uv pip install -e . --python /path/to/other-project/.venv
```

## Quick Start
See examples/add and tests/.

```sh
python tests/contest.py
```

## Development
Bump version number in `__init__.py` and run `flit publish` or another build tool. See [documentation for flit](https://flit.pypa.io/en/stable/).

## Roadmap
- [ ] Support test case from file
- [X] Upload problem to testing contest
- [X] Create contest
- [X] Create contest.zip
- [ ] Tests
- [ ] Docs
- [X] Remove legacy
- [ ] Default validation (trailing white space / empty lines... etc)
- [ ] Remove calico specific stuff from the library

## Similar tools
https://github.com/RagnarGrootKoerkamp/BAPCtools

## Changelog

### 0.2.0

- `write_test_in` returns a `str` instead of writing via `p.print_test`
  (removed). Tests become pure functions, which makes generation parallel-safe.
- `Problem(..., solution=..., seed=...)` declares your reference solution and
  seed. The library calls `random.seed` before each test, so generation is
  reproducible without you remembering to seed.
- Answer generation defaults to running `solution`; you no longer need to
  override `write_test_out` for the common case.
- `create_all_tests(n_jobs=...)` (or `-j/--jobs` on the CLI) runs answer
  generation in parallel (threads; each solution runs as a subprocess).
- Some random additional API for forward compatibility.
- `MulticaseTestFile` / `TestCaseBase` are experimental; their contract is not
  settled for 1.0.
- `create_all_tests(shard=(i, n))` is experimental; the driver contract
  (coordinating `clean_test_data()` / `pre_gen_fn`) is not settled.
