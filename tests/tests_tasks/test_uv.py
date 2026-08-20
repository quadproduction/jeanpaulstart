import os
import unittest
from copy import deepcopy

from jeanpaulstart.batch import validator
from jeanpaulstart.constants import *
from jeanpaulstart.tasks import uv


USER_DATA = {
    'name': 'Task Name',
    'uv': {
        'name': 'launcher'
    }
}


SPLITTED = {
    'name': 'Task Name',
    'command': 'uv',
    'arguments': {
        'name': 'launcher',
        'state': STATE_PRESENT
    }
}


class _MockProcess(object):
    def __init__(self, returncode):
        self.returncode = returncode


class TestTaskUv(unittest.TestCase):

    def _mock_run(self, command):
        self._mock_run_called = command
        return _MockProcess(0)

    def setUp(self):
        self._mock_run_called = None
        self._mock_installed_version = None

        self.backup_run = uv.subprocess.run
        self.backup_get_installed_version = uv.get_installed_version
        self.backup_tool_version = os.environ.get('JPS_TOOL_VERSION')

        uv.subprocess.run = self._mock_run
        uv.get_installed_version = lambda name: self._mock_installed_version
        os.environ.pop('JPS_TOOL_VERSION', None)

    def tearDown(self):
        uv.subprocess.run = self.backup_run
        uv.get_installed_version = self.backup_get_installed_version

        if self.backup_tool_version is None:
            os.environ.pop('JPS_TOOL_VERSION', None)
        else:
            os.environ['JPS_TOOL_VERSION'] = self.backup_tool_version

    def test_validate(self):
        status, message = uv.validate(USER_DATA)
        self.assertEqual(status, validator.OK)

    def test_normalize_without_state(self):
        expected = deepcopy(SPLITTED)
        expected['arguments']['state'] = STATE_PRESENT
        expected['arguments']['refresh_index'] = False

        normalized = uv.normalize_after_split(deepcopy(SPLITTED))

        self.assertDictEqual(normalized, expected)

    def test_apply_present(self):
        status = uv.apply_(name="launcher", state=uv.STATE_PRESENT)

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "install", "launcher"]
        )
        self.assertEqual(status, OK)

    def test_apply_present_with_version(self):
        status = uv.apply_(name="launcher", state=uv.STATE_PRESENT, version="1.2.3")

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "install", "launcher==1.2.3"]
        )
        self.assertEqual(status, OK)

    def test_apply_present_uses_environment_version(self):
        os.environ['JPS_TOOL_VERSION'] = "2.0.0"

        status = uv.apply_(name="launcher", state=uv.STATE_PRESENT)

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "install", "launcher==2.0.0"]
        )
        self.assertEqual(status, OK)

    def test_apply_absent(self):
        status = uv.apply_(name="launcher", state=uv.STATE_ABSENT)

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "uninstall", "launcher"]
        )
        self.assertEqual(status, OK)

    def test_apply_force_reinstall_without_version(self):
        status = uv.apply_(name="launcher", state=uv.STATE_FORCE_REINSTALL)

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "install", "launcher", "--reinstall", "--upgrade"]
        )
        self.assertEqual(status, OK)

    def test_apply_force_reinstall_with_version(self):
        status = uv.apply_(name="launcher", state=uv.STATE_FORCE_REINSTALL, version="1.2.3")

        self.assertEqual(
            self._mock_run_called,
            ["uv", "pip", "install", "launcher==1.2.3", "--reinstall"]
        )
        self.assertEqual(status, OK)

    def test_apply_adds_index_and_refresh(self):
        status = uv.apply_(
            name="launcher",
            state=uv.STATE_PRESENT,
            index_url="http://localhost:8080/simple",
            refresh_index=True
        )

        self.assertEqual(
            self._mock_run_called,
            [
                "uv",
                "pip",
                "install",
                "launcher",
                "--refresh",
                "--index-url",
                "http://localhost:8080/simple"
            ]
        )
        self.assertEqual(status, OK)

    def test_apply_skips_when_same_version_is_installed(self):
        self._mock_installed_version = "1.2.3"

        status = uv.apply_(name="launcher", state=uv.STATE_PRESENT, version="1.2.3")

        self.assertIsNone(self._mock_run_called)
        self.assertEqual(status, OK)
