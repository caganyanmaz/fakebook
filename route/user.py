# These are the routes that the user will use
# when s/he is logged in
from flask import send_file
from route._general_imports import *
from route.login import user_logged_in
from utils.dynamic_file_manager import dynamic_file_manager


def set_routes(app):
    @app.route("/main-page")
    def main_page():
        if not user_logged_in():
            return flask_utils.redirect("/")
        return render_template("main_page.html", username=tables.user.get(session["id"])["name"])

    @app.route("/profile")
    def profile():
        if not user_logged_in():
            return flask_utils.redirect("/")
        return render_template(
            "profile.html", 
            username=tables.user.get(session["id"])["name"],
            error=request.args.get("error"),
            user_id=session["id"]
        )

    @app.route("/add-user-picture", methods=["POST"])
    def add_picture():
        if not user_logged_in():
            return flask_utils.redirect("/")
        return _add_picture()

    @app.route("/logout")
    def logout():
        if not user_logged_in():
            return flask_utils.redirect("/")
        session.clear()
        return flask_utils.redirect("/")

    

@error_utils.check_keywords("/profile")    
def _add_picture(args):
    id = dynamic_file_manager.add_without_extension(request.files["file"])
    tables.user.edit(session["id"], picture=id)
    return flask_utils.redirect("/profile")
