from .problem import Problem, TestFileBase
from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable
# from typing import override

class TestCaseBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def write_test_in(self) -> str:
        """Return the input text for this test case."""
        pass

    @abstractmethod
    def verify_case(self, test_sets):
        pass

class MulticaseTestFile(TestFileBase):
    def __init__(self, cases: Iterable[TestCaseBase]|None = None) -> None:
        if cases is None:
            self.cases: list[TestCaseBase] = []
        else:
            self.cases = list(cases)
        super().__init__()

    def write_test_in(self) -> str:
        # TODO: settle the multicase return-string contract and verify_case naming.
        lines = [str(len(self.cases))]
        for case in self.cases:
            lines.append(case.write_test_in())
        return "\n".join(lines) + "\n"

#
# class TestFileFromFile(TestFileBase):
#
#     @override
#     def write_test_in(self):
#         return super().write_test_in()
