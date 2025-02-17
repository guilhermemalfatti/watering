from importlib import import_module
import os
from plugins.plugin_interface import PluginInterface
import importlib


def load_plugins(plugin_dir):
    # plugin_dir = os.path.join(os.path.dirname(__file__), '/')
    plugins = {}
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and filename != '__init__.py' and filename != 'plugin_interface.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'plugins.{module_name}')
            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, PluginInterface) and cls is not PluginInterface:
                    plugins[module_name] = cls()
    return plugins


# plugins = load_plugins()

# def get_plugins():
#     return plugins
