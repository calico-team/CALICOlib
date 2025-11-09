
import tomllib

from calico_lib import judge_api

def try_load_toml(file_path):
    try:
        with open(file_path, 'rb') as f:
            toml = tomllib.load(f)
            return toml
    except Exception as e:
        print('Warning: unable to load some configs...' + str(e))
        return None


def load_secrets(file_path: str = 'secrets.toml'):
    secrets = try_load_toml(file_path)
    if secrets is None:
        return
    judge_api.set_user(
            (secrets['username'], secrets['password']))

def load_configs(file_path: str = 'config.toml'):
    config = try_load_toml(file_path)
    if config is None:
        return
    with open(file_path, 'rb') as f:
        config = tomllib.load(f)
    judge_api.set_contest_id(config['default_contest_id'])
