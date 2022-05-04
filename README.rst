.. raw:: html

    <p align="center">
    <img alt="Flametree Logo" title="Flametree Logo" src="https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Flametree/master/docs/logo.png" width="500">
    </p>
    <h2 align="center"> Python file operations made easy </h2>



.. image:: https://github.com/Edinburgh-Genome-Foundry/Flametree/actions/workflows/build.yml/badge.svg
   :target: https://github.com/Edinburgh-Genome-Foundry/Flametree/actions/workflows/build.yml
   :alt: GitHub CI build status

.. image:: https://coveralls.io/repos/github/Edinburgh-Genome-Foundry/Flametree/badge.svg
   :target: https://coveralls.io/github/Edinburgh-Genome-Foundry/Flametree


Flametree is a Python library which provides a simple syntax for handling files and folders
(no ``os.path.join``, ``os.listdir`` etc.), and works the same way for different file systems.

Write a Flametree program to read/write files in disk folders, and your code will also be
able to read/write in zip archives and virtual (in-memory) archives - which is particularly
useful on web servers.

As an illustration, here is how to use Flametree to read a file ``texts/poems/the_raven.txt``, replace all
occurences of the word "raven" by "seagull" in the text, and write the result to a new
file ``the_seagull.txt`` in the same folder:

.. code:: python

     from flametree import file_tree

     with file_tree("texts") as root:
         poem_text = root.poems.the_raven_txt.read()
         new_text = poem_text.replace("raven", "seagull")
         root.poems._file("the_seagull.txt").write(new_text)

Even in this very simple use case, the syntax is clearer than the ``os`` way,
which would write as follows:

.. code:: python

    import os

    with open(os.path.join("poems", "the_raven.txt"), "r") as f:
        poem_text = f.read()
    new_text = poem_text.replace("raven", "seagull")
    with open(os.path.join("poems", "the_seagull.txt"), "w") as f:
        content = f.write(new_text)

Moreover, the same Flametree code also works for files inside a zip archive:

.. code:: python

     with file_tree("my_archive.zip") as root:
         poem_text = root.poems.the_raven_txt.read()
         new_text = poem_text.replace("raven", "seagull")
         root.poems._file("the_seagull.txt").write(new_text)

Now in hard mode: suppose that your server receives binary zip data of an
archive containing ``poems/the_raven.txt``, and must return back a new zip
containing a file ``poems/the_seagull.txt``. Here again, the syntax of the core
operations is the same:

.. code:: python

     destination_zip = file_tree("@memory") # Create a new virtual zip
     with file_tree(the_raven_zip_data) as root:
         poem_text = root.poems.the_raven_txt.read()
         new_text = poem_text.replace("raven", "seagull")
         destination_zip._dir("poems")._file("the_seagull.txt").write(new_text)
     destination_zip_data = destination_zip._close()
     # Now send the data to the client

See section *Usage* below for more examples and features.

Installation
------------

Flametree should work on Windows/Max/Linux, with Python 2 and 3, and has no external dependency.

It can be installed by unzipping the source code in one directory and using this command: ::

    python setup.py install

You can also install it directly from the Python Package Index with this command: ::

    pip install flametree


Contribute
----------

Flametree is an open-source software originally written by Zulko_ and released on Github_
under the MIT licence (Copyright Edinburgh Genome Foundry).
Everyone is welcome to contribute!
In particular if you have ideas of new kinds of file systems to add to Flametree.


Usage
-----

Opening a file tree
~~~~~~~~~~~~~~~~~~~

Here is how you open different kinds of file systems:

.. code:: python

     from flametree import file_tree

     # Open a directory from the disk's file system:
     root = file_tree("my_folder/")

     # Open a zip archive on the disk:
     root = file_tree("my_archive.zip")

     # Connect to a file-like object (file handle, StringIO...) of a zip:
     root = file_tree(file_like_object)

     # Create a virtual 'in-memory' zip file:
     root = file_tree("@memory")

     # Open some data string representing a zip to read
     root = file_tree(some_big_zip_data_string)



In the two first examples, if ``my_folder`` or ``my_archive.zip`` do not exist, they
will be automatically created. If they do exist, it is possible to completely overwrite
them with the option ``replace=True``.

Exploring a file tree:
~~~~~~~~~~~~~~~~~~~~~~

Once you have created the ``root`` element with one of the methods above, you can display the whole
file tree with ``root._tree_view()`` :

.. code::

    >>> print (root._tree_view())
    texts/
      poems/
        dover_beach.txt
        the_raven.txt
        the_tyger.txt
      todo_list.txt
    figures/
      figure1.png
      figure2.png
    Readme.md


The attributes of a directory like ``root`` are its files and subdirectories.
For instance to print the content of ``dover_beach.txt`` you would write:

.. code:: python

  print( root.texts.poems.dover_beach_txt.read() )

or even simpler:

.. code:: python

    root.texts.poems.dover_beach_txt.print_content()

Notice that the ``.`` before ``txt`` was replaced by ``_`` so as to form a valid
 attribute name.

This syntactic sugar is particularly useful to explore a file tree in
IPython Notebooks or other editors offering auto-completion:


.. image:: https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Flametree/master/docs/autocomplete.png
   :alt: [illustration]
   :align: center

