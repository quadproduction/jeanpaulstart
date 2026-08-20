from copy import deepcopy
import os
import re
import subprocess
from loguru import logger
import urllib.request
from importlib.metadata import version, PackageNotFoundError
from packaging.version import Version
from packaging.utils import parse_wheel_filename, parse_sdist_filename


from jeanpaulstart.constants import *


TASK_COMMAND = 'uv'


def validate(user_data):
    return OK, ""


def normalize_after_split(splitted):
    normalized = deepcopy(splitted)
    normalized['arguments']['state'] = splitted['arguments'].get('state', STATE_PRESENT)
    normalized['arguments']['refresh_index'] = splitted['arguments'].get('refresh_index', False)
    return normalized


def _extract_files_names_from_url(url):
    with urllib.request.urlopen(url) as r:
        html = r.read().decode()
 
    return re.findall(r'href="[^"]+/([^/#"]+\.(?:whl|tar\.gz))', html)


def get_installed_version(package: str) -> Version | None:
    try:
        return Version(version(package))
    except PackageNotFoundError:
        return None


def get_latest_version(package: str, index_url: str = None) -> Version | None:
    base = (index_url or "https://pypi.org/simple").rstrip("/")
    filenames = _extract_files_names_from_url(f"{base}/{package}/")

    versions = set()
    for filename in filenames:
        try:
            if filename.endswith(".whl"):
                _, ver, _, _ = parse_wheel_filename(filename)
            else:
                _, ver = parse_sdist_filename(filename)
            versions.add(ver)
        except Exception:
            pass

    return max(versions) if versions else None


def get_targeted_or_latest_version(
    package: str, 
    requested: str | None = None, 
    index_url: str = None
) -> Version:
    return Version(requested) if requested else get_latest_version(package, index_url)


def apply_(name, state, version=None, index_url=None, refresh_index=False):
    version = version or os.environ.get('JPS_TOOL_VERSION', None)
    target = Version(version) if version else get_latest_version(name, index_url)
    if not target:
        logger.warning(f"Package named '{name}' not found in the index. Skipping installation.")
        return

    installed = get_installed_version(name)
    force_reinstall = state == STATE_FORCE_REINSTALL

    if target == installed and not force_reinstall:
        logger.info(f"{name} is already installed in version {installed}, nothing to do.")
        return OK

    logger.info(
        f"Installation of {name} in version {target}" if installed else
        f"Update of {name} from {installed} to {target}"
    )

    command = ["uv", "pip", "install", f"{name}=={target}"]    
    if refresh_index:
        command.append('--refresh')
    if index_url:
        command.extend(["--index-url", index_url])

    logger.info(' '.join(command))
    returncode = subprocess.run(command).returncode

    if returncode == 0:
        return OK

    return returncode
