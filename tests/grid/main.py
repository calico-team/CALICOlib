#!/usr/bin/env python3

# Grid problem.
# You have a 2 by N grid of numbers. The first row is given (an array of length N).
# Fill in the second row of the grid such that the sum of absolute differences
# of adjacent numbers on the grid is minimized.
#
# Constraints:
#   main: T <= 10, N = 3, 1 <= val <= 10^9
#   bonus: T <= 10, N <= 100000, 1 <= val <= 10^9

import os
import random
from collections.abc import Iterable
from os import path
from typing import NamedTuple, override

from calico_lib import Problem, Subproblem, TestFileBase, cpp_runner, py_runner

problem_dir = os.path.dirname(__file__)

solution = cpp_runner(
        path.join(problem_dir, 'submissions/accepted/sol.cpp'),
        path.join(problem_dir, 'sol.bin'))
validator = py_runner(path.join(problem_dir, 'scripts/validator.py'))
validator_main = py_runner(path.join(problem_dir, 'scripts/validator_main.py'))

p = Problem(
        'grid',
        problem_dir,
        test_sets=[
            Subproblem('main', rank=2),
            Subproblem('bonus', rank=2),
            ],
        solution=solution,
        seed='grid_sp26_seed')

p.custom_checker = 'grid_compare'

class TestCase(NamedTuple):
    N: int
    row: list[int]

@p.pre_gen_fn
def pre_gen_fn():
    solution.compile()

class TestFile(TestFileBase):
    def __init__(self, cases: Iterable[TestCase]) -> None:
        self.cases = list(cases)
        super().__init__()

    @override
    def write_test_in(self) -> str:
        """Return the input text for this test file."""
        lines = [str(len(self.cases))]
        for case in self.cases:
            lines.append(str(case.N))
            lines.append(' '.join(map(str, case.row)))
        return '\n'.join(lines) + '\n'

    @override
    def validate_test_in(self, infile: str) -> None:
        """Verify the test using an external validator."""
        if 'main' in self.subproblems:
            validator_main.exec_file(infile)
        validator.exec_file(infile)

# Main sample test (N = 3 only)
p.add_sample_test(TestFile([
    TestCase(3, [1, 5, 1]),
    ]), subproblems=['main'])

# Bonus sample test (original, varied N)
p.add_sample_test(TestFile([
    TestCase(4, [1, 2, 3, 4]),
    ]), subproblems=['bonus'])

# --- Main tests (N = 3 only) ---

p.add_hidden_test(TestFile([TestCase(3, [1, 2, 3])]), 'iota', subproblems=['main'])

@p.hidden_test_generator(test_count=4, subproblems=['main'])
def pure_random_main() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        row = [random.randint(1, 10**9) for _ in range(3)]
        test.cases.append(TestCase(3, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['main'])
def sorted_asc_main() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        row = sorted(random.randint(1, 10**9) for _ in range(3))
        test.cases.append(TestCase(3, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['main'])
def sorted_desc_main() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        row = sorted((random.randint(1, 10**9) for _ in range(3)), reverse=True)
        test.cases.append(TestCase(3, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['main'])
def all_same_main() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        val = random.randint(1, 10**9)
        test.cases.append(TestCase(3, [val, val, val]))
    return test

@p.hidden_test_generator(test_count=2, subproblems=['main'])
def extremes_main() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        row = [random.choice([1, 10**9]) for _ in range(3)]
        test.cases.append(TestCase(3, row))
    return test

# --- Bonus tests (varied N) ---

# Iota-style tests
cases = []
for i in range(10):
    N = i + 1
    cases.append(TestCase(N, list(range(1, N + 1))))
p.add_hidden_test(TestFile(cases), 'iota', subproblems=['bonus'])

cases = []
for i in range(10):
    N = (i + 1) * 10000
    cases.append(TestCase(N, list(range(1, N + 1))))
p.add_hidden_test(TestFile(cases), 'iota_large', subproblems=['bonus'])

@p.hidden_test_generator(test_count=4, subproblems=['bonus'])
def pure_random() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        N = random.randint(1, 100000)
        row = [random.randint(1, 10**9) for _ in range(N)]
        test.cases.append(TestCase(N, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['bonus'])
def sorted_asc() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        N = random.randint(1, 100)
        row = sorted(random.randint(1, 10**9) for _ in range(N))
        test.cases.append(TestCase(N, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['bonus'])
def sorted_desc() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        N = random.randint(1, 100)
        row = sorted((random.randint(1, 10**9) for _ in range(N)), reverse=True)
        test.cases.append(TestCase(N, row))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['bonus'])
def all_same() -> TestFile:
    test = TestFile([])
    for _ in range(10):
        N = random.randint(1, 100)
        val = random.randint(1, 10**9)
        test.cases.append(TestCase(N, [val] * N))
    return test

@p.hidden_test_generator(test_count=4, subproblems=['bonus'])
def alternating_large() -> TestFile:
    test = TestFile([])
    for _ in range(3):
        N = random.randint(50000, 100000)
        row = [1 if i % 2 == 0 else 10**9 for i in range(N)]
        test.cases.append(TestCase(N, row))
    return test

def main():
    p.run_cli()

if __name__ == '__main__':
    main()
