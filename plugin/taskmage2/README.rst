taskmage2
=========

taskmage supports a variety of different formats that can be converted between each other.

* `tasklist`: the ReStructuredText inspired tasklist
* `mtask`:  a JSON file with tasks, and their metadata
* `taskdetails`: (todo) ini-inspired metadata representation

In order to convert between these formats, we use a parser.

* `iostream` abstracts vim-buffers and file-descriptors to a parser-friendly object.
* `lexers` convert various formats to a standardized dictionary
* the `parser` coverts that dictionary into an `asttree.AbstractSyntaxTree` , the foundation of all other formats
* `asttree` can be rendered to various other formats using `asttree.renderers` .


I had a lot of help from http://lisperator.net/pltut/parser/ , and https://en.wikipedia.org/wiki/Abstract_syntax_tree .


Example AST
===========

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



