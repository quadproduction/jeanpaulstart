import logging

from jeanpaulstart.constants import *

try:
    import winreg
except ImportError: # Python2 compatibility
    try:
        import _winreg as winreg
    except ImportError as e:
        winreg = None
        logging.warning("[win_err_reporting_dialog] : Cannot manipulate Windows Registry (are you on Windows ?)")

TASK_COMMAND = 'win_err_reporting_dialog'


def validate(user_data):
    return OK, ""


def normalize_after_split(splitted):
    return splitted


def apply_(state):
    if winreg is None:
        logging.info("[win_err_reporting_dialog] : Cannot manipulate Windows Registry (are you on Windows ?)")
        return OK

    keyVal = r'Software\Microsoft\Windows\Windows Error Reporting'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
    except:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
    if state == "present":
        winreg.SetValueEx(key, "DontShowUI", 0, winreg.REG_DWORD, 0)
    elif state == "absent":
        winreg.SetValueEx(key, "DontShowUI", 0, winreg.REG_DWORD, 1)
    return OK
