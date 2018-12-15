import pytest
import mock

from taskmage2.ast import ast, astnode, renderers


class FakeNode(object):
    update = mock.Mock()

    def __init__(self, id_):
        self.id = id_

    def __eq__(self, id_):
        return id_ == self.id


@pytest.fixture
def renderer():
    class Renderer(renderers.Renderer):
        render_calls = 0
        def __init__(self, *args, **kwargs):
            super(Renderer, self).__init__(*args, **kwargs)

        @classmethod
        def render(cls):
            cls.render_calls += 1

    return Renderer


class Test_AbstractSyntaxTree(object):
    def test_render_invalid_renderer(self):
        with pytest.raises(TypeError):
            self.render('invalid renderer')

    def test_render_valid(self, renderer):
        self.render(renderer)
        assert renderer.render_calls == 1

    def test_touch(self):
        AST = ast.AbstractSyntaxTree()
        AST.data = [mock.Mock(), mock.Mock()]

        AST.touch()
        assert all([node.touch.called for node in AST])

    def test_update_removes_nodes(self):
        AST_A = ast.AbstractSyntaxTree()
        AST_A.data = [FakeNode('1'), FakeNode('2'), FakeNode('3')]

        AST_B = ast.AbstractSyntaxTree()
        AST_B.data = [FakeNode('1'), FakeNode('3')]

        AST_A.update(AST_B)
        assert AST_A.data == [FakeNode('1'), FakeNode('3')]

    def test_update_adds_nodes(self):
        AST_A = ast.AbstractSyntaxTree()
        AST_A.data = [FakeNode('1'), FakeNode('2')]

        AST_B = ast.AbstractSyntaxTree()
        AST_B.data = [FakeNode('1'), FakeNode('2'), FakeNode('3')]

        AST_A.update(AST_B)
        assert AST_A.data == [FakeNode('1'), FakeNode('2'), FakeNode('3')]

    def test_update_performs_nodeupdate(self):
        AST_A = ast.AbstractSyntaxTree()
        AST_A.data = [FakeNode('1')]

        AST_B = ast.AbstractSyntaxTree()
        AST_B.data = [FakeNode('1')]

        AST_A.update(AST_B)
        assert AST_A[0].update.called_with(AST_B[0])

    def test_update_performs_nodeupdate_when_order_mixed(self):
        AST_A = ast.AbstractSyntaxTree()
        AST_A.data = [FakeNode('1'), FakeNode('2')]

        AST_B = ast.AbstractSyntaxTree()
        AST_B.data = [FakeNode('2'), FakeNode('1')]

        AST_A.update(AST_B)
        assert AST_A[0].update.called_with(AST_B[1])
        assert AST_A[1].update.called_with(AST_B[0])

    def test_update_keeps_new_order(self):
        AST_A = ast.AbstractSyntaxTree()
        AST_A.data = [FakeNode('1'), FakeNode('2')]

        AST_B = ast.AbstractSyntaxTree()
        AST_B.data = [FakeNode('2'), FakeNode('1')]

        AST_A.update(AST_B)
        assert AST_A.data == [FakeNode('2'), FakeNode('1')]

    def test_get_completed_taskchains(self):
        """ Retrieve all top-level task-nodes whose self/children are all completed.
        """
        complete_node = mock.Mock()
        complete_node.is_complete = mock.Mock(return_value=True)

        incomplete_node = mock.Mock()
        incomplete_node.is_complete = mock.Mock(return_value=False)

        AST = ast.AbstractSyntaxTree()
        AST.data = [complete_node, incomplete_node]

        completed = AST.get_completed_taskchains()
        assert completed.data == [complete_node]

    def test_archive_completed_tasks_only(self):
        data = [mock.Mock(), mock.Mock(), mock.Mock()]
        completed = [data[1]]

        AST = ast.AbstractSyntaxTree()
        AST.data = data[:]
        with mock.patch(
            '{}.AbstractSyntaxTree.get_completed_taskchains'.format(ast.__name__),
            return_value=completed
        ):
            archive_ast = AST.archive_completed()

        assert archive_ast.data == [data[1]]
        assert AST.data == [data[0], data[2]]

    def render(self, renderer):
        tree = ast.AbstractSyntaxTree([
            astnode.Node(
                _id='',
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
            )
        ])
        tree.render(renderer)
