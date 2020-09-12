import os
import sys
from flametree import file_tree, DiskFileManager, ZipFileManager
import pytest

PYTHON3 = sys.version_info[0] == 3


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

    # READ AN EXISTING FILE (two ways)
    assert root.texts.shorts.bla_txt.read() == "bla bla bla"
    with root.texts.shorts.bla_txt.open("r") as f:
        assert f.read() == "bla bla bla"

    # TEST REPLACE BEHAVIOR (replace=False)
    root._dir("trash")._file("bla.txt").write("bla bla bla")
    root._dir("trash")._file("blu.txt").write("blu blu blu")
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
    root = file_tree(dir_path)
    assert set([f._name for f in root._all_files]) == ALL_FILES.union(
        set(["new_file.txt"])
    )

    # TEST DELETION
    path = root.newdir.new_file_txt._path
    assert os.path.exists(path)
    root.newdir.new_file_txt.delete()
    assert not os.path.exists(path)
    assert not any([f._path == path for f in root.newdir._files])

    # TEST DIRECTORY COPYING
    root._dir("new_folder")
    root.texts._copy(root.new_folder)
    assert [d._name for d in root.new_folder._dirs] == ["texts"]

    # TEST DIRECTORY MOVING
    root._dir("newer_folder")
    root.new_folder.texts._move(root.newer_folder)
    assert [d._name for d in root.new_folder._dirs] == []
    assert [d._name for d in root.newer_folder._dirs] == ["texts"]

    # TEST FILE COPYING
    root._dir("newest_folder")
    root.newer_folder.texts.shorts.bla_txt.copy(root.newest_folder)
    assert [f._name for f in root.newest_folder._files] == ["bla.txt"]

    # TEST FILE MOVING
    root._dir("newester_folder")
    root.newer_folder.texts.shorts.bla_txt.move(root.newester_folder)
    assert [f._name for f in root.newester_folder._files] == ["bla.txt"]
    remaining_files = set([d._name for d in root.newer_folder._all_files])
    assert remaining_files == set(["bli.txt", "blu.txt"])


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

    assert set([f._name for f in root._all_files]) == ALL_FILES.union(
        set(["new_file.txt"])
    )
    root.newdir._file("new_file2.txt").write("I am another new file")
    root._close()

    # REOPEN A ZIP
    root = file_tree(zip_path)
    assert set([f._name for f in root._all_files]) == ALL_FILES.union(
        set(["new_file.txt", "new_file2.txt"])
    )

    print(root._tree_view())

    root.newdir._file("new_file_that_doesnt_exist.txt")
    with pytest.raises(NotImplementedError):
        root.newdir._file("new_file.txt")  # overwrite is not supported.

    # Open/read file in zip
    with root.texts.shorts.bla_txt.open("r") as f:
        assert f.read() == "bla bla bla"


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
        fig.savefig(fig_dir._file("fig.png").open("wb"), format="png")
        fig.savefig(fig_dir._file("fig.pdf").open("wb"), format="pdf")
    with file_tree(folder_path) as root:
        fig_dir = root._dir("figures", replace=False)
        fig.savefig(fig_dir._file("fig.png").open("wb"), format="png")  #
        fig.savefig(fig_dir._file("fig.pdf").open("wb"), format="pdf")
    assert set([f._name for f in root._all_files]) == set(["fig.png", "fig.pdf"])
    assert os.path.exists(os.path.join(folder_path, "figures", "fig.pdf"))
