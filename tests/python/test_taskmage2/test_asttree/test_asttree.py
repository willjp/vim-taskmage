import pytest
import mock

from taskmage2.asttree import asttree, astnode, renderers


class Not_A_Renderer(object):
    pass


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
    class Test__init__:
        def test_raises_typeerror_on_invalid_data(self):
            with pytest.raises(TypeError):
                asttree.AbstractSyntaxTree(['a', 'b'])

    class Test_render:
        def test_render_invalid_renderer(self):
            tree = asttree.AbstractSyntaxTree([
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
            with pytest.raises(TypeError):
                tree.render(Not_A_Renderer)

        def test_render_valid(self, renderer):
            tree = asttree.AbstractSyntaxTree([
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

            assert renderer.render_calls == 1

    class Test_touch:
        def test_children_run_touch(self):
            AST = asttree.AbstractSyntaxTree()
            AST.data = [mock.Mock(), mock.Mock()]

            AST.touch()
            assert all([node.touch.called for node in AST])

    class Test_finalize:
        def test_children_run_finalize(self):
            AST = asttree.AbstractSyntaxTree()
            AST.data = [mock.Mock(), mock.Mock()]

            AST.finalize()
            assert all([node.finalize.called for node in AST])

    class Test_update:
        def test_update_removes_nodes(self):
            AST_A = asttree.AbstractSyntaxTree()
            AST_A.data = [FakeNode('1'), FakeNode('2'), FakeNode('3')]

            AST_B = asttree.AbstractSyntaxTree()
            AST_B.data = [FakeNode('1'), FakeNode('3')]

            AST_A.update(AST_B)
            assert AST_A.data == [FakeNode('1'), FakeNode('3')]

        def test_update_adds_nodes(self):
            AST_A = asttree.AbstractSyntaxTree()
            AST_A.data = [FakeNode('1'), FakeNode('2')]

            AST_B = asttree.AbstractSyntaxTree()
            AST_B.data = [FakeNode('1'), FakeNode('2'), FakeNode('3')]

            AST_A.update(AST_B)
            assert AST_A.data == [FakeNode('1'), FakeNode('2'), FakeNode('3')]

        def test_update_performs_nodeupdate(self):
            AST_A = asttree.AbstractSyntaxTree()
            AST_A.data = [FakeNode('1')]

            AST_B = asttree.AbstractSyntaxTree()
            AST_B.data = [FakeNode('1')]

            AST_A.update(AST_B)
            assert AST_A[0].update.called_with(AST_B[0])

        def test_update_performs_nodeupdate_when_order_mixed(self):
            AST_A = asttree.AbstractSyntaxTree()
            AST_A.data = [FakeNode('1'), FakeNode('2')]

            AST_B = asttree.AbstractSyntaxTree()
            AST_B.data = [FakeNode('2'), FakeNode('1')]

            AST_A.update(AST_B)
            assert AST_A[0].update.called_with(AST_B[1])
            assert AST_A[1].update.called_with(AST_B[0])

        def test_update_keeps_new_order(self):
            AST_A = asttree.AbstractSyntaxTree()
            AST_A.data = [FakeNode('1'), FakeNode('2')]

            AST_B = asttree.AbstractSyntaxTree()
            AST_B.data = [FakeNode('2'), FakeNode('1')]

            AST_A.update(AST_B)
            assert AST_A.data == [FakeNode('2'), FakeNode('1')]

    class Test_get_completed_taskchains:
        def test_filters_incompleted_child_taskchains(self):
            """ Retrieve all top-level task-nodes whose self/children are all completed.
            """
            complete_node = mock.Mock()
            complete_node.is_complete = mock.Mock(return_value=True)

            incomplete_node = mock.Mock()
            incomplete_node.is_complete = mock.Mock(return_value=False)

            AST = asttree.AbstractSyntaxTree()
            AST.data = [complete_node, incomplete_node]

            completed = AST.get_completed_taskchains()
            assert completed.data == [complete_node]

    class Test_archive_completed:
        def test_only_completed_taskchains_archived(self):
            data = [mock.Mock(), mock.Mock(), mock.Mock()]
            completed = [data[1]]

            AST = asttree.AbstractSyntaxTree()
            AST.data = data[:]
            with mock.patch(
                '{}.AbstractSyntaxTree.get_completed_taskchains'.format(asttree.__name__),
                return_value=completed
            ):
                archive_ast = AST.archive_completed()

            assert archive_ast.data == [data[1]]
            assert AST.data == [data[0], data[2]]


