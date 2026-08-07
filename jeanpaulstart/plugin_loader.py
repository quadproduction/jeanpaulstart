import os
import sys
import logging
import importlib.util
from glob import glob
from collections import OrderedDict
from .constants import *


loaded_plugins = OrderedDict()


class Loader(object):

    def __init__(self, plugin_folder):
         self.plugin_folder = plugin_folder

    def __repr__(self):
        return "Loader(folder={folder})".format(folder=self.plugin_folder)

    def list_names(self):
        search_path = os.path.join(self.plugin_folder, "*.py")
        files = glob(search_path)
        names = sorted([os.path.splitext(os.path.basename(file_))[0] for file_ in files])
        try:
            names.remove('__init__')
        except ValueError:
            pass

        logging.info("Listed {count:03d} plugins".format(count=len(names)))

        return names

    def make_plugin_filepath(self, plugin_name):
        return os.path.join(self.plugin_folder, plugin_name + '.py').replace('\\', '/')

    def load_by_filepath(self, plugin_filepath):
        if not os.path.isfile(plugin_filepath):
            return None

        name = os.path.splitext(os.path.basename(plugin_filepath))[0]
        spec = importlib.util.spec_from_file_location(name, plugin_filepath)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        write_bytecode = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = write_bytecode

        return module

    def load_by_name(self, plugin_name):
        plugin_filepath = self.make_plugin_filepath(plugin_name)
        return self.load_by_filepath(plugin_filepath)

    def load(self, plugin_name=None, plugin_filepath=None):
        if plugin_name:
            return self.load_by_name(plugin_name)

        if plugin_filepath:
            return self.load_by_filepath(plugin_filepath)

    def validate(self, plugin):
        if not hasattr(plugin, "TASK_COMMAND"):
            return PLUG_COMMAND_MISSING

        if not isinstance(plugin.TASK_COMMAND, str):
            return PLUG_COMMAND_NOT_STR

        if not hasattr(plugin, "validate"):
            return PLUG_VALIDATE_MISSING

        if not hasattr(plugin, "normalize_after_split"):
            return PLUG_NORMALIZE_MISSING

        if not hasattr(plugin, "apply_"):
            return PLUG_APPLY_MISSING

        return OK

    def load_all(self):
        plugins = OrderedDict()

        for plugin_name in self.list_names():

            plugin = self.load(plugin_name=plugin_name)
            status = self.validate(plugin)

            if status != OK:
                logging.warning("Could not validate plugin : '{plugin_name}.py' ({status})".format(
                    plugin_name=plugin_name,
                    status=status
                ))
                continue

            command_name = plugin.TASK_COMMAND

            if command_name in plugins:
                logging.warning("Skipping plugin '{plugin_name}.py' : command '{command_name}' already loaded".format(
                    plugin_name=plugin_name,
                    command_name=command_name
                ))
                continue

            plugins[command_name] = plugin

            logging.info("Successfully loaded plugin : '{plugin_name}.py'".format(plugin_name=plugin_name))

        return plugins


def init(plugin_folder=None, force=False):
    global loaded_plugins

    if plugin_folder is None:
        plugin_folder = os.path.expandvars('$PLUGIN_FOLDER')

    if plugin_folder == "$PLUGIN_FOLDER":
        from . import tasks
        plugin_folder=os.path.dirname(tasks.__file__)

    if loaded_plugins and not force:
        return False

    logging.info("Initializing plugins from {}".format(plugin_folder))

    loader = Loader(plugin_folder=plugin_folder)
    loaded_plugins = loader.load_all()

    return True
