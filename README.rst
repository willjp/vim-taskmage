TaskMage
========

.. image:: https://travis-ci.com/willjp/vim-taskmage.svg?branch=master
    :target: https://travis-ci.com/willjp/vim-taskmage

.. image:: https://codecov.io/gh/willjp/vim-taskmage/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/willjp/vim-taskmage


A simple plaintext task manager, allowing you to edit tasks in
plaintext lists (quick to edit, no metadata clutter), and store metadata in 
json files (for genrating reports, searching by date, etc). Inspired by git 
and taskwarrior.


.. image:: ./media/screenshot.png


Install
=======

Prerequisistes
--------------

Your vim must be compiled with python (2 or 3). Run the following command
from a console - if a line is returned, your vim was built with python support.

.. code-block:: bash

    vim --version | grep '+python'     # unix
    vim --version | find /I "+python"  # windows


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

* sphinx_documentation
* running_tests_
* under_the_hood_
* future_ideas_
* similar_projects_


.. _running_tests: ./doc/readme/running_tests.rst
.. _under_the_hood: ./doc/readme/under_the_hood.rst
.. _future_ideas: ./doc/readme/future_ideas.rst
.. _similar_projects: ./doc/readme/similar_projects.rst
