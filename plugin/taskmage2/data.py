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
        """
        Constructor.

        .. note::
            AST Nodes don't care about the level of indent, or the parent.
            All they are concerned with is the type, name, data, and if
            it has any children. Indents will be assigned in their native
            format if applicable.
        """

        if children is None:
            children = []

        self.name = name
        self.children = children  # list of nodes
        self.__id = _id
        self.__type = ntype
        self.__data = getattr(NodeData, ntype)

        if data:
            self.__data = data

    def __repr__(self):
        return 'Node(id={}, type={}, name={}, data={})'.format(
            self.__id,
            self.__type,
            self.name,
            self.data,
        )

    def __eq__(self, obj):
        if not isinstance(obj, Node):
            raise TypeError('Invalid comparison')

        for attr in ('name', 'children', 'id', 'type', 'data'):
            if getattr(self, attr) != getattr(obj, attr):
                return False
        return True

    def __ne__(self, obj):
        if self.__eq__(obj):
            return False
        return True

    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__type

    @property
    def data(self):
        return self.__data

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
    """
    A class prototype for custom namdetuples.

    The attribute :py:attr:`_attrs` determines the
    namdetuple properties.

    Example:

        .. code-block:: python

            class TaskData(_namedtuple):
                _attrs = ('status', 'created')

            status = TaskData(status='done', created=datetime.datetime(..))
            print(status.status)
            >>> 'done'

            print(status.created)
            >>> datetime.datetime(...)

    """
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
    """
    This object is the interface for :py:attr:`taskmage2.data.Node.data` ,
    it exposes namedtuples for each nodetype, and allows them to be updated.

    Attributes:

        file (taskmage2.data._namedtuple):
            namedtuple class, for storing ``file`` Node data.

        section (taskmage2.data._namedtuple):
            namedtuple class, for storing ``section`` Node data.

        task (taskmage2.data._namedtuple):
            namedtuple class, for storing ``task`` Node data.

    """
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

#    def update(self, data, *args, **kwds):
#        """
#        Convenience method to update an existing `data` object.
#        Note that these objects are immutable, so `updating` them
#        is actually creating/returning a new object.
#
#        .. note::
#            THIS WILL NO LONGER WORK!!! REQUIRES A NAMEDTUPLE
#        """
#        new_kwds = list(data._asdict())
#
#        if args:
#            new_kwds = new_kwds[len(args):]
#
#        if kwds:
#            new_kwds.update(kwds)
#
#        return type(data)(*args, OrderedDict(new_kwds))


if __name__ == '__main__':
    pass
