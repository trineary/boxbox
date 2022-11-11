import yaml
import os
import sys
dir_path = os.getcwd()
sys.path.append(dir_path)


def get_config(config_filepath: str) -> dict:
    with open(config_filepath) as f:
        config = yaml.safe_load(f)
    return config

