import os
import shutil


class DiskFileManager:
    """Reader and Writer for disk files.


    target
      A directory on the disk. If it doesn't exist, it will be created.

    replace
      If the ``target`` directory exists, should it be completely replaced
      or simply appended to ?
    """

    def __init__(self, target, replace=False):
        self.target = target
        if replace and os.path.exists(target):
            shutil.rmtree(target)
        if not os.path.exists(target):
            os.makedirs(target)

    @staticmethod
    def list_directory_content(directory, element_type="file"):
        """Return the list of all file or dir objects in the directory."""
        filtr = os.path.isfile if (element_type == "file") else os.path.isdir
        path = directory._path
        return (
            []
            if not os.path.exists(path)
            else [name for name in os.listdir(path) if filtr(os.path.join(path, name))]
        )

    @classmethod
    def list_files(cls, directory):
        """Return the list of all file objects in the directory."""
        return cls.list_directory_content(directory, element_type="file")

    @classmethod
    def list_dirs(cls, directory):
        """Return the list of all directory objects in the directory."""
        return cls.list_directory_content(directory, element_type="dirs")

    @staticmethod
    def read(fileobject, mode="r"):
        """Return the entire content of a file. The mode can be 'r' or 'rb'."""
        with open(fileobject._path, mode=mode) as f:
            result = f.read()
        return result

    @staticmethod
    def write(fileobject, content, mode="a"):
        """Write the content (str, bytes) to the given file object."""
        with open(fileobject._path, mode=mode) as f:
            f.write(content)

    @staticmethod
    def delete(target):
        """Delete the file on disk."""
        if target._is_dir:
            shutil.rmtree(target._path)
        else:
            os.remove(target._path)

    def create(self, target, replace=False):
        """Create a new, empty file or directory on disk."""
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
        """Join paths in a system/independent way -- actually os.path.join."""
        return os.path.join(*paths)

    @staticmethod
    def close():
        """This method does nothing for DiskFileManagers."""
        pass

    def open(self, fileobject, mode="a"):
        """Open a file on disk at the location given by the file object."""
        return open(fileobject._path, mode=mode)
