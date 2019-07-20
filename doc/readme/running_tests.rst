Running Tests
=============

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

