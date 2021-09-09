import socket
import os
from flask import redirect, request, render_template
#from flask_mail import Mail
import utils.file as file

HOST = "http://192.168.1.10"
PORT = 5000

def init():
    global PORT, HOST
    host_name = socket.gethostname()
    HOST = "http://" + socket.gethostbyname(host_name)
    PORT = os.environ.get("PORT", PORT)


def config_flask(app):
    json_data = file.get_json("config_flask.json")
    for key, val in json_data.items():
        app.config[key] = val


def get_with_args(address, **kwargs):
    link = address + "?" 
    for kwarg in kwargs:
        link += kwarg + "=" + kwargs[kwarg] + "&"
    return redirect(link[:-1])

address_cache = None


def get_address():
    global address_cache
    if not address_cache:
        address_cache = f"{HOST}:{PORT}"
    return address_cache


def create_method_switch(**methods):
    return lambda: methods[request.method]()


def create_static_pages(app, pages, file_404="404.html"):
    @app.route("/<static_page>")
    def manage_static_pages(static_page):
        template = pages.get(static_page)
        if template:
            return render_template(template)
        return render_template(file_404), 404
