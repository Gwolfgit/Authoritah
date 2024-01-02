import os
from yaml import load, dump
from types import MappingProxyType

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

with open(os.path.join(os.getcwd(), 'settings', 'server.yaml'), 'r') as file:
    data = Loader(file).get_data()

CONFIG = MappingProxyType(data)

with open(os.path.join(os.getcwd(), 'settings', 'default.yaml'), 'r') as file:
    data = Loader(file).get_data()

DEFAULT = MappingProxyType(data)
DEFAULT_TTL = 3600
DEBUG_MODE = True
