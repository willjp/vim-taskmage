
Under The Hood
==============

A file you are editing that looks like this:

.. code-block:: ReStructuredText

    Trip Home
    =========

    * grocery shopping
      x apples
      x oranges
      * sick supplies for Alex
        for while she isn't feeling well
      - deodorant
        
In reality looks something like this. We use syntax-highlighting to
hide a UUID associated with each task.

.. code-block:: ReStructuredText

    Trip Home
    =========

    *{*40429D679A504ED99F97D0D16067B2B3*} grocery shopping
      x{*E061DCB183EF4C418E97DEE63332C1A0*} apples
      x{*10A71C4E3FCE439A86F1F001BD6BE99D*} oranges
      *{*C96A9133AFC448B2B295451757C5C5EC*} sick supplies for Alex
        for while she isn't feeling well
      -{*EBFEBD42B4894431A3AA048D4AED02B1*} deodorant
        

On-disk, tasklists are saved as JSON objects. Tasks modified in your
file update these JSON objects using their UUID. This serves a dual purpose of:

* keeping metadata out of the way in the tasklist
* storing metadata in an easily accessed format for reports, summaries, or batch operations.

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


Archived tasks are stored in a subdirectory of your root-project. Beyond that,
their format is identical to active tasks in every way.
