import sys
from flask import send_file, jsonify
from route._general_imports import *
from utils.file import get_module_names_from_file
from route.login import user_logged_in
from utils.dynamic_file_manager import dynamic_file_manager

def set_routes(app):
    @app.route("/")
    def index():
        if(user_logged_in()):
            return flask_utils.redirect("main-page")
        return render_template("index.html")

    @app.route("/search/user/<string:q>")
    def search_user(q):
        res = tables.user.search("name", q, 4)
        return jsonify(to_secure_list(res))
    
    @app.route("/get-profile-picture/<int:user_id>")
    def get_profile_picture(user_id):
        picture = tables.user.get(user_id)["picture"]
        if picture == 0:
            return ""
        return send_file(dynamic_file_manager.get_file_dest(picture))

    modules = get_module_names_from_file("route", __file__, ["main", "__pycache__", "__init__", "_general_imports"])
    for module in modules:
        __import__(module)
        sys.modules[module].__dict__["set_routes"](app)

def to_secure_list(row_list):
    res = []
    for row in row_list:
        res.append({
            "id": row["id"],
            "name": row["name"]
        })
    return res