README.rst
==========

A simple plaintext task manager

.. note:

    TO DOCUMENT:

    Lines beginning with a #, that is not a part
    of a title's underline are considered comments
    and ignored



Requires:
========

.. note::

    Nope, screw that, conceal is builtin to the vim helpfiles,
    and I can simply use a custom syntaxhighlighting file
    to do what I need :)



vim plugins:
    * Glaive_       (required by foldcol)
    * foldcol.vim_  (to be integrated)


_Glaive:      https://github.com/paulhybryant/foldcol
_foldcol.vim: https://github.com/paulhybryant/foldcol

.. code-block:: vimrc

    # install using vundle
    Plugin 'https://github.com/paulhybryant/foldcol'
    Plugin 'google/vim-maktaba'
    Plugin 'google/vim-glaive'
    Plugin 'google/vim-codefmt'




The Plan
========

Internally, all data is stored in YAML files.
When the todo command is issued, a plaintextfile is generated
from the current datafiles, that the user can edit. Changes to this
file are recorded back into the yaml files.

For the moment, we will completely ignore prerequisites,
and any sort of priority.



.. code-block:: bash

    $todo/<filename>.yml                           ## current todos
    $todo/__completed__/<filename>/<section>.yml   ## completed todos



.. code-block:: yaml

    8bbbe14d6ab74516a68a3366cb53cf33:
        section:  misc                                ## only assigned if no parent task
        parent:   a96c2c16855c4ce3b0d41d79340319c8    ## any parent-task (it's all just tasks)
        created:  '2017-06-11T14:31:47.805790-04:00' 
        finished: null
        text: |
            Make sure to do blah and blah.


.. code-block:: vimrc

    ## within the vim file, we will use the vim plugin:  foldcol.vim
    ## to perform an inline, horizontal fold. This way all of the data
    ## will be packaged and editable within the vim file, but it will
    ## still appear like a plaintext list, and users can use their preferred
    ## vim keybindings.

    ## Looks like

    * Make sure to do blah and blah

    ## but is actually    
    {* uuid:8bbbe14d6ab74516a68a3366cb53cf33 *} Make sure to do blah and blah

    ## new files can be created that would expose one note at a
    ## time with all of the yaml fields (if you wanted to edit
    ## start/end times or individual work sessions.
    ## (hotkeys should probably be provided to edit dates etc)
    ## (looots of validation)

    8bbbe14d6ab74516a68a3366cb53cf33:
        created:  '2017-06-11T14:31:47.805790-04:00' 
        finished: null
        text: |
            Make sure to do blah and blah.




