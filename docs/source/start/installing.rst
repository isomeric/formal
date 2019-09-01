.. _complex_install:

Installing
==========

Formal itself
-------------

Here is a summary of the steps to your own development environment:

1. `Fork Formal <https://github.com/isomeric/formal#fork-destination-box>`_
   (*if you haven't done so already*)
2. Clone your forked repository using `Git`_
3. Create a virtual environment
4. Install formal
5. Run tests

And you're done!

Documentation
-------------

The documentation is available online on `ReadTheDocs.org
<https://formal.readthedocs.org>`__.
If you wish to build the included documentation for offline use,
run these commands:

.. code-block:: sh

    python setup.py build_sphinx

You can also build the PDF file (and various other formats) by using the
Makefile inside the docs directory.

.. code-block:: sh

    cd docs
    make pdf

Just running make without arguments gives you a list of the other available
documentation formats.

Windows & OS X installation notes
---------------------------------
*These instructions are WiP. The easiest way to get Formal on Win7 or newer
is to install and user Docker or a virtual machine*

To install on Windows, you'll need to install these packages first:

 * Python >=3.4 https://www.python.org/downloads/windows/
 * MongoDB https://www.mongodb.org/downloads#production
 * pymongo
 * sqlalchemy
