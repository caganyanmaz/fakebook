import sys

import flask
from route._general_imports import *
from utils.file import get_module_names_from_file
from route.login import user_logged_in

def set_routes(app):
    @app.route("/")
    def index():
        if(user_logged_in()):
            return flask_utils.redirect("main-page")
        return render_template("index.html")

    

    modules = get_module_names_from_file("route", __file__, ["main", "__pycache__", "__init__", "_general_imports"])
    for module in modules:
        __import__(module)
        sys.modules[module].__dict__["set_routes"](app)