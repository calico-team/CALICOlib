from abc import ABC, abstractmethod
from collections.abc import Callable, Collection
import os
import shutil
from typing import Dict, NamedTuple
import zipfile

from calico_lib.judge_api import add_problem_metadata_to_contest, link_problem_to_contest, set_contest_id, set_user, unlink_problem_from_contest, upload_problem_zip
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

class Problem:
    test_sets: list[Subproblem]
    problem_dir: str
    custom_checker: None|str

    def __init__(self, problem_name: str, problem_dir: str, test_sets: list[Subproblem] = []):
        self.problem_name = problem_name
        self.test_sets = test_sets
        self.problem_dir = problem_dir
        self.custom_checker = None

        self.sample_count = 0
        self.hidden_count = 0

        self.always_skip_test_gen = False

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
        Upload metadata to contest.
        """
        print("adding metadata")
        i = 0
        for sub_test in self.test_sets:
            subproblem = sub_test.name

            rank_color_map = {
                    1: '#e9e4d7',
                    2: '#ff7e34',
                    3: '#995d59',
                    4: '#000000',
                    }
            label = str(p_num)
            if i > 0:
                label = label + f'b{i}'
            add_problem_metadata_to_contest(
                    self.problem_name + '_' + subproblem,
                    label,
                    rank_color_map[sub_test.rank],
                    )

    def write_lockfile_pid(self, test_set, pid):
        lockfile = self.problem_name + '_' + test_set.name + '.lock'
        if pid is not None:
            with open(lockfile, 'w', encoding='utf-8') as f:
                f.write(str(pid) + '\n')

    def run_cli(self, pre_fn: Callable[[], None]|None = None):
        """
        Run pre_fn before generating test cases.
        """
        os.chdir(self.problem_dir)
        self.init_problem()

        parser = argparse.ArgumentParser(
                        prog='CALICOLib problem CLI',
                        description='CLI interface for various actions for this problem. By default, generates and verifies test cases.',
                        epilog='')

        parser.add_argument('-a', '--auth', help='Username and password for judge, separated by colon.')
        parser.add_argument('-c', '--cid', type=str, help='Add the problem to the contest id. Impiles -u.')
        parser.add_argument('-u', '--upload', action='store_true', help='Create or update the problem on the judge. Defaults to a draft version, unless -f is specified.')
        parser.add_argument('-s', '--skip-test-gen', action='store_true', help='Skip test generation.')
        parser.add_argument('-f', '--final', action='store_true', help='Operates on the final version.')
        parser.add_argument('-i', '--p-ord', type=int, help='Problem order.')

        args = parser.parse_args()
        if args.auth is not None:
            set_user(tuple(args.auth.split(':')))

        if args.final:
            self.problem_name = self.problem_name
            assert args.p_ord is not None
        else:
            self.problem_name = self.problem_name + '_draft'

        if args.cid is not None:
            set_contest_id(args.cid)

        if not args.skip_test_gen:
            if not self.always_skip_test_gen:
                print('\n=== Creating Tests ===')
                if pre_fn is not None:
                    print('\n=== Running Tasks ===')
                    pre_fn()
                self.create_all_tests()

            print('\n=== Creating Zip ===')
            self.create_zip('')

        if args.cid is not None or args.upload:
            print('\n=== Uploading ===')
        else:
            return

        i = 0
        for test_set in self.test_sets:
            subproblem = test_set.name
            pid = self.problem_name + '_' + subproblem
            label = self.problem_name + '_' + subproblem
            if pid is not None:
                upload_problem_zip(get_zip_file_path(self.problem_name, test_set.name), pid)
            else:
                if args.final:
                    label = str(args.p_ord)
                    if i > 0:
                        label = label + f'b{i}'
                pid = upload_problem_zip(
                        get_zip_file_path(self.problem_name, test_set.name), pid)
            if args.cid is not None:
                print("linking to contest")
                try:
                    unlink_problem_from_contest(pid)
                except Exception:
                    pass
                rank_color_map = {
                        1: '#e9e4d7',
                        2: '#ff7e34',
                        3: '#995d59',
                        4: '#000000',
                        }
                link_problem_to_contest(pid, label, rank_color_map[test_set.rank])
            i = i + 1

