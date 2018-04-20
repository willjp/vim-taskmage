from collections import namedtuple
import enum


class TaskStatus( enum.Enum ):
    todo = 'todo'
    wip  = 'wip'
    done = 'done'
    skip = 'skip'


class Node(object):
    """
    A single node in an Abstract-Syntax-Tree. Nodes are nested to create a view
    of all of the tasks.

    Example:

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


    """
    def __init__(self, _id, ntype, name, data=None, children=None):
        self.name     = name
        self.children = [] # list of nodes
        self.__id     = _id
        self.__type   = ntype
        self.__data   = getattr( NodeData, ntype )

        if data:
            self.__data = data

    def __repr__(self):
        'Node(id={}, type={}, name={}, data={})'.format(
            self.__id,
            self.__type,
            self.name,
            self.data,
        )

    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__type

    @property
    def data(self):
        return self.__data

    @id.setter
    def id(self,id):
        raise AttributeError('Not allowed to set `id`')

    @type.setter
    def type(self,type):
        raise AttributeError('Not allowed to set `type`')

    @data.setter
    def data(self,data):
       if not isinstance( data, type(self.__data) ):
           raise TypeError(
               (
               'Expected `data` to be of type: "{}".\n'
               'Received: "{}"'
               ).format( getattr(NodeData,ntype), type(data) )
           )
        self.__data = data


class NodeData(object):
    class file(tuple):
        def __new__(cls):
            return tuple.__new__(cls)

    class section(tuple):
        def __new__(cls):
            return tuple.__new__(cls)

    class task(tuple):
        def __new__(cls, status, created=None, finished=False, modified=None):
            # TODO: VALIDATE!!!
            return tuple.__new__(cls, (status,created,finished,modified) )


    #def update(self, data, *args, **kwds):
    #    """
    #    Convenience method to update an existing `data` object.
    #    Note that these objects are immutable, so `updating` them
    #    is actually creating/returning a new object.

    #    .. note::
    #        THIS WILL NO LONGER WORK!!! REQUIRES A NAMEDTUPLE
    #    """
    #    new_kwds  = list(data._asdict())

    #    if args:
    #        new_kwds = new_kwds[ len(args) : ]

    #    if kwds:
    #        new_kwds.update(kwds)

    #    return type(data)( *args, collections.OrderedDict(new_kwds) )



