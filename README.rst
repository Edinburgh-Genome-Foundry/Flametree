.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Flametree/master/docs/logo.png
   :alt: [logo]
   :align: center

Flametree - Python zips and folders made easy
==============================================

.. image:: https://travis-ci.org/Edinburgh-Genome-Foundry/Flametree.svg?branch=master
   :target: https://travis-ci.org/Edinburgh-Genome-Foundry/Flametree
   :alt: Travis CI build status

Flametree is a Python library to read and files in different file systems such as
folders, zip archives, or in-memory ("virtual") archives.

In the following example, we print the content of file ``my_folder/texts/text1.txt``,
then we write some content in a new file ``my_folder/texts/new_file.txt``:

.. code:: python

     from flametree import file_tree
     with file_tree("my_folder") as root:
         print (root.texts.text1_txt.read())
         root.texts._file("new_file.txt").write("I am the file's content.")

The same code also works on a zip archive:

.. code:: python

     with file_tree("my_archive.zip") as root:
         print (root.texts.text1_txt.read())
         root.texts._file("new_file.txt").write("I am the file's content.")

And here is how you create a virtual zip archive in memory, populate it with two
files in different subdirectories, and obtain the archive's binary data,
e.g. for sending it to some distant client. Again, same syntax:

.. code:: python

     with file_tree("@memory") as root:
         root._dir("folder1")._file("report1.txt").write("Some content")
         root._dir("folder2")._file("report2.txt").write("Other content")
         data = root._close()

See below for more examples and features.

Installation
-------------
Flametree should work on any plateform, with Python 2 and 3, and has no external dependency.

It can be installed by unzipping the source code in one directory and using this command: ::

    sudo python setup.py install

You can also install it directly from the Python Package Index with this command: ::

    sudo pip flametree install


Contribute
-----------

Flametree is an open-source software originally written by Zulko_ and released on Github_
under the MIT licence (¢ Edinburgh Genome Foundry). Everyone is welcome to contribute !


Usage
-------

Opening a file tree
~~~~~~~~~~~~~~~~~~~~

For opening a connection to a directory on the disk:

.. code:: python

     from flametree import DirectoryFileTree
     root = DirectoryFileTree(path_to_some_directory)

If the directory does not exist, it will be created. If it exists it is
possible to automatically empty with the option ``replace=True``.

For opening a connection to a zip archive:

.. code:: python

     from flametree import ZipFileTree
     root = ZipFileTree("my_zip_file.zip")

Here too the archive will be created if it doesn't exist, and it will be emptied
by adding  ``replace=True`` to ``ZipFileTree``.

For opening a connection to a Zip archive in memory, represented as a variable
``data``, either a file-like object, or a string or bytes:

.. code:: python

     from flametree import ZipFileTree, ZipFileManager
     root = ZipFileTree(file_manager=ZipFileManager(source=data))

Finally for creating a memory zip archive from scratch

.. code:: python

     root = ZipFileTree("@memory")

To make things simpler Flametree provides the ``file_tree`` method which will
automatically create the right tree class by analyzing the provided target:

.. code:: python

    # target can be 'my_folder', 'archive.zip', '@memory', some_binary_data
    root = file_tree(target)

This is particularly useful when for programs that can accept multi-file data either as
zip or directories, or must produce multi-file results in either zip or folder format.

Exploring a file tree:
~~~~~~~~~~~~~~~~~~~~~~

Once you have created the ``root`` element with one of the methods above, you can display the whole
file tree with `root._tree_view()`:

.. code:: python

    >>> print (root._tree_view())
    texts/
      jokes/
        short_story1.txt
        short_story2.txt
        short_story3.txt
      todo_list.txt
    figures/
      figure1.png
      figure2.png
    Readme.md

The attributes of a directory like ``root`` are its files and subdirectories. For instance to access
 ``short_story1.txt`` and read its content, you would write:

.. code:: python

   print (root.texts.jokes.short_story1_png.read())

