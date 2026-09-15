from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from calico_lib import judge_api

from .judge_api import create_contest, set_contest_id
from .problem import RANK_COLOR_MAP, Problem


@dataclass
class Contest:
    contest_id: str
    name: str
    start_time: datetime = datetime(2000, 1, 1, 0, 0, tzinfo=ZoneInfo('America/Los_Angeles'))
    duration: str = '9999999:00:00'
    problems: list[Problem] = field(default_factory=list)

    def create_contest(self):
        create_contest(self.contest_id, self.name, self.start_time, self.duration)
        print('=======================')
        print('TODO: make the contest private, not available for all teams, and add the appropriate groups.')
        print('=======================')

def link_external_problem(cid, pid, label, rank):
    set_contest_id(cid)
    judge_api.link_problem_to_contest(pid, label, RANK_COLOR_MAP[rank])
