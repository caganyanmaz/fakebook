#import sys
#sys.path.insert(1, "D:/kodlama/python/PycharmProjects/mysql_manager/src")
#import mysql_manager
from flask import Flask, render_template, session, request
import utils.flask as flask_utils
from utils.init import init as init_utils
from models.init_models import init_models
from utils.sql_manager import SqlManager
import utils.sql_manager as tables
import constants
from route.main import set_routes as init_routes