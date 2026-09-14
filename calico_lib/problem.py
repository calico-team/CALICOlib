from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
import hashlib
import os
import random
import shutil
from typing import Dict, NamedTuple
# from warnings import deprecated
import zipfile

from .judge_api import add_problem_metadata_to_contest, get_problem, link_problem_to_contest, set_contest_id, set_user, unlink_problem_from_contest, upload_problem_zip
import argparse
from .runner import Runner
import traceback
import subprocess

class TestFileBase(ABC):
    # TODO: consider storing filename in this class

    subproblems: Collection[str]
    problem: 'Problem | None'

    def __init__(self) -> None:
        # The list of subproblems this test should belong to
        self.subproblems = []
        # Set by Problem during test generation
        self.problem = None

    @abstractmethod
    def write_test_in(self) -> str:
        """Return the input file text for this test."""
        pass

    def write_test_out(self, infile: str) -> str:
        """Return the answer file text. Default: run the problem's solution on infile."""
        assert self.problem is not None, "Test must be registered with a Problem"
        return self.problem.run_solution(infile)

    @abstractmethod
    def validate_test_in(self, infile: str) -> None:
        """Validate the generated input, written at ``infile``.

        This always runs during Phase 2 of ``create_all_tests`` and cannot be
        skipped; if validation is expensive, comment out the body instead.
        """
        pass

# A test consist of either a single case or multiple test cases

_DEFAULT_MEMLIMIT = 256_000_000

# DOMjudge problem color per subproblem rank (1..4).
RANK_COLOR_MAP = {
        1: '#e9e4d7',
        2: '#ff7e34',
        3: '#995d59',
        4: '#000000',
        }


class Subproblem(NamedTuple):
    name: str
    rank: int
    time_limit: int = 1
    mem_limit: int = _DEFAULT_MEMLIMIT
    def color(self):
        return RANK_COLOR_MAP[self.rank]

