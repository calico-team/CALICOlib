import requests
import json
# from .problem import Problem
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE_URL = 'https://calicojudge.com/api/v4'

USER = None

CONTEST_ID = -1

def _request(method: str, endpoint: str, data=None, files=None):
    print("Request: " + method + " " + endpoint)
    r = requests.request(method, BASE_URL + endpoint,
                      data=data,
                      files=files,
                      auth=USER)
    print(f'STATUS: {r.status_code}')
    print(f'{r.text[:200]}')
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

def upload_problem_zip(file_name, pid: str|None) -> str:
    data = None
    if pid is None:
        print(f'Creating problem...')
    else:
        print(f'Replacing problem; pid: {pid}...')
        data = {'problem': str(pid), 'color': '#ffffff'}
    r = _request('post',
                 f'/problems',
                 data=data,
                 files={'zip': open(file_name, 'rb')})

    print(f"problem uploaded with pid: {pid}")
    pid = r['problem_id']
    assert pid is not None
    return pid

def unlink_problem_from_contest(pid: str):
    _ = _request('DELETE', f'/contests/{CONTEST_ID}/problems/{pid}')
    print(f'Unlinking problem...')

def link_problem_to_contest(pid: str, label: str, rgb: str):
    # TODO: support points
    """
    {
      "label": "string",
      "color": "string",
      "rgb": "string",
      "points": 1,
      "lazy_eval_results": 0
    }
    """
    data = {
            'label': label,
            'rgb': rgb,
            }
    # data = json.dumps(data)
    print(f'Linking problem... {pid}')
    _ = _request(
            'PUT',
            f'/contests/{CONTEST_ID}/problems/{pid}',
            data = data)
            # files={'data': ('problems.json', data)})
    return

def add_problem_metadata_to_contest(name: str, label: str, rgb: str):
    """DEPRECATED"""
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

def create_contest(cid: str, name: str, start_time: datetime = datetime(2000, 1, 1, 0, 0), duration: str = '9999999:00:00'):
    """
    Creates a contest, check code for parameters used.
    """
    def to_iso8601_pacific(dt: datetime) -> str:
        """Assume input datetime is in Pacific Time and return ISO 8601 string."""
        pacific = ZoneInfo("America/Los_Angeles")
        dt = dt.replace(tzinfo=pacific)
        return dt.isoformat()

    activate_time = start_time - timedelta(minutes=50)
    data = {
            'id': cid,
            'name': name,
            'start_time': to_iso8601_pacific(start_time),
            'duration': duration,
            'penalty_time': 10,
            'activate_time': to_iso8601_pacific(activate_time),
            'scoreboard_freeze_time': '+02:00:00',
            'scoreboard_freeze_duration': '1:00:00',
            }

    data = json.dumps(data)
    print(f'Creating contest {data}')
    r = _request(
            'post',
            '/contests',
            files={'json': ('contest.json', data)})

# r = requests.get(BASE_URL + '/status', auth=USER)

