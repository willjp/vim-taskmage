import uuid

import enum
from taskmage2.ast import nodedata


class NodeType(enum.Enum):
    task = 'task'
    section = 'section'
    file = 'file'


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

    _data_map = (
        (NodeType.task,     nodedata.TaskData),
        (NodeType.section,  nodedata.SectionData),
        (NodeType.file,     nodedata.FileData),
    )

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
        data_map = dict(self._data_map)

        self.name = name
        self.children = children  # list of nodes
        self.__id = _id
        self._type = ntype
        self._data = data_map[ntype](**data)

    def __repr__(self):
        return 'Node(id={}, type={}, name={}, data={})'.format(
            self.__id,
            self._type,
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
        return self._type.value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, type(self._data)):
            data_map = dict(self._data_map)
            data_cls = data_map[NodeType(self._type)]
            raise TypeError(
                (
                    'Expected `data` to be of type: "{}".\n'
                    'Received: "{}"'
                ).format(data_cls, type(data))
            )
        self._data = data

    def touch(self):
        """ Adjusts last-modified timestamp, finished status,
        adds id if none assigned, etc.
        """
        if self.id is None:
            self.__id = uuid.uuid4().hex.upper()

        # NOTE: NodeData is immutable
        self.data = self.data.touch()

        # also update all children
        for child in self.children:
            child.touch()

    def update(self, node):
        if self.id != node.id:
            raise RuntimeError('cannot update nodes with different ids')

        self.name = node.name
        self._type = NodeType(node.type)
        self.data = self.data.update(node.data)

        self.children = self._update_children(node)

    def _update_children(self, node):
        # update children now
        my_children = {}
        for child in self.children:
            my_children[child.id] = child

        # handle add/remove and updates
        children = []
        for other_child in node.children:
            if other_child.id in my_children:
                my_children[other_child.id].update(other_child)
                children.append(my_children[other_child.id])
            else:
                children.append(other_child)

        return children

    def is_taskchain_completed(self):
        """ Returns True if all children statuses are in done or skip.
        """
        raise NotImplementedError('todo')

if __name__ == '__main__':
    pass
