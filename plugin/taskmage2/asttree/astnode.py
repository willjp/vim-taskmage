import uuid
import sys

from taskmage2.asttree import nodedata
if sys.version_info[0] < 3:  # pragma: no cover
    from taskmage2.vendor import enum
else: # pragma: no cover
    import enum


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

    def __init__(self, _id, ntype, name, data=None, children=None, parent=None):
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

            parent (astnode.Node, optional):
                the parent node, if node has a parent.

        """
        if children is None:
            children = []

        if data is None:
            data = {}

        ntype = NodeType(ntype)
        data_map = dict(self._data_map)

        self.name = name
        self.parent = parent
        self.children = children  # list of nodes
        self.__id = _id
        self._type = ntype
        self._data = data_map[ntype](**data)

    def __repr__(self):
        # get parentid
        parentid = getattr(self.parent, 'id', 'None')

        # string representation
        return 'Node(type={}, name={}, id={}, parentid={})'.format(
            self._type.value,
            self.name,
            self.__id,
            parentid,
        )

    def __eq__(self, obj):
        """ Tests equality of node, and it's children *ignoring it's parent* .
        """
        for attr in ('name', 'children', 'id', 'type', 'data'):
            if getattr(self, attr) != getattr(obj, attr):
                return False
        return True

    def __ne__(self, obj):
        """ Tests inequality of node and it's children *ignoring it's parent* .
        """
        if self.__eq__(obj):
            return False
        return True

    def __getitem__(self, index):
        """
        Args:
            index (int, str):
                either the child's position-index, or it's id.
        """
        if isinstance(index, int):
            return self.children[index]
        for child in self.children:
            if child.id == index:
                return child
        raise KeyError('no child exists with id/index: {}'.format(repr(index)))

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
        """
        Returns:
            nodedata._NodeData:
                nodedata class that corresponds with this nodetype.
        """
        return self._data

    @data.setter
    def data(self, data):
        """ replace this object's nodedata object.

        Args:
            data (nodedata._NodeData):
                accepts a dict, or an already instantiated NodeData object.
        """
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
        """ Finalizes fields, and sets modified-date on this node,
        and all of it's children.
        """
        if self.id is None:
            self.__id = uuid.uuid4().hex.upper()

        # NOTE: NodeData is immutable
        self.data = self.data.touch()

        # also update all children
        for child in self.children:
            child.touch()

    def finalize(self):
        """ Finalizes null-fields where appropriate so node is ready to save.
        Does not change modified-date unless it is not set.
        """
        if self.id is None:
            self.__id = uuid.uuid4().hex.upper()

        # NOTE: NodeData is immutable
        self.data = self.data.finalize()

        # also update all children
        for child in self.children:
            child.finalize()

    def update(self, node):
        """ Merges non-null fields from `node` on top of this one.
        Only changes modified-dates where changes were necessary.

        Args:
            node (taskmage2.asttree.astnode.Node):
                another ast node to merge on top of this one.
        """
        if self.id != node.id:
            raise RuntimeError('cannot update nodes with different ids')

        changed = False
        if self.name != node.name:
            self.name = node.name
            changed = True

        if self._type != NodeType(node.type):
            self._type = NodeType(node.type)
            changed = True

        # data.update() sets changed if it has changed
        _data = self.data.update(node.data)

        # update modified date
        if changed:
            _data = _data.touch()

        self.data = _data
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

    def is_complete(self):
        """ Returns True if self, and all children statuses are in done or skip.
        """
        if self.type == 'section':
            return self._is_section_complete()
        elif self.type == 'task':
            return self._is_taskchain_complete()
        else:
            return False

    def _is_taskchain_complete(self):
        # task completion is determined by task-status
        if self.data.status not in ('done', 'skip'):
            return False

        if not self.children:
            return True

        return self._are_children_complete()

    def _is_section_complete(self):
        # section completion is determined by it's contents.
        # empty sections may be left as placeholders.
        if not self.children:
            return False

        return self._are_children_complete()

    def _are_children_complete(self):
        for child in self.children:
            if not child.is_complete():
                return False
        return True


if __name__ == '__main__':  # pragma: no cover
    pass
