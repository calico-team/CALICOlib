# CALICOlib 1.0 Refactor Plan

Stabilize the public API for a 1.0 release and make test generation
parallelizable. The headline change is removing shared mutable state, plus
first-class affordances for parallel generation.

## Goal

A clean, deterministic, portable 1.0 API with:

- process-based parallelism for the expensive phase (running reference
  solutions), managed by the library;
- a supported, low-friction path for users who want to parallelize input
  generation themselves (sharding);
- packaging that works from files on disk, so externally-generated tests are
  first-class rather than an escape hatch.

## Decisions

1. **Python floor: 3.11** (matches Dockerfile, gives `tomllib`). No 3.12-only
   features; drop `typing.override` usages.
2. **Return-string contract.** `write_test_in` / `write_test_out` return the
   full text as `str`. `print_test` and `Problem._cur_file` are removed.
3. **Keep public names** `Problem`, `Subproblem`, `TestFileBase`. Naming was
   already explored and rejected (`rewrite1` branch removed `Subproblem` and was
   marked "bad idea"; README's "Subproblem→Problem" rename was also rejected).
4. **Declarative solution.** The reference solution becomes a `Runner` on
   `Problem`; answer generation defaults to "run this command on the input."
5. **Parallelism end-state: processes** for answer generation. Threads first as
   an intermediate step; the design must make the process switch cheap.
6. **User-managed input parallelism via sharding.** The library does not try to
   orchestrate user code across processes. It exposes deterministic, pure,
   shardable generation; the user owns the orchestration (fork, re-exec, queue,
   whatever).
7. **Disk-based packaging.** `create_zip` packages files on disk, not just the
   in-memory registry.
8. **Library-owned seeding.** `Problem` takes an optional `seed`; the library
   seeds deterministically before each test. If omitted, a default derived from
   `problem_name` is used, so tests are reproducible without user action.
9. **No downstream repos constrain the API** (confirmed), so we may break, but
   we prefer incremental change over a rewrite.

## Root cause: two independent obstacles

The current design can't parallelize for two reasons, and they must be treated
separately:

1. **Shared mutable state.** `_add_test` closures write through
   `Problem._cur_file`, and `write_test_in` calls back into `self.print_test()`.
   This races under threads and is nonsensical across processes.
2. **`__main__` / pickle.** Under `spawn`, a worker process cannot import user
   code defined in `main.py` (which runs as `__main__`), so shipping user
   functions or objects to a worker fails.

The return-string contract fixes obstacle #1. It does **not** fix #2. The
`multiprocessing` branch's `ThreadPoolExecutor` attempt failed because it
parallelized the *whole* generator, so threads raced on `_cur_file` (obstacle #1).

## Key insight: don't ship user code to workers

Obstacle #2 only matters if we try to run *user code* in a worker. A `Runner`
is just `run_cmd: list[str]` — **already picklable**. So:

- **Library-managed parallelism** applies only to answer generation, which is
  "run this known command on this file" — no user code in the worker.
- **User-managed parallelism** for input generation is expressed as *sharding*,
  where the user's own orchestration re-runs `main.py` (or otherwise spawns
  workers), and the library just generates a deterministic slice.

## Target architecture: three phases + sharding

```
create_all_tests(n_jobs=None, shard=None):
    jobs = self._all_tests                # stable, deterministic order
    if shard is not None:
        i, n = shard
        jobs = [j for k, j in enumerate(jobs) if k % n == i]

    # Phase 1 — generate every .in (user code + random)
    for job in jobs:
        seed(job)                          # per-test deterministic seed
        write(job.path + '.in', job.write_test_in())

    # Phase 2 — validate every .in
    for job in jobs:
        job.validate_test_in(job.path + '.in')

    # Phase 3 — run reference solution -> .ans (pure command exec, parallel)
    with executor(n_jobs):
        for job in jobs:
            run_solution(job.path + '.in', job.path + '.ans', problem.solution.run_cmd)
```

Notes:

- **Phase 1 stays serial** by default: it is fast and it is what consumes
  `random`. Sharding (above) is the user's opt-in way to parallelize it.
- **Phase 3 is the parallel unit.** Its payload is `(infile, ansfile, run_cmd)`
  — plain picklable data — and the worker function lives in `calico_lib/`
  (importable), so a `ProcessPoolExecutor` with `spawn` works without shipping
  user code.
- **Per-test seeding** makes each test independent of its siblings and of
  ordering, which is what makes sharding correct and reproducible.

## Library-owned seeding (determinism by default)

Today the user seeds manually via `@p.pre_gen_fn def pre_gen(): random.seed('6')`.
If they forget, Python's `random` falls back to OS entropy and tests change on
every run.

In 1.0 the library owns seeding:

```python
p = Problem('gta6', problem_dir, solution=..., seed='6')  # optional
```

`create_all_tests` seeds before each test's Phase 1:

```python
random.seed(f"{problem.seed}:{job.index}:{job.name}")
```

- `seed` provided -> the user controls the sequence.
- `seed` omitted -> the library uses a deterministic default derived from
  `problem_name`, so tests are reproducible with no user action. Determinism
  becomes opt-out instead of opt-in.

Per-test seeding is also what makes sharding correct: test *k* generates
identically regardless of which worker (or whether it ran serially), because it
does not depend on a single sequential RNG stream.

Caveats:

- **Only captures global `random`.** `random.seed(...)` does not reach a fresh
  `random.Random()` instance, `numpy.random`, or `secrets`. Document "use the
  global `random` module for reproducible tests"; an explicit `seed` arg to the
  factory would close the gap but is a larger API change.
- **`pre_gen_fn` remains** for non-seeding setup (precompute data, read files),
  but its seeding role is absorbed. With sharding it re-runs in every worker,
  so it must be deterministic/idempotent.
- **String vs int seed.** `random.seed('6')` and `random.seed(6)` differ, and
  string seeds are not guaranteed stable across Python versions (the string-to-int
  path changed in 3.9). Recommend int seeds for cross-version reproducibility.
- **Index in the seed.** Inserting a test shifts the seed of later tests (fine:
  code changed -> regenerate). Seeding on `name` instead avoids this but requires
  unique names per test (repeated generators via `hidden_test_generator` collide).

The exact seed-derivation format is an open question; the requirements
(library-owned, defaulted, per-test, reproducible) are not.

## User-managed input parallelism (sharding)

The library exposes `create_all_tests(shard=(i, n))` with strided partitioning:
worker `i` generates tests whose index `% n == i`. A user driver launches N
subprocesses:

```python
for i in range(4):
    subprocess.Popen([sys.executable, 'main.py'],
                     env={**os.environ, 'SHARD': str(i), 'NSHARDS': '4'})
```

and `main.py` reads the env vars and calls `create_all_tests(shard=(shard, nshards))`.

This is portable (re-exec, no pickle) and requires the user's `main.py` to have
the usual `if __name__ == '__main__':` guard. The library stays pickle-agnostic:
it just answers "generate tests matching `index % n == i`."

Shard workers skip the data/zips wipe (otherwise sibling shards would clobber
each other), so the driver must clean once before spawning them. The library
exposes `Problem.clean_test_data()` for this: it removes `data/sample`,
`data/secret`, and any `*.zip` in the problem dir whose name ends with
`_<test_set_name>`. A driver calls it once, then launches the workers.

## Disk-based packaging

`create_zip` should package whatever `.in`/`.ans` pairs exist on disk under
`data/sample/` and `data/secret/`, rather than relying solely on the in-memory
`test_paths` registry. This makes externally-generated tests (including sharded
output) first-class.

Subproblem mapping: the trailing filename segment before the extension is the
subproblem (`00_pure_random_main.in` -> `main`), matching the current naming
convention. This constrains subproblem names to not contain `_` (already
implicit in the current code). Flagged as an open question.

## Target API

```python
# calico_lib exports (unchanged names)
from calico_lib import (
    Problem, TestFileBase, Subproblem, Runner,
    py_runner, cpp_runner, Contest, MulticaseTestFile, TestCaseBase, run_cli,
)

class TestFileBase(ABC):
    subproblems: Collection[str]

    @abstractmethod
    def write_test_in(self) -> str:
        """Return the input text for this test file."""

    @abstractmethod
    def validate_test_in(self, infile: str) -> None:
        """Validate the generated input (asserts or run a validator subprocess)."""

    def write_test_out(self, infile: str) -> str:
        """Optional override. Default: run Problem.solution on infile."""
        return self.problem.run_solution(infile)

class Problem:
    def __init__(self, problem_name: str, problem_dir: str,
                 test_sets: list[Subproblem] | None = None,
                 solution: Runner | None = None,
                 seed: str | None = None): ...

    def add_sample_test(self, test, name='', subproblems=None): ...
    def add_hidden_test(self, test_or_fn, name='', subproblems=None): ...
    def create_all_tests(self, n_jobs: int | None = None,
                         shard: tuple[int, int] | None = None): ...  # None => cpu_count; 1 => serial
    def clean_test_data(self): ...  # remove data/sample, data/secret, and problem zips
    def create_zip(self, name_prefix='draft_'): ...  # packages from disk
    def upload(self): ...
    def link_to_contest(self): ...
```

Changes vs today:

- `Problem.__init__` gains `solution: Runner | None` and `seed: str | None`.
- `write_test_in` / `write_test_out` return `str` instead of writing via
  `print_test`.
- `add_hidden_test` keeps accepting either an instance (hard-coded test) or a
  factory/lambda (generated test); the warning is clarified, not removed.
  `hidden_test_generator` stays as syntactic sugar.
- `create_all_tests` gains `n_jobs` and `shard`.
- `clean_test_data` removes generated data and problem zips; call it once before
  launching sharded workers.
- `create_zip` packages from disk.
- `Problem._cur_file`, `print_test`, and the deprecated `Problem.run_cli` are
  removed.

## Forward-compat choices (bake in now)

1. **Executor seam** inside `create_all_tests` so Phase 3 can switch from threads
   to processes without touching call sites.
2. **Declarative `Problem.solution`** — keeps Phase 3 "run command on file"
   rather than user code, so the process switch stays trivial.
3. **Jobs as data** (`path`, `run_cmd`), never closures over user objects.
4. **Shard + per-test seeding** — first-class, so input-gen parallelism is a
   user choice, not a library rewrite later.
5. **Disk-based `create_zip`** — generation and packaging are decoupled.

## Implementation phases

### Track B — stabilization (do first, serial)

**DONE: Step B1 — return-string contract + phase split.**
- Change `TestFileBase` methods to return `str`.
- Split `_add_test` / `create_all_tests` into the three phases.
- Remove `_cur_file` and `print_test`.
- Add `Problem.solution` and default answer generation; compile the solution
  before Phase 3 (handles `cpp_runner`).
- Keep `n_jobs` accepted but force serial for now.
- Port `test/gta6/main.py` (the live reference; `examples/add` is stale).
- Verify byte-identical `.in`/`.ans` output.

**DONE: Step B2 — clarify instance vs factory (no API removal).**
- Keep `add_hidden_test` (instance or factory/lambda) and `hidden_test_generator`
  as-is.
- Improve the warning to explain that an instance is built eagerly (before
  `pre_gen_fn` seeds the RNG), so hard-coded tests are fine but generated tests
  should pass a factory/lambda.
- Document instance-vs-factory in README/AGENTS. Lambdas work in-process; prefer
  top-level functions for future sharded input generation.

**DONE: Step B3 — shard + per-test seeding.**
- Add `seed` to `Problem`, derive per-test seeds, seed before Phase 1.
- Add `shard=(i, n)` to `create_all_tests` (strided filter).
- Document the `if __name__ == '__main__'` re-exec pattern for users.

**Step B4 — disk-based packaging + cleanup.**
- `create_zip` discovers `.in`/`.ans` from `data/sample` and `data/secret`.
- Remove `os.chdir` from `create_all_tests` / `create_zip` / `cli.run_cli`; use
  `problem_dir`-based absolute paths.
- `zip_metadata`: write content in-memory via `zip_file.writestr` (no temp file
  in `calico_lib/`).
- De-globalize `judge_api.USER`/`CONTEST_ID` and `runner.CC`/`_ALL_EXECUTABLES`.
- De-duplicate the rank→color map (`problem.py:52`, `contest.py:24`).
- `ruff` target-version → `py311`; scope the `F401` ignore to `__init__.py`.

### Track A — parallelism (after B, small)

**Step A1 — threads for Phase 3.**
- `ThreadPoolExecutor(n_jobs)` around the solution-run phase; GIL is released
  during `subprocess.check_output`.

**Step A2 — processes for Phase 3.**
- Swap the executor to `ProcessPoolExecutor` (spawn-safe) since the job payload
  `(infile, ansfile, run_cmd)` is picklable and the worker function is importable.

## DOCS
- Rewrite AGENTS.md. Lots of stuff should go as docs.

## Testing
- Refresh or delete `examples/add/main.py`; update README pointer.
- Test on judge platform with new library. Rejudge submissions.
- Try implementing a problem.

## Open questions

- `MulticaseTestFile` / `TestCaseBase`: confirm they adopt the return-string
  contract (`TestCaseBase.write_test_in` returns one case's lines;
  `verify_case` naming may be reconsidered).
- Per-test-set solutions? `Problem.solution` is per-Problem for now; custom
  `write_test_out` is the escape hatch.
- Sample tests: keep them serial/in-process (they are few and hand-written).
- `validate_test_in` currently cannot be skipped and is abstract; consider a
  concrete no-op default (see suggestion #6) or a `validate=False` param.
- Per-test seeding mechanism: global-`random`-only vs. explicit `seed` arg to
  the factory (or both).
- Disk-based packaging subproblem parsing: trailing `_segment` convention, and
  whether subproblem names may contain `_`.

## What we lose at Python 3.11 (vs 3.12)

- `typing.override` — cosmetic; drop the import in stale examples.
- `PEP 695` `class Foo[T]` syntax.
- `Path.walk` — use `os.walk`.

None are required by this refactor.
