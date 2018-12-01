
examples/raw
============

The files contained here are files in their raw formats.
If you have this plugin enabled, in order to see their
contents properly you might want to use the unix CLI tool
`less`.

I'll unpack that a bit. When using this plugin,
you:

* Load a ``*.ptask`` file (JSON).

* After loading, the JSON file is replaced with
  a restructured-text style todo list. Ids
  are added at the start of each line
  in between the markers ``{*`` and ``*}`` .

* this file is displayed to the user using
  special syntax-highlighting that hides the Ids.
  

.. code-block:: bash

    less examples/raw/work.ptaskdata
    less examples/raw/work_valid.ptask



* ``*.ptaskdata`` files represent the data that gets
  stored on disk. These files are in the format of a list of JSON
  objects.

* ``*.ptask`` files represent the files that the user
  is actually editing within vim. These files approximate
  the format of a ReStructuredText list.


