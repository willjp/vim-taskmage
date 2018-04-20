
THE PLAN
========

Debugging my last parser was positively awful.

Using `How to implement a PL`_ as a rough guide on how to properly write a parser,
I have outlined the following plan:


* `data.Node()`: 
    The native datatype of a set of tasks is in an `AST`_ in the form of a 
    nested-set of Nodes. This `AST`_ can comprise of tasks/sections from multiple 
    files, sections ,tasks. Nodes can be converted to one of the other formats
    using a `converter` .


* TaskMage leverages 3x datatypes. Each has it's own lexer.

  * `mtask` : a JSON object (un-nested list of dictionaries). Each dictionary occupies
      a single line, and represents one `token` (file, section, task, ...).

  * `tasklist` : the rst-inspired format you use to create/modify tasks within vim. Limits
      information displayed within vim to the status, id, name. `View` Hierarchy is presented
      as indentation.

  * `taskmetadata` : a YAML-inspired detailed-view of a single task. Shows all information.
      except for children.


* Lexing occurs in 3x steps:
  * ``parser.iostream.ReadStream()`` : simplifies looking ahead/behind to obtain tokens. used in lexer
  * ``parers.lexers.{Mtask|TaskList|TaskDetails}()`` : produces a flat-list of tokens (task, section, etc)
  * ``parsers.parser.Parer()`` : produces a nested hierarchy of ``data.Node()`` objects. (the AST).


.. How to implement a PL_: http://lisperator.net/pltut/parser/

.. AST_: https://en.wikipedia.org/wiki/Abstract_syntax_tree


Node (AST)
----------


.. code-block:: python

    Node(id=.., type='file', name='home/todo.mtask', children=[
        Node(id=.., type='task', name='toplv task', data={}, children=[]),
        Node(id=.., type='section', name='home', data={}, children=[
            Node(id=.., type='task', name='write task parser', data={}, children=[
                Node(id=.., type='task' , name='learn about AST'     , data={} , children=[]) ,
                Node(id=.., type='task' , name='write in pseudocode' , data={} , children=[]) ,
                Node(id=.., type='task' , name='write in real code'  , data={} , children=[]) ,
            ]),
        ])
    ])




Formats
-------


mtask
`````

Most closely ressembles a list of string-tokens. the ``*.mtask`` format represents
a single file. It may not reference other files.


.. code-block:: javascript

    [
        {'id':...,  'type':'section',  'name':'kitchen',       'data':{},     'children':[{id}, {id}, ...] },
        {'id':...,  'type':'task',     'name':'clean dishes',  'data':{...},  'children':[{id}, {id}, ...] },
        ...
    ]



tasklist
````````

.. code-block:: ReStructuredText


    file:home/misc.mtask
    ====================

    * finish task list!
    * push to github

    home
    ----

    * clean appt.
        x clean bathroom
        - wash car # can wait another week
        o wash dishes
        * vaccuum
        * re-organize closet


taskdetails
````````````

.. code-block:: yaml

    name:     wash dishes
    status:   todo
    started:  2018-04-19T19:41:24.547530-04:00 
    finished: null
    notes:

      blah blah blah

      blah blah

