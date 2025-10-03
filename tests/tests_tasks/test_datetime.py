import datetime
import unittest
from copy import deepcopy
from jeanpaulstart.constants import *
from jeanpaulstart.tasks import datetime_


USER_DATA = {
    'name': 'Task Name',
    'datetime': {
        'variable': 'VARIABLE',
        'format': '%y%m%d'
    }
}


SPLITTED = {
    'name': 'Task Name',
    'command': 'datetime',
    'arguments': {
        'variable': 'VARIABLE',
        'format': '%y%m%d'
    }
}


class MockEnvironment(object):
    def set(self, name, value):
        self.set_env_variable_called = name, value


class TestTaskDatetime(unittest.TestCase):

    def setUp(self):
        self.backup_environment = datetime_.environment
        self.mock_environment = MockEnvironment()
        datetime_.environment = self.mock_environment

    def tearDown(self):
        datetime_.environment = self.backup_environment

    def test_validate(self):
        status, message = datetime_.validate(USER_DATA)
        self.assertEqual(
            status,
            OK
        )

    def test_normalize(self):
        normalized = datetime_.normalize_after_split(deepcopy(SPLITTED))

        self.assertDictEqual(
            normalized,
            SPLITTED
        )

    def test_apply_(self):
        status = datetime_.apply_(variable="VARIABLE", format="%y%m%d")

        self.assertEqual(
            self.mock_environment.set_env_variable_called,
            ("VARIABLE", datetime.datetime.now().strftime('%y%m%d'))
        )
        self.assertEqual(
            status,
            OK
        )
