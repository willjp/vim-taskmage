
class View():
    """
    The native format of tasks, once they have been parsed.

    This represents what is actually displayed within vim. It might
    represent a single file, or comprise of several files.

    Example:

        .. code-block:: python

            from .data import token

            View([
                token(type='file', name='home/todo.mtask', children=[
                    token(type='task', name='toplv task', data={}, children=[]),
                    token(type='section', name='home', data={}, children=[
                        token(type='task', name='write task parser', data={}, children=[
                            token(type='task' , name='learn about AST'     , data={} , children=[]) ,
                            token(type='task' , name='write in pseudocode' , data={} , children=[]) ,
                            token(type='task' , name='write in real code'  , data={} , children=[]) ,
                        ]),
                    ])
                ])
            ])

    """
    pass



