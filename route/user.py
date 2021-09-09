# These are the routes that the user will use
# when s/he is logged in
import flask
from route._general_imports import *
from route.login import user_logged_in


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
        return render_template("profile.html", username=tables.user.get(session["id"])["name"])

    @app.route("/logout")
    def logout():
        if not user_logged_in():
            return flask_utils.redirect("/")
        session.clear()
        return flask_utils.redirect("/")
    
