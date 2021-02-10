Running Tests
=============

Quickstart
----------

The core of taskmage is pure python. It doesn't know anything about vim, 
and is tested with `pytest` .

The vim-specific portion of taskmage is tested using `vader.vim` .


.. code-block:: bash

    python setup.py test_python [--addopts [...]]   # runs pytest tests (core)
    python setup.py test_vm [-i]                    # runs vader.vim tests (core)
    python setup.py test                            # runs all tests

    python setup.py coverage_python                 # reports python test-coverage
    python setup.py coverage_vim                    # reports vim test-coverage
    python setup.py coverage [--xml]                # reports both, combines into .coverage file



Interpreted Environment
-----------------------

If you're running Linux/MacOs, you can also use `nix`_ to resolve an 
environment with a python interpreter and requirements. 

.. code-block:: bash

    nix-shell   # enter nix-shell
    pytest      # run python tests

You may find it useful to further customize the nix-shell environment to add
linters/refactoring tools etc. Simply copy ``shell.nix.example`` to ``shell.nix`` and customize to your liking.

.. _nix: https://nixos.org/

