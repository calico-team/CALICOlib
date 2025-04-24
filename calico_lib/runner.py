from collections.abc import Collection, Sequence
from dataclasses import dataclass
import os
import shutil
import subprocess
import sys


CC: str = 'g++'

_ALL_EXECUTABLES: list['Runner'] = []

def configure_cpp_cc(cmd):
    global CC
    CC = cmd

# Runs various source files
@dataclass
class Runner:
    run_cmd: Sequence[str]
    compile_cmd: Sequence[str] | None = None

    def __init__(self, run_cmd, compile_cmd):
        self.run_cmd = run_cmd
        self.compile_cmd = compile_cmd
        _ALL_EXECUTABLES.append(self)

    def exec(self):
        try:
            out = subprocess.check_output(self.run_cmd).decode()
        except subprocess.CalledProcessError:
            print(f'Runner failed to run:')
            print(self)
            exit(1)
        return out

    def exec_file(self, infile: str):
        with open(infile, encoding='utf-8', newline='\n') as file:
            try:
                out = subprocess.check_output(self.run_cmd, stdin=file, encoding='utf-8')
            except subprocess.CalledProcessError:
                print(f'Runner failed to run:')
                print(self)
                exit(1)
            return out

    def compile(self):
        if self.compile_cmd is None:
            return
        return subprocess.check_output(self.compile_cmd).decode()

def py_runner(src_path: str):
    return Runner([sys.executable, src_path], None)

def cpp_runner(src_path: str, bin_name: str):
    if bin_name[0] != '/':
        bin_name = './' + bin_name
    return Runner(
            [bin_name],
            [CC, '-Wall', '-Wshadow', '-Wextra', '-O2', '-Wl,-z,stack-size=268435456', '-o', bin_name, src_path]
            )

def compile_all():
    for runner in _ALL_EXECUTABLES:
        runner.compile()

