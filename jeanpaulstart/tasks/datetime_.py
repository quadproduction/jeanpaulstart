import datetime
from jeanpaulstart import environment
from jeanpaulstart.constants import *


TASK_COMMAND = 'datetime'


def validate(user_data):
    return OK, ""


def normalize_after_split(splitted):
    return splitted


def apply_(format, variable):
    environment.set(variable, datetime.datetime.now().strftime(format))
    return OK
