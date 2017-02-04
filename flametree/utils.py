from .ZipFileTree import ZipFileTree, ZipFileManager
from .DirectoryFileTree import DirectoryFileTree
def file_tree(target, replace=False):
    """
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
        return ZipFileTree(file_manager=ZipFileManager(source=target))
    elif target == '@memory':
        return ZipFileTree("@memory")
    elif target.lower().endswith(".zip"):
        return ZipFileTree(target)
    else:
        try:
            return DirectoryFileTree(target)
        except:
            pass

    # Last chance, lets try again:
    return ZipFileTree(file_manager=ZipFileManager(source=target))
