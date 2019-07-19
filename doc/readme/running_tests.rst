Running Tests
=============

The core of taskmage is pure python. It doesn't know anything about vim, 
and is tested with `pytest` .

The vim-specific portion of taskmage is tested using `vader.vim` .


.. code-block:: bash

    python setup.py test     # runs pytest tests (core)
    python setup.py vimtest  # runs Vader.vim tests (vim-plugin)

