import requests
import json

BASE_URL = 'https://calicojudge.com/api/v4'

def upload_problem_zip(file_name, problem_id):
    print(f'Uploading problem zip {file_name}...')
    r = requests.post(BASE_URL + '/problems', files={'zip': open('unlockmanifolds_main.zip', 'rb')}, auth=('ejam', 'UaLgMZtr8PavGby'))
    print(json.dumps(r.json(), indent=2))
    print(r.text)

# r = requests.get(BASE_URL + '/contests/3/problems', auth=('ejam', 'UaLgMZtr8PavGby'))
# r = requests.get(BASE_URL + '/status', auth=('ejam', 'UaLgMZtr8PavGby'))
# print(r.text)


# print(r.text)

