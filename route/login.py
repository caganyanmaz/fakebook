from route._general_imports import *
import bcrypt

def set_routes(app):
    switch = flask_utils.create_method_switch(GET=_get, POST=_post)
    @app.route("/login", methods=["GET", "POST"])
    def login():
        return switch()


def _get():
    return render_template("login.html", error=request.args.get("error"))


@error_utils.listen("/login", SqlManager.VariableConstraintError)
@error_utils.check_keywords("/login")
def _post(args):
    users = tables.user.get_with(name=args["username"])
    if len(users) < 1:
        return flask_utils.get_with_args("/login", error="Unknown username")
    user = users[0]
    if not bcrypt.checkpw(args["password"].encode(), user["password"].encode()):
        return flask_utils.get_with_args("/login", error="Password is incorrect")
    session["id"] = user["id"]
    return flask_utils.redirect("/")


def user_logged_in():
    return session.get("id") is not None
