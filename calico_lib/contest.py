from enum import Enum
from typing import Literal, NamedTuple

from calico_lib.judge_api import create_contest

class Contest(NamedTuple):
    quarter: Literal['fa']|Literal['sp']
    year: str

    def _create_contest(self, tag = ''):
        cid = 'calico-' + self.quarter + self.year + '-' + tag.lower()
        quarter_long = 'Fall' if self.quarter == 'fa' else 'Spring'
        tag_str = '' if len(tag) == 0 else '[' + tag + '] '
        name = tag_str + 'CALICO ' +  quarter_long + ' \'' + self.year
        create_contest(cid, name)
        print('=======================')
        print('TODO: make the contest private, not available for all teams, and add the appropriate groups.')
        print('=======================')

    def create_testing_contest(self):
        self._create_contest('Testing')

    def create_actual_contest(self):
        self._create_contest()

    def create_archive_contest(self):
        self._create_contest('Archive')
