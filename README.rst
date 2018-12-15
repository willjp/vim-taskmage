TaskMage
========

A simple plaintext task manager, allowing you to edit tasks in
plaintext lists (quick to edit, no metadata clutter), and store metadata in 
json files (for genrating reports, searching by date, etc). Inspired by git 
and taskwarrior.


.. image:: ./media/screenshot.png


Install
=======

Prerequisistes
--------------

Your vim must be compiled with python (2 or 3). Check this using the command
(if nothing is returned, your vim was not compiled with python support).

.. code-block:: bash

    vim --version | grep '+python'     # unix
    vim --version | find /I "+python"  # windows


You'll also need to add the following dependencies to the python-interpreter
that vim uses for the ``py`` call.

Find python-interpreter used by vim using this command inside vim.

.. code-block:: vim

    :py import sys;print(sys.executable)


Install
-------

After setting up a vim plugin-manager like vundle_, pathogen_, etc. Add this plugin
to your ``~/.vimrc`` .

.. code-block:: vim

    Plugin 'https://github.com/willjp/vim-taskmage'



.. _vundle: https://github.com/vim-scripts/vundle
.. _pathogen: https://github.com/tpope/vim-pathogen


Instructions
============


* usage_
* syntax_
* projects_

.. _usage: ./doc/readme/usage.rst
.. _syntax: ./doc/readme/syntax.rst
.. _projects: ./doc/readme/projects.rst


Misc
====

* under_the_hood_
* future_ideas_

.. _under_the_hood: ./doc/readme/under_the_hood.rst
.. _future_ideas: ./doc/readme/future_ideas.rst
