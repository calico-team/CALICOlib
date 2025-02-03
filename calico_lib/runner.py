import shutil
import subprocess
import sys

# Runs various source files

def run_py(src_path: str, infile: str):
    print(f'running python file "{src_path}" with stdin "{infile}"')
    with open(infile) as file:
        return subprocess.check_output([sys.executable, src_path], stdin=file)
