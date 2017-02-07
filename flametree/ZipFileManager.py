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



class ZipFileManager:

    def __init__(self, path=None, source=None):
        if source is None:
            if path == "@memory":
                source = StringBytesIO()
            else:
                source = path
        elif isinstance(source, (str, bytes)):
            source = StringBytesIO(source)
        self.source = source
        self.path = "." if path is None else path
        if path == "@memory":
            # Horrible hack: we give an empty but valid zip to the reader:
            reader_source = StringBytesIO(b'PK\x05\x06' + 18 * b'\x00')
            self.reader = zipfile.ZipFile(reader_source, "r")

        elif isinstance(source, str) and not os.path.exists(source):
            reader_source = StringBytesIO(b'PK\x05\x06' + 18 * b'\x00')
            self.reader = zipfile.ZipFile(reader_source, "r")
        else:
            self.reader = zipfile.ZipFile(source, "r")
        self.files_data = defaultdict(lambda *a: StringBytesIO())
        self.writer = zipfile.ZipFile(source, "a",
                                      compression=zipfile.ZIP_DEFLATED)

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

    def tell(self, fileobject):
        path = self.relative_path(fileobject)
        return self.files_data[path].tell()

    def flush(self, fileobject):
        path = self.relative_path(fileobject)
        return self.files_data[path].flush()




    def path_exists_in_file(self, directory):
        return self.relative_path(directory) in self.reader.namelist()


    @staticmethod
    def join_paths(*paths):
        return "/".join(*paths)

    def flush(self, fileobject):
        path = self.relative_path(fileobject)
        return self.files_data[path].flush()

    def close(self):
        for path, data in self.files_data.items():
            self.writer.writestr(path, data.getvalue())
        self.writer.close()
        if hasattr(self.source, "getvalue"):
            return self.source.getvalue()