class Problem:
    test_sets: list[Subproblem]
    problem_dir: str
    custom_checker: None|str

    _cli_func: Callable|None = None

    def __init__(self, problem_name: str, problem_dir: str, test_sets: list[Subproblem] = [], solution: Runner | None = None, seed: str | None = None):
        """Create a problem rooted at ``problem_dir``.

        ``problem_dir`` is stored as an absolute path and all generated and
        packaged paths are resolved against it; the library never calls
        ``os.chdir``. ``seed`` (default ``problem_name``) drives per-test
        seeding in ``create_all_tests``.
        """
        self.problem_name = problem_name
        self.test_sets = test_sets
        self.problem_dir = os.path.abspath(problem_dir)
        self.custom_checker = None
        self.solution = solution
        self.seed = seed if seed is not None else problem_name

        # order of the problem in the contest. Used for label. Otherwise, label is problem_name
        self.label_prefix: int|str = -1

        self.sample_count = 0
        self.hidden_count = 0

        self.always_skip_test_gen = False
        self.pre_fn = None

        # mapping from test sets to tests included in that test set
        self.test_paths: Dict[str, list[str]] = dict()
        for subproblem in test_sets:
            self.test_paths[subproblem.name] = []

        self._sample_path = os.path.join(self.problem_dir, 'data', 'sample')
        self._secret_path = os.path.join(self.problem_dir, 'data', 'secret')
        self._all_tests: list[tuple[TestFileBase | Callable[[], TestFileBase], str, list[str]]] = []


    def init_problem(self):
        """
        Create subdirectories for this problem
        """
        os.makedirs(os.path.join(self.problem_dir, 'submissions', 'accepted'), exist_ok=True)
        os.makedirs(os.path.join(self.problem_dir, 'submissions', 'run_time_error'), exist_ok=True)
        os.makedirs(os.path.join(self.problem_dir, 'submissions', 'time_limit_exceeded'), exist_ok=True)
        os.makedirs(os.path.join(self.problem_dir, 'submissions', 'wrong_answer'), exist_ok=True)
        os.makedirs(os.path.join(self.problem_dir, 'templates'), exist_ok=True)
        os.makedirs(os.path.join(self.problem_dir, 'scripts'), exist_ok=True)

    def add_test_set(self, problem_name: str, rank: int, time_limit = 1, mem_limit: int = _DEFAULT_MEMLIMIT):
        self.test_sets.append(Subproblem(problem_name, rank, time_limit, mem_limit))

    def run_solution(self, infile: str) -> str:
        """Run the reference solution on infile and return its stdout."""
        # TODO: confirm newline behavior on the judge platform (solution output trailing newline).
        assert self.solution is not None, "No solution configured for this problem"
        return self.solution.exec_file(infile)

    def _test_seed(self, index: int, file_path: str) -> int:
        """Return a stable per-test integer seed derived from the problem seed.

        This seeds only the global ``random`` module; fresh ``random.Random()``
        instances and ``numpy.random`` are not affected.
        """
        key = f"{self.seed}:{index}:{os.path.basename(file_path)}".encode()
        return int.from_bytes(hashlib.sha256(key).digest()[:8], 'big')

    def _add_test(self,
                  test_file_or_fn: TestFileBase|Callable[[], TestFileBase],
                  file_dir: str,
                  file_prefix: str,
                  subproblems: list[str]|None = None):
        if subproblems is None:
            subproblems = [s.name for s in self.test_sets]
        file_path = os.path.join(file_dir, file_prefix + '_' + subproblems[0])
        self._all_tests.append((test_file_or_fn, file_path, subproblems))
        for subproblem in subproblems:
            self.test_paths[subproblem].append(file_path)

    def add_raw_test_NO_VALIDATE(self, path, subproblems: list[str]|None = None):
        if subproblems is None:
            subproblems = [s.name for s in self.test_sets]
        for subproblem in subproblems:
            self.test_paths[subproblem].append(path)

    def add_sample_test(self, test: TestFileBase, name: str='', subproblems: list[str]|None = None):
        if name != '': name = '_' + name
        self._add_test(test, self._sample_path, f'{self.sample_count:02d}{name}', subproblems)
        self.sample_count += 1

    def add_hidden_test(self, test_or_fn: TestFileBase|Callable[[], TestFileBase], name: str='', subproblems: list[str]|None = None):
        """Register a hidden (secret) test.

        ``test_or_fn`` may be a ``TestFileBase`` instance (hard-coded test) or a
        zero-arg callable returning one (generated test). Prefer a callable for
        generated tests: an instance is built eagerly, before ``pre_gen_fn``
        runs and before ``random`` is seeded, so its content is frozen too early.
        """

        # TODO: mention docs above in example
        if isinstance(test_or_fn, TestFileBase):
            print(
                f'[Warning] add_hidden_test got a TestFile instance for "{self.problem_name}". '
                'Instances are built eagerly, before pre_gen_fn seeds random, so they are '
                'fine for hard-coded tests but not for generated ones. Pass a factory/lambda '
                'for generated tests.'
            )
        if name != '': name = '_' + name
        self._add_test(test_or_fn, self._secret_path, f'{self.hidden_count:02d}{name}', subproblems)
        self.hidden_count += 1

    def hidden_test_generator(self, test_count = 1, subproblems: list[str]|None = None):
        """A function decorator that adds a hidden test generator. Repeats to generate
        test_count number of test files.
        """
        def generator(gen_fn: Callable[[], TestFileBase]):
            for _ in range(test_count):
                self.add_hidden_test(gen_fn, gen_fn.__name__, subproblems)
            return gen_fn
        return generator

    def pre_gen_fn(self, fn: Callable[[], None]):
        self.pre_fn = fn
        return fn

    def test_validator(self, validator: Callable[[Collection[TestFileBase]], None]):
        self._test_validator = validator
        return validator

    def clean_test_data(self) -> None:
        """Remove generated test data and this problem's zips.

        Deletes ``data/sample`` and ``data/secret`` (recreated by
        ``create_all_tests``) and any ``*.zip`` in ``problem_dir`` whose name
        ends with ``_<test_set_name>``. Call this once before launching sharded
        workers: ``create_all_tests(shard=...)`` skips the wipe so sibling
        shards don't clobber each other.
        """
        for path in (self._sample_path, self._secret_path):
            shutil.rmtree(path, ignore_errors=True)

        for name in os.listdir(self.problem_dir):
            if not name.endswith('.zip'):
                continue
            stem = name[:-len('.zip')]
            if any(stem.endswith('_' + test_set.name) for test_set in self.test_sets):
                os.remove(os.path.join(self.problem_dir, name))

    def create_all_tests(self, n_jobs: int | None = None, shard: tuple[int, int] | None = None):
        """Delete existing tests and regenerate them from all added tests.

        Runs three phases per test: generate the input, validate it, then
        generate the answer. ``random`` is seeded per test from ``_test_seed``
        before Phase 1, so each test is independent of its siblings and of
        ordering.

        ``shard=(i, n)`` limits generation to tests whose index ``% n == i``.
        Shard workers re-run ``main.py`` with env vars and must keep the usual
        ``if __name__ == '__main__':`` guard; they skip the data/zips wipe, so
        the driver must call ``clean_test_data()`` once before spawning them.
        """
        # TODO(n_jobs): parallelize Phase 3 (solution runs) across n_jobs workers.
        if shard is None:
            self.clean_test_data()
        os.makedirs(self._sample_path, exist_ok=True)
        os.makedirs(self._secret_path, exist_ok=True)

        if self.pre_fn is not None:
            print('\nRunning pre generation tasks...')
            self.pre_fn()

        # Materialize test instances (factories must run after pre_fn/seed).
        jobs = list(enumerate(self._all_tests))
        if shard is not None:
            i, n = shard
            jobs = [(index, job) for index, job in jobs if index % n == i]

        tests = []
        for index, (test_or_fn, file_path, subproblems) in jobs:
            random.seed(self._test_seed(index, file_path))
            test = test_or_fn() if callable(test_or_fn) else test_or_fn
            test.subproblems = subproblems
            test.problem = self
            tests.append((test, file_path))

        # Phase 1: generate inputs.
        for test, file_path in tests:
            print(f"Writing infile {file_path + '.in'}")
            with open(file_path + '.in', 'w', encoding='utf-8', newline='\n') as in_file:
                in_file.write(test.write_test_in())

        # Phase 2: validate inputs.
        for test, file_path in tests:
            test.validate_test_in(file_path + '.in')

        # Phase 3: generate answers (run solution).
        if self.solution is not None:
            self.solution.compile()
        for test, file_path in tests:
            print(f"Writing ans (out) file {file_path + '.ans'}")
            with open(file_path + '.ans', 'w', encoding='utf-8', newline='\n') as out_file:
                out_file.write(test.write_test_out(file_path + '.in'))

    def _zip_file_path(self, problem_name: str, test_set_name: str) -> str:
        """Return the absolute zip path for a problem test set."""
        return os.path.join(self.problem_dir, f'{problem_name}_{test_set_name}.zip')

    def _zip_submissions(self, zip_file: zipfile.ZipFile) -> None:
        """Add every file under ``submissions/`` to ``zip_file``."""
        submissions_dir = os.path.join(self.problem_dir, 'submissions')
        for root, _, files in os.walk(submissions_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, self.problem_dir)
                zip_file.write(file_path, arcname)

    def _write_metadata(self, zip_file: zipfile.ZipFile,
                        final_name: str, test_set: Subproblem) -> None:
        """Write the DOMjudge metadata file for a test set into ``zip_file``."""
        lines = [
            f'name={final_name}_{test_set.name}',
            f'timelimit={test_set.time_limit}',
        ]
        if self.custom_checker is not None:
            lines.append(f"special_compare='{self.custom_checker}'")
        zip_file.writestr('domjudge-problem.ini', '\n'.join(lines) + '\n')

    def create_zip(self, name_prefix='draft_'):
        """
        Create a zip for each test set. Each test set consists of data, submissions,
        and the DOMjudge metadata file.
        """
        final_name = name_prefix + self.problem_name

        for test_set in self.test_sets:
            file_path = self._zip_file_path(final_name, test_set.name)
            print(f'Creating zip for test set "{test_set.name}" at "{file_path}...')
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in self.test_paths[test_set.name]:
                    zip_file.write(file + '.in', os.path.relpath(file + '.in', self.problem_dir))
                    zip_file.write(file + '.ans', os.path.relpath(file + '.ans', self.problem_dir))

                self._zip_submissions(zip_file)
                self._write_metadata(zip_file, final_name, test_set)

            print(f'Done creating zip for test set "{test_set.name}"!')

    def add_final_metadata(self, p_num: int):
        """
        DEPRECATED:
        Upload metadata to contest.
        """
        print("adding metadata")
        i = 0
        for sub_test in self.test_sets:
            subproblem = sub_test.name

            label = str(p_num)
            if i > 0:
                label = label + f'b{i}'
            add_problem_metadata_to_contest(
                    self.problem_name + '_' + subproblem,
                    label,
                    sub_test.color(),
                    )
            i += 1

    def upload(self):
        i = 0
        for test_set in self.test_sets:
            pid = self.problem_name + '_' + test_set.name
            label = pid
            judge_problem = get_problem(pid)
            if judge_problem is None:
                print('problem not found... creating problem')
                if self.label_prefix != -1:
                    label = str(self.label_prefix)
                    if i > 0:
                        label = label + f'b{i}'
                add_problem_metadata_to_contest(pid, label, test_set.color())
            zip_file_path = self._zip_file_path(self.problem_name, test_set.name)
            pid = upload_problem_zip(zip_file_path, pid)
            i = i + 1

    def link_to_contest(self):
        """
        Link to contest, label_prefix is used for tag (1 if this is the first problem, -1 to use pid as tag).
        """
        i = 0
        for test_set in self.test_sets:
            pid = self.problem_name + '_' + test_set.name
            label = pid
            print("== Linking to Contest ==")
            # try:
            #     unlink_problem_from_contest(pid)
            # except Exception:
            #     pass
            if self.label_prefix != -1:
                label = str(self.label_prefix)
                if i > 0:
                    label = label + f'b{i}'
            judge_problem = get_problem(pid)
            if judge_problem is None:
                link_problem_to_contest(pid, label, test_set.color())
            else:
                print('Warning: problem already linked, skipping...')
            i = i + 1


    # @deprecated("Use 'from calico_lib import run_cli' instead.")
    def run_cli(self, pre_fn: Callable[[], None]|None = None):
        """
        DEPRECATED
        """
        """
        Run pre_fn before generating test cases.
        """
        print('Warning: using deprecated function..., use "from calico_lib import run_cli" instead.')
        if pre_fn is not None:
            assert self.pre_fn is None
            self.pre_fn = pre_fn
        assert self._cli_func is not None
        self._cli_func()
