from collections.abc import Collection, Sequence
from dataclasses import dataclass
import os
import shutil
import subprocess
import sys


CC: str = 'g++'

def configure_cpp_cc(cmd):
    global CC
    CC = cmd

# Runs various source files
@dataclass
class Runner:
    run_cmd: Sequence[str]
    compile_cmd: Sequence[str] | None = None

    def exec(self):
        return subprocess.check_output(self.run_cmd).decode()

    def exec_file(self, infile: str):
        with open(infile, encoding='utf-8', newline='\n') as file:
            return subprocess.check_output(self.run_cmd, stdin=file, encoding='utf-8')

    def compile(self):
        if self.compile_cmd is None:
            return
        return subprocess.check_output(self.compile_cmd).decode()

def py_runner(src_path: str):
    return Runner([sys.executable, src_path], None)

def cpp_runner(src_path: str, bin_name: str):
    return Runner(
            [bin_name],
            [CC, '-Wall', '-Wshadow', '-Wextra', '-O2', '-Wl,-z,stack-size=268435456', '-o', bin_name, src_path]
            )
