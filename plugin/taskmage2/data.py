import collections
import uuid
import datetime
import enum
from dateutil import tz


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
        """ Constructor.

        .. note::
            AST Nodes don't care about the level of indent, or the parent.
            All they are concerned with is the type, name, data, and if
            it has any children. Indents will be assigned in their native
            format if applicable.

        Args:
            _id (str, optional): ``(ex: '6a027ca647644d70ab05458fdc99378c')``
                uuid assigned to node.

            ntype (str, taskmage2.data.NodeType): ``(ex: 'task', 'section', 'file', TaskType.task )``
                type of node this object will represent.

            name (str): ``(ex: 'clean dishes' )``
                the name of the task, file, section etc.

            data (dict, optional):
                metadata associated with the node. format varies by nodetype.

            children (list, optional):
                list of :py:obj:`taskmage2.data.Node` objects with a child
                relationship to this node.

        """

        if children is None:
            children = []

        if data is None:
            data = {}

        ntype = NodeType(ntype)
        data_map = {
            NodeType.task:     TaskData,
            NodeType.section:  SectionData,
            NodeType.file:     FileData,
        }

        self.name = name
        self.children = children  # list of nodes
        self.__id = _id
        self.__type = ntype
        self.__data = data_map[ntype](**data)

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
        """
        Returns:
            str: the nodetype.
        """
        return self.__type.value

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

    def touch(self):
        """ Adjusts last-modified timestamp, finished status,
        adds id if none assigned, etc.
        """
        utcnow = datetime.datetime.now(tz.UTC)
        if self.id is None:
            self.__id = uuid.uuid4().hex.upper()

        if self.type is 'task':
            self.data.modified = utcnow

            if self.data.status is None:
                self.data.status = 'todo'

            if self.data.created is None:
                self.data.created = utcnow

            # finished
            if all([
                self.data.status in ('done', 'skip'),
                self.data.finished is not False,
            ]):
                self.data.finished = utcnow
            else:
                self.data.finished = False


class NodeType(enum.Enum):
    task = 'task'
    section = 'section'
    file = 'file'


class _NodeData(tuple):
    """ A class prototype for custom namdetuples.

    The attribute :py:attr:`_attrs` determines the
    namdetuple properties.

    Example:

        .. code-block:: python

            class TaskData(_NodeData):
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
                'Each `_NodeData` must have a `cls._attrs` attribute '
                'with a list of arguments in order'
            )
        if len(cls._attrs) != len(data):
            raise RuntimeError(
                'incorrect number of entries in `_NodeData`'
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

    def as_dict(self):
        d = collections.OrderedDict()
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

                >>> class task(_NodeData):
                >>>     _attrs = ('status','finished')
                >>>     def __new__(cls, status, finished=False):
                >>>         return _NodeData.__new__(cls, (status,finished))

                >>> t = task('wip')
                task(status='wip', finished=False)

                >>> t.copy(finished=True)
                task(status='wip', finished=True)

        """
        new_kwds = list(self.as_dict().items())

        if args:
            new_kwds = new_kwds[len(args):]

        new_kwds = collections.OrderedDict(new_kwds)
        if kwds:
            new_kwds.update(kwds)

        return type(self)(*args, **new_kwds)


class FileData(_NodeData):
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())


class SectionData(_NodeData):
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())


class TaskData(_NodeData):
    _attrs = ('status', 'created', 'finished', 'modified')

    def __new__(cls, status, created=None, finished=False, modified=None):
        if finished is None:
            finished = False

        if status not in ('todo', 'skip', 'done', 'wip'):
            raise TypeError('status')

        if created is not None:
            if not isinstance(created, datetime.datetime):
                raise TypeError('created')
            elif not created.tzinfo:
                raise TypeError('created')

        if finished is not False:
            if not isinstance(finished, datetime.datetime):
                raise TypeError('finished')
            elif not finished.tzinfo:
                raise TypeError('finished')

        if modified is not None:
            if not isinstance(modified, datetime.datetime):
                raise TypeError('modified')
            elif not modified.tzinfo:
                raise TypeError('modified')

        return _NodeData.__new__(cls, (status, created, finished, modified))


if __name__ == '__main__':
    pass
