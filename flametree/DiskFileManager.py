import os
import shutil


class DiskFileManager:

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
    def delete(target):
        if target._is_dir:
            shutil.rmtree(target._path)
        else:
            os.remove(target._path)

    def create(self, target, replace=True):
        path = target._path
        if replace and os.path.exists(path):
            self.delete(target)
        if replace or (not os.path.exists(path)):
            if target._is_dir:
                os.mkdir(path)
            else:
                with open(path, "w") as f:
                    pass

    @staticmethod
    def join_paths(*paths):
        return os.path.join(*paths)

    def close():
        pass

    def tell(self, fileobject):
        with open(fileobject._path, "a") as f:
             return f.tell()

    def flush(self, fileobject):
        pass
