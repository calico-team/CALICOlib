from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
import os
from os.path import dirname
import shutil
from typing import Dict
import zipfile
from .legacy import *

class TestCaseBase(ABC):
    @abstractmethod
    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        pass

    @abstractmethod
    def verify_case(self, test_sets: list[str]):
        """Verify the test using assert"""
        pass

# A test consist of either a single case or multiple test cases
type Test = TestCaseBase | Collection[TestCaseBase]

_SAMPLE_PATH = os.path.join('data', 'sample')
_SECRET_PATH = os.path.join('data', 'secret')

class Problem[T: TestCaseBase]:
    def __init__(self, problem_name: str, time_limit: int, mem_limit: int, test_sets: list[str] = ['main']):
        self.problem_name = problem_name
        self.time_limit = time_limit
        self.mem_limit = mem_limit
        self.test_sets = test_sets;

        self.sample_count = 0
        self.hidden_count = 0

        # mapping from test sets to tests included in that test set
        self.test_paths: Dict[str, list[str]] = dict()
        for subproblem in test_sets:
            self.test_paths[subproblem] = []

        self._cur_file = None
        self._test_validator = None
        self._all_test_generators = []

        os.makedirs(os.path.join('submissions', 'accepted'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'run_time_error'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'time_limit_exceeded'), exist_ok=True)
        os.makedirs(os.path.join('submissions', 'wrong_answer'), exist_ok=True)

    # def create_test():
    #     pass

    def print_test(
            self,
            *values: object,
            sep: str | None = " ",
            end: str | None = "\n",
            ):
        """Print data to the test file. Arguments are the same as print."""
        assert self._cur_file != None
        print(*values, sep=sep, end=end, file=self._cur_file)

    def _add_test(self, cases: Test, file_name: str, subproblems: list[str] = ['main']):
        def test_generator():
            with open(file_name + '.in', 'w') as in_file:
                self._cur_file = in_file
                if isinstance(cases, TestCaseBase):
                    cases.verify_case(subproblems)
                    cases.write_test_in()
                else:
                    self.print_test(len(cases))
                    for case in cases:
                        case.verify_case(subproblems)
                        case.write_test_in()
            with open(file_name + '.out', 'w') as out_file:
                self._cur_file = out_file
                self._test_out_writer(file_name + '.in')
        self._all_test_generators.append(test_generator)
        for subproblem in subproblems:
            self.test_paths[subproblem].append(file_name)

    def add_sample_test(self, cases: Test, name: str='', subproblems: list[str] = ['main']):
        if name != '': name = '_' + name
        filepath = os.path.join(_SAMPLE_PATH, f'{self.sample_count:02d}_{subproblems[-1]}{name}')
        self.sample_count += 1
        self._add_test(cases, filepath, subproblems)

    def add_hidden_test(self, cases: Test, name: str='', subproblems: list[str] = ['main']):
        if name != '': name = '_' + name
        filepath = os.path.join(_SECRET_PATH, f'{self.hidden_count:02d}_{subproblems[-1]}{name}')
        self.hidden_count += 1
        self._add_test(cases, filepath, subproblems)

    def hidden_test_generator(self, case_per_test: int, test_count = 1, subproblems: list[str] = ['main']):
        """Add a hidden test generator. Repeats to generate test_count number of test files.
        Repeat case_per_test times for each test.
        """
        def generator(gen_fn: Callable[[int], T]):
            for i in range(test_count):
                cases = [gen_fn(i) for _ in range(case_per_test)]
                assert self._test_validator is not None
                self._test_validator(cases)
                self.add_hidden_test(cases, gen_fn.__name__, subproblems)
            return gen_fn
        return generator

    def test_validator(self, validator: Callable[[Collection[T]], None]):
        self._test_validator = validator
        return validator

    def test_out_writer(self, fn: Callable[[str], None]):
        self._test_out_writer = fn
        return fn

    def create_all_tests(self):
        """Delete existing tests and regenerate them based on all the tests and generators added."""
        shutil.rmtree(_SAMPLE_PATH)
        shutil.rmtree(_SECRET_PATH)
        os.makedirs(_SAMPLE_PATH, exist_ok=True)
        os.makedirs(_SECRET_PATH, exist_ok=True)
        for fn in self._all_test_generators:
            fn()

    def create_zip(self):
        """
        Create a zip for each test set. Each test set consists of data, submissions,
        and the DOMjudge metadata file.
        """
        for test_set_name in self.test_sets:
            file_path = get_zip_file_path(self.problem_name, test_set_name)
            print(f'Creating zip for test set "{test_set_name}" at "{file_path}...')
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in self.test_paths[test_set_name]:
                    zip_file.write(file+'.in')
                    zip_file.write(file+'.out')

                zip_path(zip_file, 'submissions', test_set_name, lambda _, _2: True)
                zip_metadata(zip_file, self.problem_name, test_set_name, self.time_limit)

            print(f'Done creating zip for test set "{test_set_name}"!')
