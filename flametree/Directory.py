import os
import re

non_alphanum_regexpr = re.compile(r"[^a-zA-Z\d]")
def sanitize_name(name):
    """Return the name with all non-alphanumerics replaced by '_'. """
    if name[0] in "0123456789":
        name = "_" + name
    return re.sub(non_alphanum_regexpr, "_", name)

class FileTreeElement:
    """Base class for Directories and Files."""

    def __init__(self, location=".", name=None, file_manager=None):

        # Initialize the properties and the files manager
        self._name = name
        self._location = location
        if name is None:
            self._path = self._location
        else:
            self._path = os.path.join(self._location._path, self._name)
        self._file_manager = file_manager

        # Automatically explore the folder and subfolders to build a tree
        if self._is_dir:
            self._dict = {}
            self._files = []
            self._dirs = []
            if self._is_dir:
                for filename in self._file_manager.list_files(self):
                    self._file(filename, replace=False)
                for dirname in self._file_manager.list_dirs(self):
                    self._dir(dirname, replace=False)

    def _close(self):
        """Close the file manager."""
        return self._file_manager.close()

    def __exit__(self, *a):
        """Exit and close the file manager."""
        self._close()

    def __enter__(self):
        """Enter the Matrix."""
        return self

    def __repr__(self):
        """Pretty representation of the element, as its path"""
        return "<%s%s>" % (self._path, "/" if self._is_dir else "")


class Directory(FileTreeElement):
    """Directories contains a list of ``_files`` and subdirectories ``_dirs``.

    You can also access all files in the directory's subtree with
    ``._all_files``

    """
    _is_dir = True

    def _dir(self, name, replace=True):
        """Create and return a new subdirectory in the current directory.
        If replace is True and the subdirectory exists, it is overwritten.
        """

        if name in self._dict:
            subdir = self["name"]
            if replace:
                subdir._delete()
            else:
                return subdir
        else:
            subdir = Directory(location=self, name=name,
                               file_manager=self._file_manager)
        # From here we create
        self._file_manager.create(subdir, replace=replace)
        self._dirs.append(subdir)
        self._dict[name] = subdir
        self.__dict__[sanitize_name(subdir._name)] = subdir
        return subdir

    def _file(self, name, replace=True):
        """Create a new file or overwrite an existing one."""
        if name in self._dict:
            f = self["name"]
            if replace:
                f.delete()
            else:
                return f
        else:
            f = File(location=self, name=name, file_manager=self._file_manager)
        # From here we create
        self._file_manager.create(f)
        self._files.append(f)
        self._dict[f._name] = f
        self.__dict__[sanitize_name(f._name)] = f
        return f

    @property
    def _all_files(self):
        """Return a list of all file objects in that tree."""
        return self._files + sum([d._all_files for d in self._dirs], [])

    def _tree_view(self, indent_size=2, indent_level=0, as_lines=False):
        """Return a string representation of the tree for pretty printing.
        """
        lines = []
        space = indent_size * indent_level * " "
        for subdir in sorted(self._dirs, key=lambda subdir: subdir._name):
            lines.append("%s%s/" % (space, subdir._name))
            lines += subdir._tree_view(indent_size=indent_size,
                                       indent_level=indent_level + 1,
                                       as_lines=True)
        for f in sorted(self._files, key=lambda f: f._name):
            lines.append("%s%s" % (space, f._name))

        return lines if as_lines else "\n".join(lines)

    def _move(self, directory, replace_dirs=True, replace_files=True):
        """Move this directory into the specified directory.

        If ``replace_dirs`` is True, existing directories will be erased or
        overwritten. If ``replace_files`` is True, existing files will be
        overwritten.

        """
        # TODO: That's not the most memory-efficient way: better file-by-file
        self._copy(directory, replace_dirs=replace_dirs,
                   replace_files=replace_files)
        self._delete()

    def _copy(self, directory, replace_dirs=True, replace_files=True):
        """Copy this directory into the specified directory.

        If ``replace_dirs`` is True, existing directories will be erased or
        overwritten. If ``replace_files`` is True, existing files will be
        overwritten.

        """
        target = directory._dir(self._name, replace=replace_dirs)
        for f in self._files:
            f.copy(target, replace=replace_files)
        for subdir in self._dirs:
            target = target._dir(subdir._name, replace=replace_dirs)
            subdir._copy(target, replace_dirs=replace_dirs,
                         replace_files=replace_files)

    def _delete(self):
        """Delete this folder or file"""
        if isinstance(self._location, str):
            raise IOError("You can't delete the root dir with Flametree.")
        self._file_manager.delete(self)
        location = self._location
        location._dict.pop(self._name)
        location.__dict__.pop(self._name, None)
        location._dirs = [subdir for subdir in location._dirs
                          if subdir._name != self._name]

    def __getitem__(self, it):
            return self._dict[it]

class File(FileTreeElement):
    _is_dir = False

    def read(self, mode="r"):
        """Return the file's content as a string (mode 'r') or bytes ('rb').
        """
        return self._file_manager.read(self, mode=mode)

    def write(self, content, mode="a"):
        """Write data in the file.
        """
        if hasattr(content, "decode") and not mode.endswith("b"):
            mode += "b" # You'll thank me for this. Unless it breaks something.
        self._file_manager.write(self, content, mode=mode)

    def print_content(self):
        """Print the file's content."""
        print (self.read())

    def move(self, target, replace=True):
        """Move this file to the specified target (a directory or a file)
        """
        self.copy(target, replace=replace)
        self.delete()

    def copy(self, target, replace=True):
        if target._is_dir:
            if replace or (self._name not in target._dict):
                target._file(self._name).write(self.read(mode="rb"), mode="wb")
        else:
            target.write(self.read(mode="rb"), mode="wb")

    def delete(self):
        """Delete this file"""
        self._file_manager.delete(self)
        location = self._location
        location._dict.pop(self._name)
        location.__dict__.pop(self._name, None)
        location._files = [f for f in location._dirs if f._name != self._name]

    def open(self, mode="a"):
        return self._file_manager.open(self, mode=mode)

    @property
    def _name_no_extension(self):
        """File name without the extension"""
        return self._name.split(".")[0]

    @property
    def _path_no_extension(self):
        """File path without the extension"""
        return self._path.split(".")[0]

    @property
    def _extension(self):
        """File path without the extension"""
        return "" if "." not in self._name else self._name.split(".")[-1]
