import argparse
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


def run_contest_cli(self):
    parser = argparse.ArgumentParser(
            prog='CALICO contest creation CLI',
            description='CLI to create contest. Actually, it\'s just for auth',
            epilog='')

    MODES = ['NORMAL', 'ARCHIVE', 'TESTING']
    parser.add_argument(
            '-n', '--create', type=str.upper, choices=MODES, default='TESTING',
            help=f"Create a new contest for this season with type. "
            f"(default: %(default)s)"
            )

    args = parser.parse_args()
    if args.create is not None:
        tag = ''
        if args.create == 'ARCHIVE':
            tag = 'Archive'
        elif args.create == 'TESTING':
            tag = 'Testing'
        self._create_contest(tag)

