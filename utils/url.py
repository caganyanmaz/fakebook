def init():
    pass


def add_variable(url, var_name, value):
    end = var_name + "=" + str(value)
    if "?" in url:
        url += "&"
    else:
        url += "?"
    return url + end
