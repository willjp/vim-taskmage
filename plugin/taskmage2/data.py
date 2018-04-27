from collections import OrderedDict
import enum


class TaskStatus(enum.Enum):
    todo = 'todo'
    wip = 'wip'
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
        self.name = name
        self.children = []  # list of nodes
        self.__id = _id
        self.__type = ntype
        self.__data = getattr(NodeData, ntype)

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
    def id(self, id):
        raise AttributeError('Not allowed to set `id`')

    @type.setter
    def type(self, type):
        raise AttributeError('Not allowed to set `type`')

    @data.setter
    def data(self, data):
        if not isinstance(data, type(self.__data)):
            raise TypeError(
                (
                    'Expected `data` to be of type: "{}".\n'
                    'Received: "{}"'
                ).format(getattr(NodeData, self.__type), type(data))
            )
        self.__data = data


class _namedtuple(tuple):
    def __new__(cls, data):
        if not isinstance(cls._attrs, tuple):
            raise RuntimeError(
                'Each `_namedtuple` must have a `cls._attrs` attribute '
                'with a list of arguments in order'
            )
        if len(cls._attrs) != len(data):
            raise RuntimeError(
                'incorrect number of entries in `_namedtuple`'
            )
        return tuple.__new__(cls, data)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(
                ['{}={}'.format(self._attrs[i], self[i]) for i in range(len(self._attrs))]
            )
        )

    def __getattr__(self, attr):
        if attr not in self._attrs:
            raise AttributeError('Attribute "{}" does not exist on object {}'.format(attr, self.__class__.__name__))
        return self[self._attrs.index(attr)]

    def _asdict(self):
        d = OrderedDict()
        for i in range(len(self._attrs)):
            d[self._attrs[i]] = self[i]
        return d

    def copy(self, *args, **kwds):
        """
        Create a duplicate object of this type,
        optionally modifying it's arguments in the new
        object's constructor.

        Example:

            .. code-block:: python

                class task(_namedtuple):
                    _attrs = ('status','finished')
                    def __new__(cls, status, finished=False):
                        return _namedtuple.__new__(cls, (status,finished))

                t = task('wip')
                >>> task(status='wip', finished=False)

                t.copy(finished=True)
                >>> task(status='wip', finished=True)

        """
        new_kwds = list(self._asdict().items())

        if args:
            new_kwds = new_kwds[len(args):]

        new_kwds = OrderedDict(new_kwds)
        if kwds:
            new_kwds.update(kwds)

        return type(self)(*args, **new_kwds)


class NodeData(object):
    class file(_namedtuple):
        _attrs = tuple()

        def __new__(cls):
            return _namedtuple.__new__(cls, tuple())

        def __repr__(self):
            return 'filedata()'

    class section(_namedtuple):
        _attrs = tuple()

        def __new__(cls):
            return _namedtuple.__new__(cls, tuple())

    class task(_namedtuple):
        _attrs = ('status', 'created', 'finished', 'modified')

        def __new__(cls, status, created=None, finished=False, modified=None):
            # TODO: VALIDATE!!!
            return _namedtuple.__new__(cls, (status, created, finished, modified))
            # return super(task,cls).__new__(cls, (status,created,finished,modified))

    def update(self, data, *args, **kwds):
        """
        Convenience method to update an existing `data` object.
        Note that these objects are immutable, so `updating` them
        is actually creating/returning a new object.

        .. note::
            THIS WILL NO LONGER WORK!!! REQUIRES A NAMEDTUPLE
        """
        new_kwds = list(data._asdict())

        if args:
            new_kwds = new_kwds[len(args):]

        if kwds:
            new_kwds.update(kwds)

        return type(data)(*args, OrderedDict(new_kwds))


if __name__ == '__main__':
    pass
