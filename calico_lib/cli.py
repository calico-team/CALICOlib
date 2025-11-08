import os
import sys

from calico_lib.config import load_secrets, load_configs
from .contest import Contest
from .judge_api import set_contest_id, set_user
from .problem import Problem
import argparse


def run_cli(obj: Contest|Problem):
    desc = 'CLI interface for various actions for this problem. '\
            'By default, generates and verifies test cases.'
    if isinstance(obj, Contest):
        desc = 'CLI interface for various actions for this contest. '\
                'Similar to problem CLI, but operates on all problems, or a specific one.'
    parser = argparse.ArgumentParser(
                    prog='CALICOLib CLI',
                    description=desc,
                    epilog='')

    parser.add_argument('-a', '--auth', help='Username and password for judge, separated by colon.')
    parser.add_argument('-c', '--cid', type=str, help='Link the problem to the contest id.')
    parser.add_argument('-u', '--upload', action='store_true', help='Create or update the problem on the judge. Defaults to a draft version, unless -f is specified.')
    parser.add_argument('-s', '--skip-test-gen', action='store_true', help='Skip test generation.')
    parser.add_argument('-f', '--final', action='store_true', help='Don\'t append _draft to the problem id.')
    # parser.add_argument('-i', '--p-ord', type=int, help='Problem order.')

    try:
        if isinstance(obj, Contest):
            load_secrets()
            set_contest_id(obj.contest_id)
        elif isinstance(obj, Problem):
            load_secrets('../secrets.toml')
            load_configs('../config.toml')
    except Exception as e:
        print('Warning: unable to load some configs...' + str(e))

    if isinstance(obj, Contest):
        parser.add_argument(
                '-n', '--create', action='store_true',
                help=f"Create the contest."
                )
        parser.add_argument(
                '-p', '--target-problem', type=str,
                help=f"Operate on a specific problem."
                )

    args = parser.parse_args()
    if isinstance(obj, Contest) and len(sys.argv) == 1:
        parser.print_help()
        return

    if isinstance(obj, Contest) and args.create:
        obj.create_contest()
        return

    target_problems = None
    if isinstance(obj, Problem):
        target_problems = [obj]
    elif args.target_problem is not None:
        assert isinstance(obj, Contest)
        for i in obj.problems:
            if i.problem_name == args.target_problem:
                target_problems = [i]
                break

    else:
        target_problems = obj.problems

    if args.auth is not None:
        set_user(tuple(args.auth.split(':')))

    assert target_problems is not None

    for target_problem in target_problems:
        print(f'---> Operating on {target_problem.problem_name}')
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
            set_contest_id(args.cid)
            if args.p_ord is None:
                target_problem.link_to_contest()
            else:
                target_problem.link_to_contest(args.p_ord)

Problem._cli_func = run_cli
