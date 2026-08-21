import os
import re
from loguru import logger
from packaging.version import Version
from jeanpaulstart import parser
from jeanpaulstart.constants import *
from jeanpaulstart.environment import parse
from jeanpaulstart.file_io import norm_slashes
from .validator import validate
from .normalizer import normalize


class Batch(object):
    """
    Object holding tasks to be run

    Member `load_status` defaults to `BATCH_NOT_LOADED`
    Member `name` defaults to "Unnamed batch"
    Member `tags`
    Member `tasks`
    """
    def __init__(self, data=None, source=None, filepath=None):
        self.name = "Unnamed batch"

        if data is not None:
            logger.info('New batch from data')
            self._data = data

        elif source is not None:
            logger.info('New batch from source')
            self._data = parser.parse(source)

        elif filepath is not None:
            filepath = norm_slashes(filepath)
            logger.info("New batch from file {}", filepath)
            self._data = parser.from_file(filepath)

        self.load_status = BATCH_NOT_LOADED
        self.icon_path = ""
        self.version = None
        self.staging_folder = None
        self.stagings = None
        self.old_versions = list()
        self.tags = list()
        self.options = list()
        self.tasks = list()

        self._load()

    def __repr__(self):
        return "Batch(name='{name}', tags={tags}, load_status={status}, tasks={tasks_count})".format(
            name=self.name,
            tags=self.tags,
            status=self.load_status,
            tasks_count=len(self.tasks)
        )

    def _load(self):
        """
        Validates and normalizes Batch data
        Updates member `loaded_status` with `OK`, `BATCH_NO_DATA`, `BATCH_NOT_VALID` or `BATCH_NOT_NORMALIZED`
        :return: None
        """
        if self._data is None:
            logger.info('No data was found')
            self.load_status = BATCH_NO_DATA
            return

        status, message = validate(self._data)

        if status != OK:
            logger.info("Validation failed : {}", message)
            self.load_status = BATCH_NOT_VALID
            return

        self.name = self._data['name']
        self.icon_path = parse(self._data.get('icon_path'))
        self.description = self._data.get('description')
        self.options = self._create_options()
        self.option_mandatory = self._data.get('option_mandatory', True) and bool(self.options)
        self._find_versions()
        self._find_stagings()
        tags, tasks, status = normalize(self._data)

        if status != OK:
            logger.info('Batch normalization failed')
            self.load_status = BATCH_NOT_NORMALIZED
            return

        self.tags = tags
        self.tasks = tasks
        self.load_status = OK

    def _create_options(self):
        options = list()
        if self._data.get('options') is not None:
            for option_data in self._data.get('options'):
                batch_option = _BatchOption(option_data)
                if batch_option.load_status == OK:
                    options.append(batch_option)
        return options

    def _find_versions(self):
        """ Find all version folders in the version folder"""
        versions_regex = self._data.get('version_regex', SEMVER_REGEX)
        re_folder = re.compile(versions_regex)
        versions = list()
        versions_folder = self._data.get('version_folder', "")
        if versions_folder == "":
            return
        if not os.path.exists(versions_folder):
            logger.warning("Can't found version folder {}", versions_folder)
            return
        for folder in os.listdir(versions_folder):
            # if not os.path.isdir(os.path.join(versions_folder, folder)):
            #     continue
            match = re_folder.match(folder)
            if match:
                versions.append(match.group("version"))
        if not versions:
            logger.warning("no version folder found in {}", versions_folder)
            return
        versions.sort(reverse=True, key=Version)
        self.version = versions.pop(0)
        self.old_versions = versions

    def _find_stagings(self):
        """ Find all staging folders in the staging folder"""
        staging_folder = self._data.get('staging_folder', "")
        if staging_folder == "":
            return
        self.stagings = []
        self.staging_folder = staging_folder
        if not os.path.exists(staging_folder):
            logger.debug("Can't found staging folder {}", staging_folder)
            return
        for folder in os.listdir(staging_folder):
            if not os.path.isdir(os.path.join(staging_folder, folder)):
                continue
            self.stagings.append(folder)
        if not self.stagings:
            logger.debug("no staging folder found in {}", staging_folder)


class _BatchOption(object):
    def __init__(self, data=None):
        self.name = "Unknown"
        self.load_status = BATCH_NOT_LOADED
        self.tags = list()

        if data is not None:
            self._data = data

        self._load()

    def _load(self):
        if self._data is None:
            self.load_status = BATCH_NO_DATA
            return

        self.name = self._data['name']
        if not self._data.get('tags'):
            self._data['tags'] = []
        tags, tasks, status = normalize(self._data)
        self.tags = tags
        self.tasks = tasks
        
        self.load_status = OK if status == OK else BATCH_NOT_NORMALIZED
