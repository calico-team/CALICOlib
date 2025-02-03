#!/usr/bin/env python3

from collections.abc import Collection
from calico_lib import Problem, TestCaseBase, run_py
import random

class TestCase(TestCaseBase):
    def __init__(self, X: int, Y: int) -> None:
        self.X = X
        self.Y = Y
        super().__init__()

    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        p.print_test(self.X, self.Y)

    def verify_case(self, test_sets):
        """Verify the test using assert"""
        assert 1 <= self.X <= 10000
        if 'main' in test_sets:
            assert self.X <= 100

p = Problem[TestCase]('add', time_limit=1, mem_limit=1024000, test_sets=['main', 'bonus'])

@p.test_out_writer
def out_writer(infile: str):
    p.print_test(run_py('submissions/accepted/add_sol.py', infile).decode())

@p.test_validator
def validator(cases: Collection[TestCase]):
    total = 0
    assert len(cases) <= 100
    for case in cases:
        total += case.X + case.Y
    assert total <= 1e6

@p.hidden_test_generator(100, 2, ['main'])
def pure_random(case_num):
    if case_num < 10:
        return TestCase(random.randint(1, 100), random.randint(1, 100))
    return TestCase(random.randint(70, 10000), random.randint(70, 10000))

def main():
    p.add_sample_test([TestCase(4, 7), TestCase(8, 2)])
    p.create_zip()

main()
