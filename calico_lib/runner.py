from collections.abc import Collection, Sequence
from dataclasses import dataclass
import shutil
import subprocess
import sys

# Runs various source files
@dataclass
class Runner:
    run_cmd: Sequence[str]
    compile_cmd: Sequence[str] | None

    def exec_file(self, infile: str):
        with open(infile) as file:
            return subprocess.check_output(self.run_cmd, stdin=file).decode()

    def compile(self):
        if self.compile_cmd is None:
            return
        return subprocess.check_output(self.run_cmd)

def py_runner(src_path: str):
    return Runner([sys.executable, src_path], None)
