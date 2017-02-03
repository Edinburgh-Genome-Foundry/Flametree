import os
import shutil
from .FilesTree import FilesTree


class DirectoryFilesManager:

    @staticmethod
    def list_files(directory):
        path = directory._path
        return [] if not os.path.exists(path) else [
            name for name in os.listdir(path)
            if os.path.isfile(os.path.join(path, name))
        ]
    @staticmethod
    def list_dirs(directory):
        path = directory._path
        return [] if not os.path.exists(path) else [
            name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))
        ]

    @staticmethod
    def read(fileobject, mode="r"):
        with open(fileobject._path, mode=mode) as f:
            result = f.read()
        return result

    @staticmethod
    def write(fileobject, content, mode="a"):
        with open(fileobject._path, mode=mode) as f:
            f.write(content)

    @staticmethod
    def delete(directory):
        if directory._is_dir:
            shutil.rmtree(directory._path)
        else:
            os.remove(directory._path)

    def create(self, directory, replace=True):
        path = directory._path
        if replace and os.path.exists(path):
            self.delete(directory)
        if replace or (not os.path.exists(path)):
            if directory._is_dir:
                os.mkdir(path)
            else:
                with open(path, "w") as f:
                    pass

    @staticmethod
    def join_paths(*paths):
        return os.path.join(*paths)

class DirectoryFilesTree(FilesTree):

    def _init_files_manager(self):
        return DirectoryFilesManager()
