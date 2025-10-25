import os
import sys
from .contest import Contest
from .judge_api import set_contest_id, set_user
from .problem import Problem
import argparse


def run_cli(obj: Contest|Problem):
    parser = argparse.ArgumentParser(
                    prog='CALICOLib problem CLI',
                    description='CLI interface for various actions for this problem. By default, generates and verifies test cases.',
                    epilog='')

    parser.add_argument('-a', '--auth', help='Username and password for judge, separated by colon.')
    parser.add_argument('-c', '--cid', type=str, help='Add the problem to the contest id.')
    parser.add_argument('-u', '--upload', action='store_true', help='Create or update the problem on the judge. Defaults to a draft version, unless -f is specified.')
    parser.add_argument('-s', '--skip-test-gen', action='store_true', help='Skip test generation.')
    parser.add_argument('-f', '--final', action='store_true', help='Operates on the final version.')
    parser.add_argument('-i', '--p-ord', type=int, help='Problem order.')

    if isinstance(obj, Contest):
        MODES = ['NORMAL', 'ARCHIVE', 'TESTING']
        parser.add_argument(
                '-n', '--create', nargs='?', type=str.upper, choices=MODES, const='TESTING',
                help=f"Create a new contest for this season with type. "
                f"(default: %(default)s)"
                )
        parser.add_argument(
                '-p', '--target-problem', type=str,
                help=f"Operate on a specific problem."
                )

    args = parser.parse_args()
    if isinstance(obj, Contest) and len(sys.argv) == 1:
        parser.print_help()
        return

    if args.create is not None:
        assert isinstance(obj, Contest)
        tag = ''
        if args.create == 'ARCHIVE':
            tag = 'Archive'
        elif args.create == 'TESTING':
            tag = 'Testing'
        obj._create_contest(tag)
        return

    target_problem = None
    if args.target_problem is not None:
        assert isinstance(obj, Contest)
        for i in obj.problems:
            if i.problem_name == args.target_problem:
                target_problem = i
                break
    if isinstance(obj, Problem):
        target_problem = obj

    if args.auth is not None:
        set_user(tuple(args.auth.split(':')))

    if args.cid is not None:
        set_contest_id(args.cid)

    assert target_problem is not None

    os.chdir(target_problem.problem_dir)
    target_problem.init_problem()

    if args.final:
        target_problem.problem_name = target_problem.problem_name
        assert args.p_ord is not None
    else:
        target_problem.problem_name = target_problem.problem_name + '_draft'

    if not args.skip_test_gen:
        if not target_problem.always_skip_test_gen:
            print('\n=== Creating Tests ===')
            target_problem.create_all_tests()

        print('\n=== Creating Zip ===')
        target_problem.create_zip('')

    if args.upload:
        print('=== Uploading Problem Zip ===')
        target_problem.upload()

    if args.cid is not None:
        print('=== Linking to Contest ===')
        if args.p_ord is None:
            target_problem.link_to_contest()
        else:
            target_problem.link_to_contest(args.p_ord)

