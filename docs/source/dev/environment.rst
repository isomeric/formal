.. _Git: https://git-scm.com/

.. _environment:

Setting up a Formal Development Environment
===========================================

This is the recommended way to setup a development environment for developing
Formal.

Getting Started
---------------

Here is a summary of the steps to your own development environment:

1. `Fork Formal <https://github.com/isomeric/formal#fork-destination-box>`_
   (*if you haven't done so already*)
2. Clone your forked repository using `Git`_
3. Create a virtual environment
4. Install formal
5. Run tests

And you're done!

Setup
-----

The setup guide shall aid you in setting up a development environment for all
purposes and facettes of Formal development. It is split up in a few parts
and a common basic installation.

Get the sourcecode
^^^^^^^^^^^^^^^^^^

After forking the repository, clone it to your local machine:

.. code-block:: bash

    git clone git@github.com:yourgithubaccount/formal.git ~/src/formal


Setting up a basic development Instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First install the management tool:

.. code-block:: sh

    cd ~/src/formal
    python setup.py install

This installs basic dependencies and Formal itself.
