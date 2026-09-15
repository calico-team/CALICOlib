#!/usr/bin/env python3

# Laser problem.

import math
import os
import random
from collections.abc import Iterable
from os import path
from typing import NamedTuple, override

from calico_lib import Problem, Subproblem, TestFileBase, cpp_runner, py_runner, run_cli

problem_dir = os.path.dirname(__file__)

class TestCase(NamedTuple):
    K: int
    N: int
    M: int
    P: int
    Q: int
    X: list[int]
    Y: list[int]

solution = py_runner(path.join(problem_dir, 'submissions/accepted/laser_bonus.py'))
solution2 = cpp_runner(
        path.join(problem_dir, 'submissions/accepted/laser_bonus.cpp'),
        path.join(problem_dir, 'laser_bonus.bin'))
validator1 = py_runner(path.join(problem_dir, 'scripts/validator_main.py'))
validator2 = py_runner(path.join(problem_dir, 'scripts/validator.py'))

p = Problem(
        'laser',
        problem_dir,
        test_sets=[
            Subproblem('main', rank=1),
            Subproblem('bonus', rank=3),
            ],
        solution=solution,
        seed='asteroids')

class TestFile(TestFileBase):
    def __init__(self, cases: Iterable[TestCase]) -> None:
        self.cases = list(cases)
        super().__init__()

    @override
    def write_test_in(self) -> str:
        """Return the input text for this test file."""
        lines = [str(len(self.cases))]
        for case in self.cases:
            lines.append(f'{case.K} {case.N} {case.M} {case.P} {case.Q}')
            for x, y in zip(case.X, case.Y):
                lines.append(f'{x} {y}')
        return '\n'.join(lines) + '\n'

    @override
    def validate_test_in(self, infile: str) -> None:
        """Verify the test using an external validator."""
        if 'main' in self.subproblems:
            validator1.exec_file(infile)
        validator2.exec_file(infile)

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
    run_cli(p)

if __name__ == '__main__':
    main()
