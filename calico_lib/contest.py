import argparse
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal

from .judge_api import create_contest, set_contest_id
from .problem import Problem
from calico_lib import judge_api

@dataclass
class Contest():
    contest_id: str
    name: str
    start_time: datetime = datetime(2000, 1, 1, 0, 0)
    duration: str = '9999999:00:00'
    problems: List[Problem] = field(default_factory=list)

    def create_contest(self):
        create_contest(self.contest_id, self.name, self.start_time, self.duration)
        print('=======================')
        print('TODO: make the contest private, not available for all teams, and add the appropriate groups.')
        print('=======================')

def link_external_problem(cid, pid, label, rank):
    rank_color_map = {
            1: '#e9e4d7',
            2: '#ff7e34',
            3: '#995d59',
            4: '#000000',
            }
    set_contest_id(cid)
    judge_api.link_problem_to_contest(pid, label, rank_color_map[rank])
