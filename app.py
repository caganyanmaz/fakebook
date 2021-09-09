from _imports import *

def main():
    app = Flask(__name__, static_url_path="")
    app.secret_key = "rkjfkjfejfıfjdasd2498934892348adksa"
    init_utils()
    sql_manager = SqlManager("database.db")
    init_models(sql_manager)
    init_routes(app)
    return app


_ = main()
