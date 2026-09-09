from copy import deepcopy
import os
from pathlib import Path
from subprocess import call
from jeanpaulstart.constants import *


TASK_COMMAND = 'requirements'


def validate(user_data):
    return OK, ""


def normalize_after_split(splitted):
    normalized = deepcopy(splitted)
    normalized['arguments']['requirements_folder'] = splitted['arguments'].get('requirements_folder', None)
    return normalized


def apply_(name=None, requirements_folder=None, index_url=None, trusted_host=None):
    env_requirements_folder = os.environ.get("REQUIREMENTS_FOLDER", None)
    if not requirements_folder and not env_requirements_folder:
        raise ValueError("requirements_folder must be specified either as an argument or as an environment variable")

    project_path = Path(requirements_folder or env_requirements_folder).as_posix()
    exit_code = call(f"uv sync --project {project_path} --no-install-project --active", shell=True)

    if exit_code == 0:
        return OK

    return exit_code
