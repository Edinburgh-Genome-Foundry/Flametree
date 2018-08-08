Flametree
=========


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

Infos
-----

**PIP installation:**

.. code:: bash

  pip install flametree

**Github Page**

`<https://github.com/Edinburgh-Genome-Foundry/Flametree>`_

**License:** MIT, Copyright Edinburgh Genome Foundry
