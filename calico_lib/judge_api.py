import requests
import json
# from .problem import Problem

BASE_URL = 'https://calicojudge.com/api/v4'

USER = None

CONTEST_ID = 33

def _request(method: str, endpoint: str, data=None, files=None):
    print("Request: " + method + " " + endpoint)
    r = requests.request(method, BASE_URL + endpoint,
                      data=data,
                      files=files,
                      auth=USER)
    print(f'STATUS: {r.status_code}')
    print(f'{r.text}')
    if r.status_code >= 300:
        raise Exception(r.status_code)
    r = r.json()
    print(json.dumps(r, indent=2))
    return r

def set_user(user_password_pair: tuple[str, str]):
    """
    Set the user used for api requests
    """
    global USER
    USER = user_password_pair

def set_contest_id(contest_id: int):
    global CONTEST_ID
    CONTEST_ID = contest_id

def upload_to_testing_contest(problem):
    pass
    # problem_json = json.dumps([problem.default_metadata('main')])
    # print(problem_json)
    # r = requests.post(BASE_URL + '/api/v4/contests/3/problems/add-data',
    #                   files={'data': problem_json}, auth=USER)
    # print(r.text)
    # for s in problem.test_sets:
    #     problem.default_metadata(s.name)

def upload_problem_zip(file_name, pid: int|None):
    data = None
    if pid is None:
        print(f'Creating problem...')
    else:
        print(f'Replacing problem; pid: {pid}...')
        data = {'problem': str(pid), 'color': '#ffffff'}
    r = _request('post',
                 f'/contests/{CONTEST_ID}/problems',
                 data=data,
                 files={'zip': open(file_name, 'rb')})

    print(f"problem uploaded with pid: {pid}")
    pid = r['problem_id']
    return pid

def add_problem_metadata_to_contest(name: str, label: str, rgb: str):
    """Adds the problem metadata, but not the zip"""
    # try:
    #     _request('delete', f'/contests/{CONTEST_ID}/problems/{pid}')
    # except Exception as e:
    #     print("delete failed: " + str(e))
    data = [{
            'id': name,
            'label': label,
            'rgb': rgb,
            }]
    data = json.dumps(data)
    print(f'Adding problem metadata {data}')
    r = _request(
            'post',
            f'/contests/{CONTEST_ID}/problems/add-data',
            # data = {'problem': str(pid)},
            files={'data': ('problems.json', data)})
    assert len(r) == 1
    return r[0]


# r = requests.get(BASE_URL + '/status', auth=USER)

