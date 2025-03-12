from .problem import Problem, TestFileBase
from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable
from typing import override

class TestCaseBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def write_test_in(self):
        """Write the input file of this test case using print_test"""
        pass

    @abstractmethod
    def verify_case(self, test_sets):
        pass

class MulticaseTestFile(TestFileBase):
    problem = None

    def __init__(self, cases: Iterable[TestCaseBase]|None = None) -> None:
        if cases is None:
            self.cases: list[TestCaseBase] = []
        else:
            self.cases = list(cases)
        super().__init__()

    # @override
    # def get_subproblems(self) -> list[str]:
    #     return ['bonus']

    @override
    def write_test_in(self):
        assert self.problem != None, "Must set problem for multicase test file"
        self.problem.print_test(len(self.cases))
        for case in self.cases:
            case.write_test_in()
        return super().write_test_in()

#
# class TestFileFromFile(TestFileBase):
#
#     @override
#     def write_test_in(self):
#         return super().write_test_in()
