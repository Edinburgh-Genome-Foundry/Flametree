from .ZipFileManager import ZipFileManager
from .DiskFileManager import DiskFileManager
from .Directory import Directory

def file_tree(target, replace=False):
    """Open a connection to a file tree which can be either a disk folder, a
    zip archive, or an in-memory zip archive.

    Parameters
    ----------

    target
      Either the path to a target folder, or a zip file, or '@memory' to write
      a zip file in memory (at which case a string of the zip file is returned)

    replace
      If True, will remove the target if it already exists. If False, new files
      will be written inside the target and some files may be overwritten.
    """
    if not isinstance(target, str):
        return Directory(file_manager=ZipFileManager(source=target))
    elif target == '@memory':
        return Directory("@memory", file_manager=ZipFileManager("@memory"))
    elif target.lower().endswith(".zip"):
        return Directory(target, file_manager=ZipFileManager(target),
                         replace=replace)
    else:
        try:
            return Directory(target, file_manager=DiskFileManager(),
                             replace=replace)
        except:
            pass

    # Last chance, lets try again if it's some kind of zip data:
    return Directory(file_manager=ZipFileManager(source=target))
