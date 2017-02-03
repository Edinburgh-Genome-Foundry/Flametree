from .ZipFilesTree import ZipFilesTree, ZipFilesManager
from .DirectoryFilesTree import DirectoryFilesTree
def files_tree(target, replace=False):
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
        return ZipFilesTree(files_manager=ZipFilesManager(source=target))
    elif target == '@memory':
        return ZipFilesTree("@memory")
    elif target.lower().endswith(".zip"):
        return ZipFilesTree(target)
    else:
        try:
            return DirectoryFilesTree(target)
        except:
            pass

    # Last chance, lets try again:
    return ZipFilesTree(files_manager=ZipFilesManager(source=target))
