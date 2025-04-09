import requests
import json
# from .problem import Problem

BASE_URL = 'https://calicojudge.com/api/v4'

USER = None

# TODO:
# judge.lock: contains problemid on the judge
# check if problem exists
# error check

# def _post()

def set_user(user_password_pair: tuple[str, str]):
    """
    Set the user used for api requests
    """
    global USER
    USER = user_password_pair

def upload_to_testing_contest(problem):
    pass
    # problem_json = json.dumps([problem.default_metadata('main')])
    # print(problem_json)
    # r = requests.post(BASE_URL + '/api/v4/contests/3/problems/add-data',
    #                   files={'data': problem_json}, auth=USER)
    # print(r.text)
    # for s in problem.test_sets:
    #     problem.default_metadata(s.name)

def upload_problem_zip(file_name) -> int|None:
    print('Creating new problem...')
    r = requests.post(BASE_URL + '/contests/3/problems', files={'zip': open(file_name, 'rb')}, auth=USER)
    print(f'STATUS: {r.status_code}')
    print(f'{r.text}')
    if r.status_code == 401:
        print('UNAUTHORIZED')
        return
    result = r.json()
    print(json.dumps(result, indent=2))
    if r.status_code != 200:
        print('FAILED')
        return
    pid = result['problem_id']
    if (r.status_code == 200):
        print(f"New problem created with pid: {pid}")
    return pid

def replace_problem_zip(file_name, pid: int):
    print(f'Replacing problem; pid: {pid}...')
    r = requests.post(BASE_URL + '/contests/3/problems', files={'zip': open(file_name, 'rb')}, auth=USER)
    print(f'STATUS: {r.status_code}')
    print(f'{r.text}')
    if r.status_code == 401:
        print('UNAUTHORIZED')
        return
    result = r.json()
    print(json.dumps(result, indent=2))
    pid = result['problem_id']
    if (r.status_code == 200):
        print(f"new problem created with pid: {pid}")

# r = requests.get(BASE_URL + '/contests/3/problems', auth=('ejam', 'UaLgMZtr8PavGby'))
# r = requests.get(BASE_URL + '/status', auth=('ejam', 'UaLgMZtr8PavGby'))
# print(r.text)


# print(r.text)

