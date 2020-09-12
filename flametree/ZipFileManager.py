import os
import sys
import zipfile
import re
from collections import defaultdict

PYTHON3 = sys.version_info[0] == 3

if PYTHON3:
    from io import StringIO, BytesIO

    StringBytesIO = BytesIO

else:
    from StringIO import StringIO

    BytesIO = StringIO
    StringBytesIO = StringIO

EMPTY_ZIP_BYTES = b"PK\x05\x06" + 18 * b"\x00"


class ZipFileManager:
    """Reader and Writer of Zip files.

    Parameters
    ----------

    path
      Path to a zip archive to be read or written to.

    source
      Either a string/byte representing zipped data, or a file-like object
      connected to zipped data.

    replace
      In case the provided ``path`` is pointing to an already-existing file,
      should it be erased or appended to ?
    """

    # The Zipfile manager manages at the same time files already in the zip
    # archive when it was created, and files left uncompressed in memory.
    # The uncompressed files in memory are flushed into the archive upon
    # closing of the manager, with the ``.close`` method.

    def __init__(self, path=None, source=None, replace=False):
        self.path = "." if path is None else path
        if path == "@memory":  # VIRTUAL ZIP FROM SCRATCH
            self.source = StringBytesIO()
            self.writer = zipfile.ZipFile(
                self.source, "a", compression=zipfile.ZIP_DEFLATED
            )
            self.reader = zipfile.ZipFile(StringBytesIO(EMPTY_ZIP_BYTES), "r")
        elif path is not None:  # ON DISK ZIP
            self.source = path
            if replace or not os.path.exists(path):
                with open(self.source, "wb") as f:
                    f.write(EMPTY_ZIP_BYTES)
            self.writer = zipfile.ZipFile(
                self.source, "a", compression=zipfile.ZIP_DEFLATED
            )
            self.reader = zipfile.ZipFile(self.source, "r")
        else:  # VIRTUAL ZIP FROM EXISTING DATA
            self.source = source
            if isinstance(self.source, (str, bytes)):
                self.source = StringBytesIO(source)
            self.writer = zipfile.ZipFile(
                self.source, "a", compression=zipfile.ZIP_DEFLATED
            )
            self.reader = zipfile.ZipFile(self.source, "r")
        self.files_data = defaultdict(lambda *a: StringBytesIO())

    def relative_path(self, target):
        path = target._path[len(self.path) + 1 :]
        if target._is_dir and path != "":
            path += "/"
        return path

    def list_directory_components(self, directory, regexpr):
        path = self.relative_path(directory)
        matches = [
            re.match(regexpr % re.escape(path), name) for name in self.reader.namelist()
        ]
        return sorted(
            set(
                [
                    match.groups()[0]
                    for match in matches
                    if match is not None and (match.groups()[0] != "")
                ]
            )
        )

    def list_files(self, directory):
        return self.list_directory_components(directory, regexpr=r"%s([^/]*)$")

    def list_dirs(self, directory):
        return self.list_directory_components(directory, regexpr=r"%s([^/]*)/")

    def read(self, fileobject, mode="r"):
        path = self.relative_path(fileobject).strip("/")
        if path in self.files_data:
            result = self.files_data[path].getvalue()
        else:
            result = self.reader.read(path)
        if (mode == "r") and hasattr(result, "decode"):
            result = result.decode("utf8")
        return result

    def write(self, fileobject, content, mode="w"):
        path = self.relative_path(fileobject)
        if self.path_exists_in_file(fileobject):
            raise NotImplementedError(
                "Rewriting a file already zipped is not currently supported. "
                "It may actually not even be possible, or in an inelegant way."
            )
        if mode in ("w", "wb"):  # i.e. not append
            self.files_data.pop(path, None)  # overwrite if exists!
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
            container = {"r": StringIO, "rb": BytesIO}[mode]
            if path in self.files_data:
                content = self.files_data[path].getvalue()
                if mode == "r":
                    content = content.decode()
                return container(content)
            else:
                return container(self.read(fileobject, mode=mode))
        else:
            if mode == "w" and path not in self.files_data:
                self.files_data[path] = StringIO()
            elif mode == "wb" and path not in self.files_data:
                self.files_data[path] = BytesIO()
            return self.files_data[path]
