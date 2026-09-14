#!/usr/bin/env python3

from datetime import datetime
from calico_lib import Contest, run_cli

from gta6.main import p as gta6
from laser.main import p as laser
from grid.main import p as grid

def main():
    problem_list = [
            gta6,
            laser,
            grid,
            ]
    all_branch = [p.problem_name for p in problem_list]
    all_branch.append('multiplication')
    all_branch.append('lecture')


    i = 0
    labels = ['1', '2', '3']
    assert len(labels) == len(problem_list)
    for p in problem_list:
        i += 1
        p.label_prefix = labels[i-1]

    # problem_list = problem_list[4:]

    c = Contest('contest-shortname',
                "Contest Name",
                 # datetime(2025, 11, 9, 4),
                 datetime(2026, 4, 11, 16), # bro it's 16 not 4
                 '3:00:00',
                 problems = problem_list)

    run_cli(c)

main()
