import requests
import json

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

def upload_problem_zip(file_name, problem_id: int|None =None):
    print(f'Uploading problem zip {file_name}...')
    r = requests.post(BASE_URL + '/problems', files={'zip': open('unlockmanifolds_main.zip', 'rb')}, auth=USER)
    print(f"STATUS: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

# r = requests.get(BASE_URL + '/contests/3/problems', auth=('ejam', 'UaLgMZtr8PavGby'))
# r = requests.get(BASE_URL + '/status', auth=('ejam', 'UaLgMZtr8PavGby'))
# print(r.text)


# print(r.text)

