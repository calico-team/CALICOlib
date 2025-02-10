#!/usr/bin/env python3

from collections.abc import Collection
from typing import override
from calico_lib import Problem, run_py, TestFileBase
import random

class TestCase():
    def __init__(self, X: int, Y: int) -> None:
        self.X = X
        self.Y = Y
        super().__init__()

    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        p.print_test(self.X, self.Y)

    def verify_case(self, test_sets):
        assert 1 <= self.X <= 10000
        if 'main' in test_sets:
            assert self.X <= 100

# TODO: move this to library
class Test(TestFileBase):
    def __init__(self, cases: list[TestCase]|None = None) -> None:
        self.cases: list[TestCase] = []
        if cases is not None:
            self.cases = cases
        super().__init__()

    @override
    def get_subproblems(self) -> list[str]:
        return ['bonus']

    @override
    def write_test_in(self):
        p.print_test(len(self.cases))
        for case in self.cases:
            case.write_test_in()
        return super().write_test_in()

    @override
    def write_test_out(self, infile: str):
        p.print_test(run_py('submissions/accepted/add_sol.py', infile).decode())

    @override
    def validate_test_in(self, infile: str):
        """Verify the test using assert (not recommended, consider properly
        verifying by reading the file)."""
        total = 0
        assert 1 <= len(self.cases) <= 100, f"Got {len(self.cases)} cases"
        for case in self.cases:
            case.verify_case(self.get_subproblems())
            total += case.X + case.Y
        assert total <= 1e6

p = Problem[Test](
        'add',
        test_sets=['main', 'bonus'])

p.add_sample_test(Test([
    TestCase(4, 7),
    TestCase(1, 23),
    TestCase(9, 8),
    TestCase(1, 1),
    ]))

@p.hidden_test_generator(test_count=2, subproblems=['main'])
def pure_random():
    test = Test()
    for i in range(100):
        if i < 10:
            test.cases.append(TestCase(random.randint(1, 100), random.randint(1, 100)))
        else:
            test.cases.append(TestCase(random.randint(70, 10000), random.randint(70, 10000)))
    return test

print(len(pure_random().cases))
print(len(pure_random().cases))

@p.hidden_test_generator(test_count=2, subproblems=['main'])
def pure_random2():
    return Test([TestCase(random.randint(70, 1000), random.randint(5, 10))])

def main():
    # p.run_cli()
    p.create_all_tests()
    # p.create_zip()

main()
