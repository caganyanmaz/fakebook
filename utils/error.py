from flask import request
from functools import wraps
from utils.flask import get_with_args

def init():
    pass

def listen(link, error_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                return get_with_args(link, error=str(e))
        return wrapper
    return decorator


def check_keywords(link):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(dict(request.form))
            except KeyError as e:
                return get_with_args(link, error=f"Key error {str(e)}")
        return wrapper
    return decorator