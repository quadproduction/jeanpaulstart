from os import system
from subprocess import Popen, call
from jeanpaulstart.constants import *


TASK_COMMAND = 'raw'


def validate(user_data):
    return OK, ""


def normalize_after_split(splitted):
    normalized = dict(splitted)
    normalized['arguments']['async_'] = splitted['arguments'].get('async_', splitted['arguments'].pop('async', True))
    normalized['arguments']['open_terminal'] = splitted['arguments'].get('open_terminal', False)
    return normalized


def apply_(async_, command, open_terminal):
    if async_:
        if open_terminal:
            command = "start cmd /k " + command
            status = system(command)
        else:
            Popen(command, shell=True, close_fds=True)
            status = OK
    else:
        status = call(command, shell=True)

    if str(status) == "0":
        return OK

    return status
