import os
import sys
from flametree import (DirectoryFileTree, ZipFileTree, ZipFileManager,
                       file_tree)

PYTHON3 = (sys.version_info[0] == 3)


zip_path = "test.zip"
test_dir = "testdir"
ALL_FILES = set(["bla.txt", "bli.txt", "blu.txt", "Readme.md"])

def test_directory(tmpdir):
    # CREATE AND POPULATE A DIRECTORY FROM SCRATCH
    dir_path = os.path.join(str(tmpdir), "test_dir")
    root = DirectoryFileTree(dir_path)
    root._file("Readme.md").write("This is a test zip")
    root._dir("texts")._dir("shorts")._file("bla.txt").write("bla bla bla")
    root.texts.shorts._file("bli.txt").write("bli bli bli")
    root.texts.shorts._file("blu.txt").write("blu blu blu")

    # READ AN EXISTING DIRECTORY
    root = DirectoryFileTree(dir_path)
    assert set([f._name for f in root._all_files]) == ALL_FILES

    # APPEND TO AN EXISTING DIRECTORY
    root._dir("newdir")._file("new_file.txt").write("I am a new file")

    root = DirectoryFileTree(dir_path)
    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt"]))

    # TEST DELETION
    path = root.newdir.new_file_txt._path
    assert os.path.exists(path)
    root.newdir.new_file_txt._delete()
    assert not os.path.exists(path)
    assert not any([f._path == path for f in root.newdir._files])



def test_zip(tmpdir):
    # CREATE AND POPULATE A ZIP FROM SCRATCH, IN MEMORY
    root = ZipFileTree("@memory")
    root._file("Readme.md").write("This is a test zip")
    root._dir("texts")._dir("shorts")._file("bla.txt").write("bla bla bla")
    root.texts.shorts._file("bli.txt").write("bli bli bli")
    root.texts.shorts._file("blu.txt").write("blu blu blu")

    data = root._close()

    # READ A ZIP FROM DATA IN MEMORY
    root = ZipFileTree(file_manager=ZipFileManager(source=data))
    assert set([f._name for f in root._all_files]) == ALL_FILES

    # APPEND TO A CREATED ZIP IN MEMORY
    root._dir("newdir")._file("new_file.txt").write("I am a new file")
    new_data = root._close()

    # VERIFY THAT THE DATA RECEIVED CAN BE WRITTEN TO A VALID ZIP

    zip_path = os.path.join(str(tmpdir), "test.zip")
    with open(zip_path, ("wb" if PYTHON3 else "w")) as f:
        f.write(new_data)
    root = ZipFileTree(zip_path)

    # READ ZIP FROM DISK, APPEND TO IT

    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt"]))
    root.newdir._file("new_file2.txt").write("I am another new file")
    root._close()

    # Final test
    root = ZipFileTree(zip_path)
    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt", "new_file2.txt"]))

def test_file_tree(tmpdir):
    """Assert that the file_tree function dispatches as expected."""

    root = file_tree(os.path.join(str(tmpdir), "my_folder/"))
    assert root.__class__ == DirectoryFileTree

    root = file_tree(os.path.join(str(tmpdir), "my_archive.zip"))
    assert root.__class__ == ZipFileTree

    root = file_tree("@memory")
    assert root.__class__ == ZipFileTree
    root._file("test.txt").write("bla bla bla bla bla bla bla bla")
    data = root._close()

    root = file_tree(data)
    assert root.__class__ == ZipFileTree
    assert [f._name for f in root._all_files] == ["test.txt"]

def test_file_writer(tmpdir):
    zip_path = os.path.join(str(tmpdir), "archive.zip")
    print (zip_path)
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return True
    with ZipFileTree(zip_path) as root:
        fig, ax = plt.subplots(1)
        fig_dir = root._dir("figures2", replace=False)
        fig.savefig(fig_dir._file("nice2.png"), format="png")
    root = ZipFileTree(zip_path)
    assert [f._name for f in root._all_files] == ["nice2.png"]
