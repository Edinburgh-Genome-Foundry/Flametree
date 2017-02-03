.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Flametree/master/docs/logo.png
   :alt: [logo]
   :align: center

Flametree - Zips and folders made easy
========================================

Flametree is a Python library providing a very simple syntax to write, read,
and explore file systems such as disk folders, zip archives, and in-memory zip
archives and im-memory ("virtual") zip archives.

For example, in the following snippet, we first read and print the content of
file ``my_folder/texts/text1.txt``, then we create a new file
``my_folder/texts/text2.txt`` with some content:

.. code:: python

     from flametree import file_tree
     with file_tree("my_folder") as root:
         print (root.texts.text1_txt.read())
         root.texts._file("new_text.txt").write("I am the file's content.")

Now with the same syntax we can do the same inside a zip archive:

.. code:: python

     with file_tree("my_archive.zip") as root:
         print (root.texts.text1_txt.read())
         root.texts._file("new_text.txt").write("I am the file's content.")

And here is how you would create a zip archive *in memory*, populate it with two
files in different subdirectories, and obtain the archive's binary data,
e.g. for sending it to some distant client. Again, same syntax:

.. code:: python

     with file_tree("@memory") as root:
         root._dir("new_dir")._file("new_file.txt").write("Some content")
         root._dir("other_dir")._file("other_file.txt").write("Other content")
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

     from flametree import DirectoryFilesTree
     root = DirectoryFilesTree(path_to_some_directory)

If the directory does not exist, it will be created. If it exists it is
possible to automatically empty by adding ``replace=True`` to the command.

For opening a connection to a zip archive:

.. code:: python

     from flametree import ZipFilesTree
     root = ZipFilesTree("my_zip_file.zip")

Here too the archive will be created if it doesn't exist, and it will be emptied
by adding  ``replace=True`` to ``ZipFilesTree``.

For opening a connection to a Zip archive in memory, represented as a variable
``data``, either a file-like object, or a string or bytes:

.. code:: python

     from flametree import ZipFilesTree, ZipFilesManager
     root = ZipFilesTree(files_manager=ZipFilesManager(source=data))

Finally for creating a memory zip archive from scratch

.. code:: python

     root = ZipFilesTree("@memory")

To make things simpler Flametree provides the ``files_tree`` method which will
automatically create the right tree class by analyzing the provided target:

.. code:: python

    # target can be 'my_folder', 'archive.zip', '@memory', some_binary_data
    root = files_tree(target)

This is particularly useful when for programs that can accept multi-file data either as
zip or directories, or must produce multi-file results in either zip or folder format.

Exploring a file tree:
~~~~~~~~~~~~~~~~~~~~~~

Once you have created the ``root`` element with one of the methods above, you can display the whole
file system with `root._tree_view()`:

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

This whole tree is also contained in ``root`` as a series of nested objects, so for instance to
reach file ``short_story1.txt``, you would write ``root.texts.jokes.short_story1_png``.
And here is how you print the content of that file:

.. code:: python

   print (root.texts.jokes.short_story1_png.read())


Notice that non-alphanumerical caracters such as ``.`` are replaced by ``_`` to give a valid attribute
name. This feature is particularly useful to explore a file tree when using an editor with autocompletion,
e.g. an IPython Notebook, but may not work with all use cases. Alternatively, you can access the file using
dictionnary calls:

.. code:: python

    root["texts"]["jokes"]["short_story.png"]

You can iterate through the subdirectories of a directory using the ``_dirs`` attribute, for instance:

.. code:: python

    for subdir in root._dirs:
        print (dir._name) # Will print 'texts', 'figures'

You can iterate through the files of a directory using the ``_files`` attribute, for instance:


.. code:: python

    for f in root.figures._files:
        print (f._name) # Will print 'figure1.png', 'figure1.png'

Finally ``_all_files`` gives you access to all files in all directories and
subdirectories. For instance here is how you display the content of all text files
under the root folder:

.. code:: python

    for f in root._all_files:
        if f._name.endswith(".txt"):
            print (f.read())

Writing in a file tree:
~~~~~~~~~~~~~~~~~~~~~~~~

To create a new subdirectory use the ``._dir('dir_name')`` command.
To create a new file, use the ``._file('file_name')`` command.
To write in a file, use the ``.write(content)`` command.
These commands can be chained, so for instance if you want to write a file ``data/day_1/values.csv``
you will use:

.. code:: python

    root._dir("data")._dir("day_1")._file("values.csv").write("1, 15, 25, 14")

Keep in mind that ``._dir`` and ``._file`` **overwrite by default**, which means
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

    root.data.values1_csv._delete() # delete file 'values1.csv'
    root.data._delete() # delete directory 'data'

As a last warning, it it not currently possible to modify/delete a file that is
already zipped into an archive (but that's not a big problem as zips are used
mostly to read from or writes new files to).

Using files writers
~~~~~~~~~~~~~~~~~~~~

Some libraries have functions which expect a file name or a file object to write too.
You can also feed Flametree files to these functions. for instance here is
how to use Weasyprint to create a PDF ``pdfs/report.pdf``

.. code:: python

    import weasyprint
    from flametree import files_tree
    root = files_tree(".") # or 'archive.zip' to write in an archive.
    html = weasyprint.HTML(string="<b>Hello</b> world!", base_url='.')
    html.write_pdf(root._dir("pdfs")._file("test.pdf"))

And here is how you would save a Matplotlib figure:

.. code:: python

    import matplotlib.pyplot as plt
    from flametree import files_tree
    root = files_tree(".") # or 'archive.zip' to write in an archive.
    fig, ax = plt.subplots(1)
    ax.plot([1, 2, 3], [3, 1, 2])
    fig.savefig(root._dir("plots")_file("figure.png"), format="png")




.. _Zulko: https://github.com/Zulko/
.. _Github: https://github.com/Edinburgh-Genome-Foundry/flametree