This syntactic sugar is particularly useful to explore a file tree in editors with autocompletion,
like IPython Notebooks. Notice that non-alphanumerical caracters such as the
``.`` before ``png``, are replaced by ``_`` to form a valid attribute
name.

Alternatively, you can access files and directories using dictionnary calls:

.. code:: python

    root["texts"]["jokes"]["short_story.png"]

To iterate through the subdirectories of a directory, use the ``_dirs`` attribute:

.. code:: python

    for subdirectory in root._dirs:
        print (subdirectory._name) # Will print 'texts', 'figures'

To iterate through the files of a directory, use the ``_files`` attribute:

.. code:: python

    for f in root.figures._files:
        print (f._name) # Will print 'figure1.png', 'figure1.png'

Finally, use ``_all_files`` to iterate through all files in all directories and
subdirectories. The snippet below prints the content of all ``.txt`` files in the file tree:

.. code:: python

    for f in root._all_files:
        if f._name.endswith(".txt"):
            print (f.read())

Writing in a file tree:
~~~~~~~~~~~~~~~~~~~~~~~~

To create a new subdirectory use ``_dir``:

.. code:: python

    root._dir("data") # create a 'data' folder at the root.

To create a new file use ``_file``:

.. code:: python

    root._file("poem.txt") # create a 'poem.txt' file at the root.

To write content in a file, use ``.write``:

.. code:: python

    root.poem_txt.write("Two roads diverged in a yellow wood.")

These commands can be chained. Let us create folders ``data`` and ``day1``, and
write file ``data/day1/values.csv``, all in a single line:

.. code:: python

    root._dir("data")._dir("day_1")._file("values.csv").write("1, 15, 25, 14")

Keep in mind that ``._dir`` and ``._file`` **overwrite their target by default**, which means
that if you write:

.. code:: python

    root._dir("data")._file("values1.csv").write("1, 15, 25, 14")
    root._dir("data")._file("values2.csv").write("1, 15, 25, 14")

The directory ``data`` will only contain ``values2.csv``, because the second
line's ``_dir("data")`` erases the ``data`` directory and starts a new one. To avoid this,
either write:

.. code:: python

    root._dir("data")._file("values1.csv").write("1, 15, 25, 14")
    root.data._file("values2.csv").write("1, 15, 25, 14")

Or use ``replace=False`` in ``_dir``:

.. code:: python

    root._dir("data")._file("values1.csv").write("1, 15, 25, 14")
    root._dir("data", replace=False)._file("values2.csv").write("1, 15, 25, 14")

To delete a file, use ``_delete``:

.. code:: python

    root.data.values1_csv._delete() # delete file 'values1.csv'
    root.data._delete() # delete directory 'data'

As a last warning, it it not currently possible to modify/delete a file that is
already zipped into an archive (because zips are not really made for that, it
would be doable but would certainly be a hack).

Using files writers
~~~~~~~~~~~~~~~~~~~~

Some libraries have functions which expect a file name or a file object to write too.
You can also feed Flametree files to these functions. for instance here is
how to use Weasyprint to create a PDF ``pdfs/report.pdf``

.. code:: python

    import weasyprint
    from flametree import file_tree
    root = file_tree(".") # or 'archive.zip' to write in an archive.
    html = weasyprint.HTML(string="<b>Hello</b> world!", base_url='.')
    html.write_pdf(root._dir("pdfs")._file("test.pdf"))

And here is how you would save a Matplotlib figure:

.. code:: python

    import matplotlib.pyplot as plt
    from flametree import file_tree
    root = file_tree(".") # or 'archive.zip' to write in an archive.
    fig, ax = plt.subplots(1)
    ax.plot([1, 2, 3], [3, 1, 2])
    fig.savefig(root._dir("plots")._file("figure.png"), format="png")

That's all folks !


.. _Zulko: https://github.com/Zulko/
.. _Github: https://github.com/Edinburgh-Genome-Foundry/flametree
