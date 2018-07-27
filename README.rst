TaskMage
========

A simple plaintext task manager, allowing you to edit tasks in
plaintext lists (quick to edit, no metadata clutter), and store metadata in 
json files (for genrating reports, searching by date, etc). Inspired by git 
and taskwarrior.


.. image:: ./media/screenshot.png



**You Edit a file that looks like this:**

.. code-block:: ReStructuredText

    Trip Home
    =========

    * grocery shopping
      x apples
      x oranges
      * sick supplies for Alex
        for while she isn't feeling well
      - deodorant
        
    Home
    ====

    * finish ZNC server setup
        * write saltstack recipe for ZNC server setup
        * test saltstack recipe



**(Actually you are editing this, details are just hidden):**


.. code-block:: ReStructuredText

    Trip Home
    =========

    *{*40429D679A504ED99F97D0D16067B2B3*} grocery shopping
      x{*E061DCB183EF4C418E97DEE63332C1A0*} apples
      x{*10A71C4E3FCE439A86F1F001BD6BE99D*} oranges
      *{*C96A9133AFC448B2B295451757C5C5EC*} sick supplies for Alex
        for while she isn't feeling well
      -{*EBFEBD42B4894431A3AA048D4AED02B1*} deodorant
        
    ...


**Tasks are saved as JSON objects - metadata is kept out of the way**

.. code-block:: javascript

    [
    {
        "_id":      "40429D679A504ED99F97D0D16067B2B3",
        "section":  "Trip Home",
        "created":  "2017-06-11T22:40:52.460849-04:00",
        "finished": false,
        "text":     "apples",
        "status":   "todo"
    },
    {
        "_id":        "E061DCB183EF4C418E97DEE63332C1A0",
        "parenttask": "40429D679A504ED99F97D0D16067B2B3",
        "created":    "2017-06-11T22:40:52.460849-04:00",
        "finished":   false,
        "text":       "apples",
        "status":     "done"
    },

    //
    // ... and so on ...
    //

    ]




|
|

.. contents:: Table Of Contents

|
|



Usage:
======

.. code-block:: vim

    " create a new taskmage project
    :TaskMageCreateProject

    " create a new taskfile
    :e myfile.mtask      " alternatively from shell:   touch myfile.mtask



Add tasks to the file

.. code-block:: ReStructuredText


    Fiona's wedding
    ===============

    * make beanbags for yard-game
      * find sewing machine
      * purchase fabric


    Work
    ====

    * package ep100
    * finish browser UI
     


.. code-block:: vim

    " save the file (saved in JSON, reopens as Rst)
    :w


    " Over time, as you have collected several finished
    " tasks, archive them (move them to 
    " ``.taskmage/{filename}.mtask``
    :TaskMageArchiveCompleted


Personally, I store all of these in a git project, so that 
I can easily sync tasks across all of my computers.




Syntax:
=======

Task-data is stored in json-formatted files assigned the extension ``.mtask``.
With this plugin enabled, opening one of these files using vim parses that file,
and replaces the loaded buffer with a ReStructuredText inspired task-list.

Instead of only using ``*`` as the list marker, I have added a few others
which contain special meaning:

.. code-block:: bash


    *   # todo
    x   # finished
    -   # skipped
    o   # currently active task

In order to create new tasks, simply add them to the file.
Every time the file is saved, it is parsed/converted back to JSON,
the ``.mtask`` file is updated, and the current ReStructuredText formatted
file is reloaded.


Sections
--------

Tasks can be categorized into sections (which take the format of a
ReStructuredText header). This is purely for convenience. Currently
sections cannot be nested (sorry).


.. code-block:: ReStructuredText

    * fix mouse scrollwheel
    * water plants

    Tommorrow
    =========

    * christmas shopping
    * taskmage documentation


    Work
    ====

    * package ep110


Task Hierarchy
--------------

Task Hierarchies can be established simply by indenting tasks
underneath another. This information is stored in the JSON file,
so that other views/reports into the data can be created.

.. code-block:: ReStructuredText


    * do the laundry

    * clean the kitchen

      * wash the floors
      * clean the inside of the oven
        * find oven cleaner
        * clean

        * a really long task
          that takes multiple lines

          with some space in the middle


Comments
--------

Inline comments (within tasks) are also supported.
My intention for this is a means of writing yourself
little notes about tasks, that are highlighted differently.

.. code-block:: ReStructuredText


    * do dishes  # start with forks!
                 # then continue with spoons!

    * another task





Project:
========

Like git, taskmage uses a directory to indicate both a project-root,
and store completed task-data. 


.. code-block:: python

    /home/todo/.taskmage/

        completed/                # bulk-storage of completed tasks

            module_name/
                section1.mtask
                section2.mtask
                section3.mtask
                ...
            module_name/
                section1.mtask
                section2.mtask
                ...



