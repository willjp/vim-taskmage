
Syntax:
=======

Tasks
-----

    Tasks are treated similarly to ReStructuredText list-items, except that
    additional characters are used to indicate task-status.
    
    .. code-block:: bash
    
    
        *   # todo
        x   # finished
        -   # skipped
        o   # currently in-progress
    
    
    Tasks can be divided into subtasks by indenting them under their parent.
    
    .. code-block:: bash
    
        * clean kitchen
            * dishes
                * cutlery
                    * spoons
                    * forks
                    * knives
    

Sections
--------

    Tasks can be categorized into sections (which take the format of a
    ReStructuredText header). Headers can be nested.
    
    
    .. code-block:: ReStructuredText
    
        * fix mouse scrollwheel
        * water plants
    
        Tommorrow
        =========
    
        work
        ----
    
        * UI for software-updater
        * installer for software-updater 
    
    
        home 
        ----
    
        * christmas shopping
        * taskmage documentation
    
    
        After Tomorrow
        ==============
    
        * package ep110


Comments
--------

    Inline comments (within tasks) are also supported. 
    They are technically a part of the message of a task, but they are 
    syntax-highlighted differently so that they stand out.
    
    .. code-block:: ReStructuredText
    
    
        * do dishes  # start with forks!
                     # then continue with spoons!
    
        * another task
