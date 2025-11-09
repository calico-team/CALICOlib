from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
import os
import shutil
from typing import Dict, NamedTuple
# from warnings import deprecated
import zipfile

from .judge_api import add_problem_metadata_to_contest, get_problem, link_problem_to_contest, set_contest_id, set_user, unlink_problem_from_contest, upload_problem_zip
import argparse
from .legacy import *
import traceback
import subprocess

# TODO:
# screw problem dir, just have user cd into dir

class TestFileBase(ABC):
    # TODO: consider storing filename in this class

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

_DEFAULT_MEMLIMIT = 256_000_000

class Subproblem(NamedTuple):
    name: str
    rank: int
    time_limit: int = 1
    mem_limit: int = _DEFAULT_MEMLIMIT
    def color(self):
        rank_color_map = {
                1: '#e9e4d7',
                2: '#ff7e34',
                3: '#995d59',
                4: '#000000',
                }
        return rank_color_map[self.rank]

class Problem:
    test_sets: list[Subproblem]
    problem_dir: str
    custom_checker: None|str

    _cli_func: Callable|None = None

    def __init__(self, problem_name: str, problem_dir: str, test_sets: list[Subproblem] = []):
        self.problem_name = problem_name
        self.test_sets = test_sets
        self.problem_dir = problem_dir
        self.custom_checker = None

        # order of the problem in the contest. Used for label. Otherwise, label is problem_name
        self.ordinal = -1

        self.sample_count = 0
        self.hidden_count = 0

        self.always_skip_test_gen = False
        self.pre_fn = None

        # mapping from test sets to tests included in that test set
        self.test_paths: Dict[str, list[str]] = dict()
        for subproblem in test_sets:
            self.test_paths[subproblem.name] = []

        # the current file that we will write to with print_test
        self._cur_file = None
        self._sample_path = os.path.join('data', 'sample')
        self._secret_path = os.path.join('data', 'secret')
        self._all_test_generators = []


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

    def print_test(
            self,
            *values: object,
            sep: str | None = " ",
            end: str | None = "\n",
            ):
        """Print data to the test file. Arguments are the same as print."""
        assert self._cur_file != None, "This function should be called in one of the test_write_* function"
        print(*values, sep=sep, end=end, file=self._cur_file)

    def _add_test(self,
                  test_file_or_fn: TestFileBase|Callable[[], TestFileBase],
                  file_dir: str,
                  file_prefix: str,
                  subproblems: list[str]|None = None):
        if subproblems is None:
            subproblems = [s.name for s in self.test_sets]
        file_path = os.path.join(file_dir, file_prefix + '_' + subproblems[0])
        def test_generator():
            if callable(test_file_or_fn):
                test = test_file_or_fn()
            else:
                test = test_file_or_fn
            test.subproblems = subproblems
            with open(file_path + '.in', 'w', encoding='utf-8', newline='\n') as in_file:
                self._cur_file = in_file
                print(f"Writing infile {file_path+'.in'}")
                test.write_test_in()
            self._cur_file = None

            # try:
            test.validate_test_in(file_path + '.in')
            # except (AssertionError, subprocess.CalledProcessError):
            #     print(f"!!--------------------------------------------")
            #     print(f"Validation failed on testcase {file_name}")
            #     print(traceback.format_exc())
            #     # pass
            with open(file_path + '.ans', 'w', encoding='utf-8', newline='\n') as out_file:
                self._cur_file = out_file
                print(f"Writing ans (out) file {file_path+'.ans'}")
                test.write_test_out(file_path + '.in')
            self._cur_file = None

        self._all_test_generators.append(test_generator)
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
        if isinstance(test_or_fn, TestFileBase):
            print(f'[Warning]: {self.problem_name} hidden test added in place...')
        if name != '': name = '_' + name
        self._add_test(test_or_fn, self._secret_path, f'{self.hidden_count:02d}{name}', subproblems)
        self.hidden_count += 1

    def hidden_test_generator(self, test_count = 1, subproblems: list[str] = ['main']):
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

    def create_all_tests(self):
        """Delete existing tests and regenerate them based on all the tests and generators added."""
        os.chdir(self.problem_dir)

        try:
            shutil.rmtree(self._sample_path)
            shutil.rmtree(self._secret_path)
        except FileNotFoundError:
            # First time running
            pass
        os.makedirs(self._sample_path, exist_ok=True)
        os.makedirs(self._secret_path, exist_ok=True)

        if self.pre_fn is not None:
            print('\nRunning pre generation tasks...')
            self.pre_fn()
        for fn in self._all_test_generators:
            fn()

    def create_zip(self, name_prefix='draft_'):
        """
        Create a zip for each test set. Each test set consists of data, submissions,
        and the DOMjudge metadata file.
        """
        os.chdir(self.problem_dir)

        final_name = name_prefix + self.problem_name

        for test_set in self.test_sets:
            file_path = get_zip_file_path(final_name, test_set.name)
            file_path = os.path.join(self.problem_dir, file_path)
            print(f'Creating zip for test set "{test_set.name}" at "{file_path}...')
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in self.test_paths[test_set.name]:
                    zip_file.write(file+'.in')
                    zip_file.write(file+'.ans')

                zip_path(zip_file, 'submissions', test_set.name, lambda _, _2: True)
                zip_metadata(zip_file,
                             final_name,
                             test_set.name,
                             test_set.time_limit,
                             self.custom_checker)

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
                if self.ordinal != -1:
                    label = str(self.ordinal)
                    if i > 0:
                        label = label + f'b{i}'
                add_problem_metadata_to_contest(pid, label, test_set.color())
            pid = upload_problem_zip(get_zip_file_path(self.problem_name, test_set.name), pid)
            i = i + 1

    def link_to_contest(self):
        """
        Link to contest, ordinal is used for tag (1 if this is the first problem, -1 to use pid as tag).
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
            if self.ordinal != -1:
                label = str(self.ordinal)
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
        if pre_fn is not None:
            assert self.pre_fn is None
            self.pre_fn = pre_fn
        assert self._cli_func is not None
        self._cli_func()
