import os
import sys
from flametree import (file_tree, DiskFileManager, ZipFileManager)

PYTHON3 = (sys.version_info[0] == 3)


zip_path = "test.zip"
test_dir = "testdir"
ALL_FILES = set(["bla.txt", "bli.txt", "blu.txt", "Readme.md"])

def test_directory(tmpdir):
    # CREATE AND POPULATE A DIRECTORY FROM SCRATCH
    dir_path = os.path.join(str(tmpdir), "test_dir")
    root = file_tree(dir_path)
    assert root._file_manager.__class__ == DiskFileManager
    root._file("Readme.md").write("This is a test zip")
    root._dir("texts")._dir("shorts")._file("bla.txt").write("bla bla bla")
    root.texts.shorts._file("bli.txt").write("bli bli bli")
    root.texts.shorts._file("blu.txt").write("blu blu blu")

    # TEST REPLACE BEHAVIOR
    root._dir("trash")._file("bla.txt").write("bla bla bla")
    root._dir("trash")._file("blu.txt").write("blu blu blu")
    print (root._tree_view())
    assert root.trash._filenames == ["blu.txt"]

    root.trash._delete()
    root._dir("trash")._file("bla.txt").write("bla bla bla")
    root._dir("trash", replace=False)._file("blu.txt").write("blu blu blu")
    assert set(root.trash._filenames) == set(["bla.txt", "blu.txt"])


    # READ AN EXISTING DIRECTORY
    root = file_tree(dir_path)
    assert set([f._name for f in root._all_files]) == ALL_FILES

    # APPEND TO AN EXISTING DIRECTORY
    root._dir("newdir")._file("new_file.txt").write("I am a new file")
    print("ah ah ah ah ah ah")
    root = file_tree(dir_path)
    print("ojojjoojojojojoj")
    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt"]))

    # TEST DELETION
    path = root.newdir.new_file_txt._path
    assert os.path.exists(path)
    root.newdir.new_file_txt.delete()
    assert not os.path.exists(path)
    assert not any([f._path == path for f in root.newdir._files])



def test_zip(tmpdir):
    # CREATE AND POPULATE A ZIP FROM SCRATCH, IN MEMORY
    root = file_tree("@memory")
    assert root._file_manager.__class__ == ZipFileManager
    root._file("Readme.md").write("This is a test zip")
    root._dir("texts")._dir("shorts")._file("bla.txt").write("bla bla bla")
    root.texts.shorts._file("bli.txt").write("bli bli bli")
    root.texts.shorts._file("blu.txt").write("blu blu blu")

    data = root._close()

    # READ A ZIP FROM DATA IN MEMORY
    root = file_tree(data)
    assert set([f._name for f in root._all_files]) == ALL_FILES

    # APPEND TO A CREATED ZIP IN MEMORY
    root._dir("newdir")._file("new_file.txt").write("I am a new file")
    new_data = root._close()

    # VERIFY THAT THE DATA RECEIVED CAN BE WRITTEN TO A VALID ZIP

    zip_path = os.path.join(str(tmpdir), "test.zip")
    with open(zip_path, ("wb" if PYTHON3 else "w")) as f:
        f.write(new_data)
    root = file_tree(zip_path)

    # READ ZIP FROM DISK, APPEND TO IT

    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt"]))
    root.newdir._file("new_file2.txt").write("I am another new file")
    root._close()

    # Final test
    root = file_tree(zip_path)
    assert set([f._name for f in root._all_files]) == \
        ALL_FILES.union(set(["new_file.txt", "new_file2.txt"]))

def test_file_tree(tmpdir):
    """Assert that the directory function dispatches as expected."""

    root = file_tree(os.path.join(str(tmpdir), "my_folder/"))
    assert root._file_manager.__class__ == DiskFileManager

    root = file_tree(os.path.join(str(tmpdir), "my_archive.zip"))
    assert root._file_manager.__class__ == ZipFileManager

    root = file_tree("@memory")
    assert root._file_manager.__class__ == ZipFileManager
    root._file("test.txt").write("bla bla bla bla bla bla bla bla")
    data = root._close()

    root = file_tree(data)
    assert root._file_manager.__class__ == ZipFileManager
    assert [f._name for f in root._all_files] == ["test.txt"]

def test_matplotlib_writer(tmpdir):
    zip_path = os.path.join(str(tmpdir), "archive.zip")
    folder_path = os.path.join(str(tmpdir), "test_folder")
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Not running test_matplotlib_writer: Matplotlib not available.")
        return True
    fig, ax = plt.subplots(1)
    with file_tree(zip_path) as zip_root:
        fig_dir = zip_root._dir("figures", replace=False)
        fig.savefig(fig_dir._file("fig.png"), format="png")
        fig.savefig(fig_dir._file("fig.pdf").open("wb"), format="pdf")
    with file_tree(folder_path) as root:
        fig_dir = root._dir("figures", replace=False)
        fig.savefig(fig_dir._file("fig.png"), format="png")#
        fig.savefig(fig_dir._file("fig.pdf").open("wb"), format="pdf")
    assert (set([f._name for f in root._all_files]) ==
            set(["fig.png", "fig.pdf"]))
    assert os.path.exists(os.path.join(folder_path, "figures", "fig.pdf"))
