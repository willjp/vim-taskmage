from taskmage2.asttree import renderers, astnode
from six.moves import UserList


class AbstractSyntaxTree(UserList):
    """

    Example:

        .. code-block:: python

            [
                astnode.Node(id=.., type='file', name='home/todo.mtask', children=[
                    astnode.Node(id=.., type='task', name='toplv task', data={}, children=[]),
                    astnode.Node(id=.., type='section', name='home', data={}, children=[
                        astnode.Node(id=.., type='task', name='write task parser', data={}, children=[
                            astnode.Node(id=.., type='task' , name='learn about AST'     , data={} , children=[]) ,
                            astnode.Node(id=.., type='task' , name='write in pseudocode' , data={} , children=[]) ,
                            astnode.Node(id=.., type='task' , name='write in real code'  , data={} , children=[]) ,
                        ]),
                    ])
                ]),
                astnode.Node(id=.., type='file', name='home/todo.mtask', children=[]),
                ...
            ]

    """
    def __init__(self, data=None):
        if data is None:
            data = []

        for node in data:
            if not isinstance(node, astnode.Node):
                raise TypeError('expected `node` to be of type `taskmage2.astnode.Node`')

        self.data = data

    def render(self, renderer):
        """ Render tree to an output format.

        Args:
            renderer (taskmage2.parser.renderers.Renderer):
                An un-initialized renderer subclass
                that will be used to render this parser
                object.

        Example:

            .. code-block:: python

                >>> tree = ast.AbstractSyntaxTree([
                >>>     astnode.Node(ntype='task', name='task A', ...),
                >>>     astnode.Node(ntype='task', name='task B', ...),
                >>> ])
                >>> tree.render(render.TaskList)
                * task A
                * task B

        Returns:
            The output depends on the renderer.

        """
        if not issubclass(renderer, renderers.Renderer):
            raise TypeError(
                'Must specify output format'
            )

        renderer_instance = renderer(self)
        return renderer_instance.render()

    def touch(self):
        """ Update modified times, create ids if necessary, update metadata.
        """
        for node in self.data:
            node.touch()

    def update(self, other_ast):
        """ Merge changes from another AST on top of this one.
        """
        my_nodes = {}
        for node in self.data:
            my_nodes[node.id] = node

        new_ast = []
        for node in other_ast:
            if node.id in my_nodes:
                my_nodes[node.id].update(node)
                new_ast.append(my_nodes[node.id])
            else:
                new_ast.append(node)

        self.data = new_ast

    def get_completed_taskchains(self):
        """ Returns all top-level nodes whose children statuses are all completed (done, or skip).

        Returns:
            taskmage2.ast.ast.AbstractSyntaxTree:
                an abstractsyntaxtree with only the entirely completed task-chains.
        """
        completed_taskchains = AbstractSyntaxTree()
        for node in self.data:
            if node.is_complete():
                completed_taskchains.append(node)
        return completed_taskchains

    def archive_completed(self, archive_ast=None):
        if archive_ast is None:
            archive_ast = AbstractSyntaxTree()

        # remove completed from active, add to archive
        completed_nodes = self.get_completed_taskchains()

        for node in self.data:
            if node in completed_nodes:
                self.data.remove(node)
                archive_ast.append(node)

        return archive_ast
