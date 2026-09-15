"""Experimental multicase test support.

``TestCaseBase`` and ``MulticaseTestFile`` are exported but experimental: their
contract is not settled and should not be relied on for 1.0. Open questions:

- **Case-text contract.** ``TestCaseBase.write_test_in`` returns one case's
text, which ``MulticaseTestFile`` concatenates after a leading case count. It
is undefined whether a case returns one line, several lines, or a trailing
newline; multi-line cases happen to work, but a trailing newline would corrupt
the join. Pick and document one rule (e.g. "a case returns its lines joined,
with no trailing newline").
- **``verify_case`` is a dead hook.** ``TestCaseBase`` requires
``verify_case(self, test_sets)``, but nothing in the library ever calls it:
``MulticaseTestFile`` only implements ``write_test_in`` and inherits
``validate_test_in`` as abstract. Either wire it in (have ``validate_test_in``
loop the cases) or drop it.
- **Naming.** ``verify_case`` vs ``validate_test_in`` is inconsistent, and
``test_sets`` is an odd parameter name and type.

TODO(multicase): settle the above before this leaves experimental status.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .problem import TestFileBase

# from typing import override

class TestCaseBase(ABC):
    """Experimental: one case inside a ``MulticaseTestFile``. See module docstring."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def write_test_in(self) -> str:
        """Return the input text for this case (contract unsettled)."""

    @abstractmethod
    def verify_case(self, test_sets):
        """Validate this case. Not called by the library yet."""

class MulticaseTestFile(TestFileBase):
    """Experimental: a test file made of N repeated cases. See module docstring."""

    def __init__(self, cases: Iterable[TestCaseBase]|None = None) -> None:
        if cases is None:
            self.cases: list[TestCaseBase] = []
        else:
            self.cases = list(cases)
        super().__init__()

    def write_test_in(self) -> str:
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
