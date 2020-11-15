
Commands:
=========

.. contents:: Table of Contents


Projects
---------

.. code-block:: vim

    " Archive fully completed task-chains.
    :TaskMageArchiveCompleted

    " Create a new taskmage project.
    :TaskMageCreateProject


Search
------

.. code-block:: vim


    " Search all tasks for a keyword.
    :TaskMageSearch <keyword>
    
    " List/Filter tasks by date (active implied unless provided)
    :TaskMageLatest active:0 finished:0 modified:>2020-01-01


Search Filters:

========== ================ ========================= =============================
Filter     Format           Example                   Description
========== ================ ========================= =============================
`active:`   0/1              0                        archived/active
`finished:` 0/1              1                        (done/skip) vs (todo/wip)
`modified:` [<>]YYYY-MM-DD   >2020-01-01              last recorded change to task
`created:`  [<>]YYYY-MM-DD   <2020-01-01              task creation date
========== ================ ========================= =============================


Archive
--------

.. code-block:: vim

    " Toggle taskfile/taskfile-archive
    :TaskMageToggle
    :TaskMageSplit
    :TaskMageVSplit

