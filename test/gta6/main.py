#!/usr/bin/env python3

# Example add problem.
# Constraints:
#   main: T <= 100, A <= 100, B <= 100
#   bonus: T <= 1e5, A <= 1e12, B <= 1e12

from calico_lib import Problem, cpp_runner, py_runner, TestFileBase, MulticaseTestFile, Subproblem, Runner
from collections.abc import Collection, Iterable
from typing import NamedTuple
import random
import os
from os import path

from calico_lib.multicase import TestCaseBase

problem_dir = os.path.dirname(__file__)

p = Problem(
        'gta6',
        problem_dir, # problem is in the same directory as the python source file
        test_sets=[
            Subproblem('main', rank=1),
        ])

class TestCase(NamedTuple):
    E: str
    D: int
    M: int
    Y: int

solution = py_runner(path.join(problem_dir, 'submissions/accepted/gta6.py'))
solution2 = cpp_runner(
        path.join(problem_dir, 'submissions/accepted/gta6.cpp'),
        path.join(problem_dir, 'gta6.bin'))
validator1 = py_runner(path.join(problem_dir, 'scripts/validator_main.py'))
validator2 = py_runner(path.join(problem_dir, 'scripts/validator.py'))

@p.pre_gen_fn
def pre_gen():
    random.seed('6')

class TestFile(TestFileBase):
    def __init__(self, cases: Iterable[TestCase]) -> None:
        self.cases = list(cases)
        super().__init__()

    # @override
    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        p.print_test(len(self.cases))
        for case in self.cases:
            p.print_test(case.E)
            p.print_test("{:04d}".format(case.Y), "{:02d}".format(case.M), "{:02d}".format(case.D))

    # @override
    def validate_test_in(self, infile: str):
        """Verify the test using an external validator."""
        #if 'main' in self.subproblems:
        #    validator1.exec_file(infile)
        #validator2.exec_file(infile)
        for c in self.cases:
            assert c.D >= 1 and c.D <= 31
            assert c.M >= 1 and c.M <= 12
            assert c.Y >= 0 and c.Y <= 2200


    # @override
    def write_test_out(self, infile: str):
        p.print_test(solution.exec_file(infile))

# adds to all subproblems by default
p.add_sample_test(TestFile([
    TestCase("calico", 9, 11, 2025),
    TestCase("big ben's bday", 6, 9, 2026),
    TestCase("six eight", 27, 12, 2026),
    TestCase("gta6 eve", 18, 11, 2026),
    TestCase("contest start", 31, 12, 2200)
]))

# edge cases
p.add_hidden_test(TestFile([
    TestCase("gta 6 anniversary", 26, 5, 2027),
    TestCase("afjafi", 31, 5, 2025),
    TestCase("67", 6, 7, 2026),
    TestCase("beginning of time", 1, 1, 0),
    TestCase("12", 12, 12, 12)
]))

# cases = []
# for i in range(80):
#     cases.append(TestCase(i+1, 80-i))

# p.add_hidden_test(TestFile(cases), 'iota')
    
# cases = []
# for i in range(100):
#     cases.append(TestCase(i+1, 10000-i))

# p.add_hidden_test(TestFile(cases), 'iota', subproblems=['bonus'])

def random_string(length: int) -> str:
    string = ""
    for _ in range(length):
        string += chr(ord('a') + random.randint(0, 25))
    return string

# more ways to add test cases
@p.hidden_test_generator(test_count=4)
def pure_random() -> TestFile:
    test = TestFile([])
    for i in range(100):
        E = random_string(random.randint(1, 100))
        test.cases.append(TestCase(E, random.randint(1, 31), random.randint(1, 12), random.randint(0, 2200)))
    return test

# @p.hidden_test_generator(test_count=4, subproblems=['bonus'])
# def pure_random2():
#     cases = (TestCase(random.randint(70, int(1e12)), random.randint(70, int(1e12))) for _ in range(100))
#     return TestFile(cases)

def main():
    # increase stack size for running solutions using heaving recursion
    # import resource
    # resource.setrlimit(resource.RLIMIT_STACK, (268435456, 268435456))

    # TODO: set seed
    #solution2.compile()
    p.run_cli()

    # p.init_problem()
    # p.create_all_tests()
    # p.create_zip()

if __name__ == '__main__':
    main()
