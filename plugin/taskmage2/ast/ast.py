
from six.moves import UserList


class AbstractSyntaxTree(UserList):
    def __init__(self, data=None):
        if data is None:
            data = []

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
        pass

    def update(self, ast):
        pass