Alternatively, you can access files and directories using dictionary calls:

.. code:: python

    root["texts"]["poems"]["dover_beach.txt"]

To iterate through the subdirectories of a directory, use the ``_dirs`` attribute:

.. code:: python

    for subdirectory in root._dirs:
        print (subdirectory._name) # Will print 'texts' and 'figures'

To iterate through the files of a directory, use the ``_files`` attribute:

.. code:: python

    for f in root.figures._files:
        print (f._name) # Will print 'figure1.png' and 'figure2.png'

Finally, use ``_all_files`` to iterate through all files nested in a directory.
The snippet below prints the content of all ``.txt`` files in the file tree:

.. code:: python

    for f in root._all_files:
        if f._name.endswith(".txt"):
            f.print_content()

Creating files and folders
~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new subdirectory use ``_dir``:

.. code:: python

    root._dir("data") # create a 'data' folder at the root
    root.data._dir("reports") # create a 'reports' folder under `root/data`

To create a new file use ``_file``:

.. code:: python

    root._file("joke.txt") # create a 'joke.txt' file at the root.
    root.texts._file("hello.txt") # create 'hello.txt' in `root/texts`.

To write content in a file, use ``.write``:

.. code:: python

    root.joke_txt.write("A plateau is the highest form of flattery.")

Writing to a file will use mode ``a`` (append) by default. To overwrite
the file set the write mode to ``"w"``. Let's erase and rewrite that ``joke.txt``:

.. code:: python

    root.joke_txt.write("'DNA' stands for National Dyslexic Association.", "w")

File and directory creation commands can be chained.
Let us create some new folders ``data/`` and ``data/test_1/``, and
write to file ``data/test_1/values.csv``, all in a single line:

.. code:: python

    root._dir("data")._dir("test_1")._file("values.csv").write("1,15,25")

Beware that ``._dir`` and ``._file`` **overwrite their target by default**, which means that if you write:

.. code:: python

    root._dir("data")._file("values_1.csv").write("1,4,7")
    root._dir("data")._file("values_2.csv").write("2,9,7")

The directory ``data`` will only contain ``values_2.csv``, because the second
line's ``_dir("data")`` erases the ``data`` directory and starts a new one. To avoid this,
either use ``root.data`` in the second line:

.. code:: python

    root._dir("data")._file("values_1.csv").write("1,4,7")
    root.data._file("values_2.csv").write("2,9,7")

Or use ``replace=False`` in ``_dir``:

.. code:: python

    root._dir("data")._file("values_1.csv").write("1,4,7")
    root._dir("data", replace=False)._file("values_2.csv").write("2,9,7")


Other operations
~~~~~~~~~~~~~~~~

You can move, copy, and delete a file with ``.move(folder)``, ``.copy(folder)``,
``.delete()``, and a directory with ``._move(folder)``, ``._copy(folder)``,
``._delete()``.

.. code:: python

    root.data.values1_csv.delete() # delete file 'values1.csv'
    root.data._delete() # delete directory 'data'
    # Move folder `plots` from `root/figures` to `other_root/figures`
    root.figures.plots._move(other_root.figures)
    # Move file `fig.png` from `root/figures` to `other_root/figures`
    root.figures.fig_png.move(other_root.figures)

Special rules for ZIP archives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is not currently possible to modify/delete a file that is already zipped
into an archive (because zips are not really made for that, it would
be doable but would certainly be a hack).

When creating files and folders in a zip with Flametree, the changes in the actual zip
will only be performed by closing the ``root`` with ``root._close()``
(after which the ``root`` can't be used any more). If it is an in-memory zip, ``root._close()``
returns the value of the zip content as a string (Python 2) or bytes (Python 3).

Here are a few examples:

.. code:: python

    root = file_tree("archive.zip")
    root._file("hello.txt").write("Hi there !")
    root._close()

    # Equivalent to the previous, using `with`:
    with file_tree("archive.zip") as root:
        root._file("hello.txt").write("Hi there !")

    # Getting binary data of an in-memory zip file:
    root = file_tree("@memory")
    root._file("hello.txt").write("Hi there !")
    binary_data = root._close()


Using file writers from other libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some libraries have file-generating methods which expect a file name or a file
object to write too.
You can also feed Flametree files to these functions. for instance here is
how to use Weasyprint to create a PDF ``pdfs/report.pdf``

.. code:: python

    import weasyprint
    from flametree import file_tree
    root = file_tree(".") # or 'archive.zip' to write in an archive.
    html = weasyprint.HTML(string="<b>Hello</b> world!", base_url='.')
    html.write_pdf(root._dir("pdfs")._file("test.pdf"))

And here is how you would save a Matplotlib figure in a zip archive:

.. code:: python

    import matplotlib.pyplot as plt
    from flametree import file_tree
    fig, ax = plt.subplots(1)
    ax.plot([1, 2, 3], [3, 1, 2])
    with file_tree("archive.zip") as root:
        fig.savefig(root._dir("plots")._file("figure.png"), format="png")

That's all folks !


.. _Zulko: https://github.com/Zulko/
.. _Github: https://github.com/Edinburgh-Genome-Foundry/flametree
