from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
import os
import shutil
from typing import Dict, NamedTuple
import zipfile
from .legacy import *
import traceback

class TestFileBase[T](ABC):
    # TODO: consider storing filename in this class

    type Test = T | Collection[T]
    subproblems: Collection[str]

    def __init__(self) -> None:
        # The list of subproblems this test should belong to
        self.subproblems = []

    @abstractmethod
    def write_test_in(self):
        """Write the input file of this test using print_test"""
        pass

    @abstractmethod
    def write_test_out(self, infile: str):
        """Write the solution file, with input already written in infile"""
        pass

    @abstractmethod
    def validate_test_in(self, infile: str):
        """Validate the current test in, written in infile"""
        # assert False, "Must validate test"
        pass

# A test consist of either a single case or multiple test cases

_SAMPLE_PATH = os.path.join('data', 'sample')
_SECRET_PATH = os.path.join('data', 'secret')
_DEFAULT_MEMLIMIT = 256_000_000

class Subproblem(NamedTuple):
    name: str
    rank: int
    time_limit: int = 1
    mem_limit: int = _DEFAULT_MEMLIMIT

class Problem[T: TestFileBase]:
    def __init__(self, problem_name: str, test_sets = []):
        self.problem_name = problem_name
        self.test_sets: list[Subproblem] = test_sets;

        self.sample_count = 0
        self.hidden_count = 0

        # mapping from test sets to tests included in that test set
        self.test_paths: Dict[str, list[str]] = dict()
        for subproblem in test_sets:
            self.test_paths[subproblem] = []

        # the current file that we will write to with print_test
        self._cur_file = None
        self._all_test_generators = []

        os.makedirs(os.path.join('submissions', 'accepted'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'run_time_error'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'time_limit_exceeded'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'wrong_answer'), exist_ok=True)

    def add_test_set(self, problem_name: str, rank: int, time_limit = 1, mem_limit: int = _DEFAULT_MEMLIMIT):
        self.test_sets.append(Subproblem(problem_name, rank, time_limit, mem_limit))

    def print_test(
            self,
            *values: object,
            sep: str | None = " ",
            end: str | None = "\n",
            ):
        """Print data to the test file. Arguments are the same as print."""
        assert self._cur_file != None, "This function should be called in one of the test_write_* function"
        print(*values, sep=sep, end=end, file=self._cur_file)

    def _add_test(self, test: TestFileBase, file_name: str, subproblems: list[str] = ['main']):
        def test_generator():
            with open(file_name + '.in', 'w') as in_file:
                self._cur_file = in_file
                print(f"Writing infile {file_name+'.in'}")
                test.write_test_in()
            self._cur_file = None

            try:
                test.validate_test_in(file_name + '.in')
            except AssertionError:
                print(f"!!--------------------------------------------")
                print(f"Validation failed on testcase {file_name}")
                print(traceback.format_exc())
                # pass
            with open(file_name + '.out', 'w') as out_file:
                self._cur_file = out_file
                test.write_test_out(file_name + '.in')
            self._cur_file = None

        self._all_test_generators.append(test_generator)
        test.subproblems = subproblems
        for subproblem in subproblems:
            self.test_paths[subproblem].append(file_name)

    def add_sample_test(self, test: TestFileBase, name: str='', subproblems: list[str] = ['main']):
        if name != '': name = '_' + name
        filepath = os.path.join(_SAMPLE_PATH, f'{self.sample_count:02d}_{subproblems[-1]}{name}')
        self.sample_count += 1
        self._add_test(test, filepath, subproblems)

    def add_hidden_test(self, test: TestFileBase, name: str='', subproblems: list[str] = ['main']):
        if name != '': name = '_' + name
        filepath = os.path.join(_SECRET_PATH, f'{self.hidden_count:02d}_{subproblems[-1]}{name}')
        self.hidden_count += 1
        self._add_test(test, filepath, subproblems)

    def hidden_test_generator(self, test_count = 1, subproblems: list[str] = ['main']):
        """Add a hidden test generator. Repeats to generate test_count number of test files.
        Repeat case_per_test times for each test.
        """
        def generator(gen_fn: Callable[[], T]):
            for _ in range(test_count):
                self.add_hidden_test(gen_fn(), gen_fn.__name__, subproblems)
            return gen_fn
        return generator

    def test_validator(self, validator: Callable[[Collection[T]], None]):
        self._test_validator = validator
        return validator

    def create_all_tests(self):
        """Delete existing tests and regenerate them based on all the tests and generators added."""
        try:
            shutil.rmtree(_SAMPLE_PATH)
            shutil.rmtree(_SECRET_PATH)
        except FileNotFoundError:
            # First time running
            pass
        os.makedirs(_SAMPLE_PATH, exist_ok=True)
        os.makedirs(_SECRET_PATH, exist_ok=True)
        for fn in self._all_test_generators:
            fn()

    def create_zip(self):
        """
        Create a zip for each test set. Each test set consists of data, submissions,
        and the DOMjudge metadata file.
        """
        for test_set in self.test_sets:
            file_path = get_zip_file_path(self.problem_name, test_set.name)
            print(f'Creating zip for test set "{test_set.name}" at "{file_path}...')
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in self.test_paths[test_set.name]:
                    zip_file.write(file+'.in')
                    zip_file.write(file+'.out')

                zip_path(zip_file, 'submissions', test_set.name, lambda _, _2: True)
                zip_metadata(zip_file, self.problem_name, test_set.name, test_set.time_limit)

            print(f'Done creating zip for test set "{test_set.name}"!')
