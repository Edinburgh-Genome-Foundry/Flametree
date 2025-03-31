import os
import sys
from flametree import file_tree, DiskFileManager, ZipFileManager
import pytest

# THIRD PARTY LIBS BEING TESTED
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import weasyprint
import pandas

PYTHON3 = sys.version_info[0] == 3


def test_weasyprint(tmpdir):
    path = str(tmpdir)
    root = file_tree(str(tmpdir))  # or 'archive.zip' to write in an archive.
    html = weasyprint.HTML(string="<b>Hello</b> world!", base_url=".")
    html.write_pdf(root._dir("pdfs")._file("test.pdf"))
    with open(os.path.join(path, "pdfs", "test.pdf"), "rb") as f:
        filesize = len(f.read())
        assert 4000 < filesize


def test_matplotlib(tmpdir):
    path = str(tmpdir)
    root = file_tree(path)
    fig, ax = plt.subplots(1)
    fig.savefig(root._file("fig1.png").open("wb"), format="png")
    with PdfPages(root._file("plots.pdf").open("wb")) as pdf_io:
        for i in range(3):
            fig, ax = plt.subplots(1)
            pdf_io.savefig(fig)
            plt.close(fig)
    with open(os.path.join(path, "fig1.png"), "rb") as f:
        filesize = len(f.read())
        assert filesize > 7000
    with open(os.path.join(path, "plots.pdf"), "rb") as f:
        filesize = len(f.read())
        assert filesize > 6000


def test_pandas(tmpdir):
    path = str(tmpdir)
    root = file_tree("@memory")
    root._file("test.csv").write("A,B,C\n1,2,3\n4,5,6")
    dataframe = pandas.read_csv(root.test_csv.open("r"))
