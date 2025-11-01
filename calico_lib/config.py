
import tomllib

from calico_lib import judge_api

def load_secrets(file_path: str = 'secrets.toml'):
    with open(file_path, 'rb') as f:
        secrets = tomllib.load(f)
    judge_api.set_user(
            (secrets['username'], secrets['password']))
