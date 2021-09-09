import os
import utils.file as file_utils

dynamic_file_manager = None

def init():
    pass


class DynamicFileManager:
    def __init__(self):
        self.SUB_DIR = "files"
        self.FOLDER_SIZE = 5
        self.file_count = self.get_file_count()

    def add(self, file):
        extension = file_utils.get_extension(file.filename)
        file_dest, id = self.create_file_data(extension)
        file_utils.create_directory(file_utils.get_directory(file_dest))
        file.save(file_dest)
        return id

    def get_id(self, filepath):
        val = 0
        filepath_pieces = filepath.split("\\")
        if len(filepath_pieces) < 2:
            return val
        for folder in filepath_pieces[1:-1]:
            val *= self.FOLDER_SIZE
            val += int(folder)
        val *= self.FOLDER_SIZE
        val += int(file_utils.lose_extension(filepath_pieces[-1]))
        return val
    
    def create_file_data(self, extension=".file"):
        self.file_count += 1
        return self.get_file_dest(self.file_count, extension), self.file_count

    def get_file_dest(self, id, extension=".file"):
        dest = extension
        while id > 0:
            dest = "\\" + str((id % self.FOLDER_SIZE)) + dest
            id = int(id / self.FOLDER_SIZE)
        return self.SUB_DIR + dest

    def get_file_count(self):
        filepath = self.SUB_DIR
        if not os.path.exists(file_utils.get_absolute_path(filepath)):
            return 0
        while True:
            dir_list = os.listdir(file_utils.get_absolute_path(filepath))[::-1]
            for dir in dir_list:
                if "." in dir:
                    continue
                filepath += "\\" + dir
                break
            else:
                if len(dir_list) > 0:
                    filepath += "\\" + dir_list[0]
                break
        return self.get_id(filepath)

dynamic_file_manager = DynamicFileManager()
