import os
import sys
from utils.file import get_module_names_from_file
#import mysql_manager
NAME = "models"


def init_models(sql_manager):
    modules = get_module_names_from_file("models", __file__, ["init_models", "__pycache__", "__init__"])
    for module in modules:
        try:
            __import__(module)
            table = sys.modules[module].__dict__["TEMPLATE"]
            name = module[len(NAME) +1:]
            sql_manager.add_table(name, table)
        except Exception as e:
            raise e
    sql_manager.create_tables()
