from os import error
from route._general_imports import *
import bcrypt

def set_routes(app):
    switch = flask_utils.create_method_switch(GET=_get, POST=_post)
    @app.route("/register", methods=["GET", "POST"])
    def register():
        return switch()


def _get():
    return render_template("register.html", error=request.args.get("error"))

@error_utils.check_keywords("/register")
@error_utils.listen("/register", SqlManager.VariableConstraintError)
def _post(args):
    if args["password"] != args["password-confirm"]:
        return flask_utils.get_with_args("/register", error="Password doesn't match with the confirmation")
    
    session["id"] = tables.user.insert({
        "name": args["username"],
        "password": bcrypt.hashpw(args["password"].encode(), bcrypt.gensalt()),
        "email": args["email"]
    })

    return flask_utils.redirect("/") #Change to main page later