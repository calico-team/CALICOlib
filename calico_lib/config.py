
import tomllib

from calico_lib import judge_api

def load_secrets(file_path: str = 'secrets.toml'):
    with open(file_path, 'rb') as f:
        secrets = tomllib.load(f)
    judge_api.set_user(
            (secrets['username'], secrets['password']))

def load_configs(file_path: str = 'config.toml'):
    with open(file_path, 'rb') as f:
        config = tomllib.load(f)
    judge_api.set_contest_id(config['default_contest_id'])
