from json import loads as to_json
import os

file_count = 0
FILE_STEP = 5
DYNAMIC_FILE_SUB_DIR = "files"


def init():
    pass


def get_string(filename):
    data = ""
    with open(filename, "r") as file:
        data = file.read().replace("\n", "")
    return data


def get_json(filename):
    text = get_string(filename)
    return to_json(text)


def get_module_names_from_file(start, file, BYPASS):
    for file in os.listdir(os.path.dirname(os.path.realpath(file))):
        file_name = lose_extension(file)
        if file_name not in BYPASS:
            yield start + "." + lose_extension(file)


def get_absolute_path(name):
    return os.path.join(os.getcwd(), name)


def create_directory(dir):
    if not os.path.exists(os.path.join(os.getcwd(), dir)):
        os.mkdir(dir)


def lose_extension(filename):
    index = get_extension_index(filename)
    return filename[:index]


def get_extension(filename):
    return filename[get_extension_index(filename):]


def get_directory(file_dest):
    return file_dest[:get_name_index(file_dest)]


def get_name(file_dest):
    return file_dest[get_name_index(file_dest):get_extension_index(file_dest)]


def get_extension_index(filename):
    index = filename.rfind(".")
    if index < 0:
        return len(filename)
    return index


def get_name_index(file_dest):
    return file_dest.rfind("/") + 1
