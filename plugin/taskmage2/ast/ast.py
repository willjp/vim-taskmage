from taskmage2.ast import renderers, astnode
from six.moves import UserList


class AbstractSyntaxTree(UserList):
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

        renderer_inst = renderer(self)
        return renderer_inst.render()

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
