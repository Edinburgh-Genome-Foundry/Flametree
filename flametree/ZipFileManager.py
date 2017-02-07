import os
import sys
import zipfile
import re
from collections import defaultdict

PYTHON3 = (sys.version_info[0] == 3)

if PYTHON3:
    from io import StringIO, BytesIO
    StringBytesIO = BytesIO
else:
    from StringIO import StringIO
    StringBytesIO = StringIO

EMPTY_ZIP_BYTES = b'PK\x05\x06' + 18 * b'\x00'

class ZipFileManager:

    def __init__(self, path=None, source=None, replace=False):
        self.path = "." if path is None else path
        if path == "@memory": # VIRTUAL ZIP FROM SCRATCH
            self.source = StringBytesIO()
            self.writer = zipfile.ZipFile(self.source, "a",
                                          compression=zipfile.ZIP_DEFLATED)
            self.reader = zipfile.ZipFile(StringBytesIO(EMPTY_ZIP_BYTES), "r")
        elif path is not None:  # ON DISK ZIP
            self.source = path
            if replace or not os.path.exists(path):
                with open(self.source, "wb") as f:
                    f.write(EMPTY_ZIP_BYTES)
            self.writer = zipfile.ZipFile(self.source, "a",
                                          compression=zipfile.ZIP_DEFLATED)
            self.reader = zipfile.ZipFile(self.source, "r")
        else: # VIRTUAL ZIP FROM EXISTING DATA
            self.source = source
            if isinstance(self.source, (str, bytes)):
                self.source = StringBytesIO(source)
            self.writer = zipfile.ZipFile(self.source, "a",
                                          compression=zipfile.ZIP_DEFLATED)
            self.reader = zipfile.ZipFile(self.source, "r")
        self.files_data = defaultdict(lambda *a: StringBytesIO())

    def relative_path(self, target):
        path = target._path[len(self.path)+1:]
        if target._is_dir and path != "":
            path += "/"
        return path


    def list_files(self, directory):
        path = self.relative_path(directory)
        matches = [
            re.match(r"%s([^/]*)$" % path, name)
            for name in self.reader.namelist()
        ]
        files = set([
            match.groups()[0]
            for match in matches
            if match is not None
            and (match.groups()[0] != "")
        ])
        return files


    def list_dirs(self, directory):
        path = self.relative_path(directory)
        matches = [
            re.match(r"%s([^/]*)/" % path, name)
            for name in self.reader.namelist()
        ]
        dirs = set([
            match.groups()[0]
            for match in matches
            if match is not None
            and (match.groups()[0] != "")
        ])
        return dirs


    def read(self, fileobject, mode="r"):
        path = self.relative_path(fileobject).strip("/")
        if path in self.files_data:
            return self.files_data[path].getvalue()
        else:
            return self.reader.read(path)

    def write(self, fileobject, content, mode="w"):
        path = self.relative_path(fileobject)
        if self.path_exists_in_file(fileobject):
            raise NotImplementedError(
                "Rewriting a file already zipped is not currently supported. "
                "It may actually not even be possible, or in an inelegant way."
            )
        if mode in ("w", "wb"): # i.e. not append
            self.files_data.pop(path, None) # overwrite if exists!
        if not isinstance(content, bytes):
            content = content.encode("utf-8")
        self.files_data[path].write(content)

    def delete(self, directory):
        raise NotImplementedError(
            "Deleting/modifying/overwriting an already-zipped file "
            "is not currently supported. "
            "It may actually not even be possible, or in a very inelegant way."
        )

    def create(self, directory, replace=False):
        if self.path_exists_in_file(directory) and replace:
            self.delete(directory)
        # TODO: I don't know how to create an empty dir in a zip but right
        # now it doesn't really matter because the directories are created
        # the moment we create a file whose address in this directory.

    def path_exists_in_file(self, directory):
        return self.relative_path(directory) in self.reader.namelist()


    @staticmethod
    def join_paths(*paths):
        return "/".join(*paths)

    def close(self):
        for path, data in self.files_data.items():
            self.writer.writestr(path, data.getvalue())
        self.writer.close()
        if hasattr(self.source, "getvalue"):
            return self.source.getvalue()

    def open(self, fileobject, mode="a"):
        path = self.relative_path(fileobject)
        if mode in ("r", "rb"):
            if path in self.files_data:
                return StringBytesIO(self.files_data.getvalue())
            else:
                return StringBytesIO(self.read(fileobject, mode=mode))
        else:
            return self.files_data[path]
