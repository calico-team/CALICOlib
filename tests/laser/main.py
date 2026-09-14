#!/usr/bin/env python3

# Example add problem.
# Constraints:
#   main: T <= 100, A <= 100, B <= 100
#   bonus: T <= 1e5, A <= 1e12, B <= 1e12

from typing import override
from calico_lib import Problem, cpp_runner, py_runner, TestFileBase, MulticaseTestFile, Subproblem, Runner
from collections.abc import Collection, Iterable
from typing import NamedTuple, override
import random
import os
import math
from os import path

from calico_lib.multicase import TestCaseBase

problem_dir = os.path.dirname(__file__)

p = Problem(
        'laser',
        problem_dir, # problem is in the same directory as the python source file
        test_sets=[
            Subproblem('main', rank=1),
            Subproblem('bonus', rank=3),
            ])

class TestCase(NamedTuple):
    K: int
    N: int
    M: int
    P: int
    Q: int
    X: list[int]
    Y: list[int]

sol = py_runner("submissions/accepted/laser_bonus.py")
sol2 = cpp_runner(
        'submissions/accepted/laser_bonus.cpp',
        'laser_bonus.bin')
validator1 = py_runner('scripts/validator_main.py')
validator2 = py_runner('scripts/validator.py')

@p.pre_gen_fn
def pre_gen_fn():
    random.seed('asteroids')
    #sol2.compile()

class TestFile(TestFileBase):
    def __init__(self, cases: Iterable[TestCase]) -> None:
        self.cases = list(cases)
        super().__init__()

    @override
    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        p.print_test(len(self.cases))
        for case in self.cases:
            p.print_test(case.K, case.N, case.M, case.P, case.Q)
            for x, y in zip(case.X, case.Y):
                p.print_test(x, y)

    @override
    def validate_test_in(self, infile: str):
        """Verify the test using an external validator."""
        if 'main' in self.subproblems:
            validator1.exec_file(infile)
        validator2.exec_file(infile)

    @override
    def write_test_out(self, infile: str):
        p.print_test(sol.exec_file(infile))
        #p.print_test(sol2.exec_file(infile))

# adds to all subproblems by default
p.add_sample_test(TestFile([
    TestCase(3, 10, 10, 1, 1, [0, 2, 9], [0, 2, 9]),
    TestCase(3, 6, 8, 2, 1, [1, 1, 5], [1, 5, 1]),
    TestCase(3, 6, 8, 2, 1, [1, 2, 4], [1, 3, 4]),
    TestCase(3, 5, 5, 2, 3, [2, 0, 1], [2, 0, 4]),
    ]))

# Bonus Sample Test
p.add_sample_test(TestFile([
    TestCase(5, 999999, int(1e6), 2, 1, 
             [0, 500000, 999997, 499995, 499995], 
             [0, 1, 0, 0, 1]),
    ]), subproblems=['bonus']) 

#cases = [] 
#for i in range(80):
#    cases.append(TestCase(i+1, 80-i))

#p.add_hidden_test(TestFile(cases), 'iota')
    
#cases = []
#for i in range(100):
#    cases.append(TestCase(i+1, 10000-i))

#p.add_hidden_test(TestFile(cases), 'iota', subproblems=['bonus'])

# more ways to add test cases. This is preferred, since running the function is offloaded to run only at test generation.


def gen_coords(K: int, M: int, N: int):
    X = []
    Y = []
    used: set[tuple[int, int]] = set()
    for _ in range(K):
        x = random.randint(0, N - 1)
        y = random.randint(0, M - 1)
        while (x, y) in used:
            x = random.randint(0, N - 1)
            y = random.randint(0, M - 1)
        used.add((x, y))
        Y.append(y)
        X.append(x)
    return X, Y

def gen_case(max_K: int, max_N: int):
    K = random.randint(1, max_K)
    M = random.randint(K if K < 500 else K // 2, max_N)
    N = random.randint(K, max_N)
    if random.randint(0, 1) == 1:
        N, M = M, N
    P = random.randint(1, M)
    Q = random.randint(1, N)

    G = math.gcd(P, Q)
    P //= G
    Q //= G

    X, Y = gen_coords(K, M, N)
    return TestCase(K, N, M, P, Q, X, Y)


@p.hidden_test_generator(test_count=4, subproblems=['main', 'bonus'])
def pure_random() -> TestFile:
    test = TestFile([])
    for i in range(10):
        test.cases.append(gen_case(100, 1000))
    return test

@p.hidden_test_generator(test_count=8, subproblems=['main', 'bonus'])
def pure_random_small() -> TestFile:
    test = TestFile([])
    for i in range(10):
        test.cases.append(gen_case(i+1, 15))
    return test

@p.hidden_test_generator(test_count=2, subproblems=['main', 'bonus'])
def random_no_asteroid():
    test = TestFile([])
    for i in range(10):
        test.cases.append(gen_case(1, 1000))
    return test

@p.hidden_test_generator(test_count=2, subproblems=['bonus'])
def pure_random_bonus():
    test = TestFile([])
    for i in range(5):
        test.cases.append(gen_case(int(1.5e4), int(1e6)))
    return test

@p.hidden_test_generator(test_count=8, subproblems=['bonus'])
def pure_random_bonus_large():
    test = TestFile([])
    for i in range(1):
        test.cases.append(gen_case(int(1e5), int(1e6)))
    return test

@p.hidden_test_generator(test_count=2, subproblems=['bonus'])
def random_no_asteroid_bonus():
    test = TestFile([])
    for i in range(10):
        test.cases.append(gen_case(1, int(1e6)))
    return test


def main():
    # increase stack size for running solutions using heaving recursion
    # import resource
    # resource.setrlimit(resource.RLIMIT_STACK, (268435456, 268435456))

    # TODO: set seed
    p.run_cli()

    # p.init_problem()
    # p.create_all_tests()
    # p.create_zip()

if __name__ == '__main__':
    main()
