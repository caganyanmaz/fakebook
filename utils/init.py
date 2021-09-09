import os
import sys
from utils.file import get_module_names_from_file


def init():
    modules = get_module_names_from_file("utils", __file__, ["init", "__pycache__", "__init__"])
    for module in modules:
        __import__(module)
        sys.modules[module].__dict__["init"]()