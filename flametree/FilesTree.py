import os
import re

expr = re.compile(r"[^a-zA-Z\d]")
def sanitize_name(name):
    if name[0] in "0123456789":
        name = "_" + name
    return re.sub(expr, "_", name)

class FilesTree:
    _is_dir = True

    def __init__(self, location=".", name=None, files_manager=None,
                 replace=False):

        # Initialize the properties and the files manager
        self._name = name
        self._location = location
        self._dict = {}
        if name is None:
            self._path = self._location
        else:
            self._path = os.path.join(self._location._path, self._name)
        if files_manager is None:
            files_manager = self._init_files_manager()
        self._files_manager = files_manager
        self._files_manager.create(self, replace=replace)

        # Automatically explore the folder and subfolders to build a tree
        self._files = []
        self._dirs = []
        if self._is_dir:
            for filename in self._files_manager.list_files(self):
                self._file(filename, replace=False)
            for dirname in self._files_manager.list_dirs(self):
                self._dir(dirname, replace=False)

    def _dir(self, name, replace=True):
        if name not in self._dict:
            subdir = FilesTree(location=self, name=name,
                               files_manager=self._files_manager,
                               replace=replace)
            self._dirs.append(subdir)
            self._dict[name] = subdir
            self.__dict__[sanitize_name(subdir._name)] = subdir
        return self._dict[name]

    def _file(self, name, replace=True):
        if name not in self._dict:
            f = File(location=self, name=name,
                     files_manager=self._files_manager,
                     replace=replace)
            self._files.append(f)
            self._dict[f._name] = f
            self.__dict__[sanitize_name(f._name)] = f
        return self._dict[name]

    def _delete(self):
        if isinstance(self._location, str):
            raise IOError("Looks like you are trying to delete the root.")
        self._files_manager.delete(self)
        location = self._location
        location._dict.pop(self._name)
        location.__dict__.pop(self._name, None)
        if self._is_dir:
            location._dirs = [subdir for subdir in location._dirs
                              if subdir._name == self._name]
        else:
            location._files = [f for f in location._dirs
                               if f._name == self._name]

    def __getitem__(self, it):
        return self._dict[it]

    @property
    def _all_files(self):
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

    def _close(self):
        pass

    def __exit__(self, *a):
        self._close()

    def __enter__(self):
        return self


class File(FilesTree):
    _is_dir = False

    def read(self, mode="r"):
        return self._files_manager.read(self, mode=mode)

    def write(self, content, mode="a"):
        if hasattr(content, "decode"):
            mode += "b"
        self._files_manager.write(self, content, mode=mode)
