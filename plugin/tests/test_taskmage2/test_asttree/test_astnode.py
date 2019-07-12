import uuid

import mock
import pytest

from taskmage2.asttree import astnode, nodedata

ns = astnode.__name__


class Test_Node(object):
    class Test__init__:
        def test_task_without_metadata_not_modified(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )

            assert task.data.as_dict() == dict(
                status='todo',
                created=None,
                finished=False,
                modified=None,
            )

    class Test_touch:
        def test_assigns_id_if_missing(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )

            _uuid = uuid.UUID('34db96d439164c55ac02de9173fb79ac')
            with mock.patch('{}.uuid.uuid4'.format(ns), return_value=_uuid):
                task.touch()

            assert task.id == '34DB96D439164C55AC02DE9173FB79AC'

        def test_updates_children(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[mock.Mock(), mock.Mock()],
            )

            task.touch()
            assert all([child.touch.called for child in task.children])

    class Test_finalize:
        def test_assigns_id_if_missing(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )

            _uuid = uuid.UUID('34db96d439164c55ac02de9173fb79ac')
            with mock.patch('{}.uuid.uuid4'.format(ns), return_value=_uuid):
                task.finalize()

            assert task.id == '34DB96D439164C55AC02DE9173FB79AC'

        def test_updates_children(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[mock.Mock(), mock.Mock()],
            )

            task.finalize()
            assert all([child.finalize.called for child in task.children])

    class Test_update:
        def test_update_with_nonmatching_id(self):
            params = dict(
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            node_A = astnode.Node(
                _id='24B7213E055B43C2A182FB2CEDC9D36F',
                **params
            )
            node_B = astnode.Node(
                _id='7B28520767FD4EA2961A42E414022B3F',
                **params
            )
            with pytest.raises(RuntimeError):
                node_A.update(node_B)

        def test_update_assigns_name(self):
            params = dict(
                _id=None,
                ntype='task',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            node_A = astnode.Node(name='task A', **params)
            node_B = astnode.Node(name='task B', **params)

            node_A.update(node_B)
            assert node_A.name == 'task B'

        def test_update_receives_type(self):
            params = dict(
                _id=None,
                ntype='task',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            node_A = astnode.Node(name='task A', **params)
            node_B = astnode.Node(name='task B', **params)

            # NOTE: actual value is enum, `type` returns the enum's value
            node_A.update(node_B)
            assert node_A.type == 'task'

        def test_update_operates_on_data(self):
            params = dict(
                _id=None,
                name='task A',
                ntype='task',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            with mock.patch('{}.isinstance'.format(ns), return_value=True):
                mock_data = mock.Mock(spec='{}.TaskData'.format(nodedata.__name__))
                mock_data.update = mock.Mock()

                node_A = astnode.Node(**params)
                node_A._data = mock_data
                node_B = astnode.Node(**params)

                node_A.update(node_B)
                assert mock_data.update.called_with(node_B)

        def test_update_remove_child(self):
            old_node = astnode.Node(
                _id='233662903DE54C4E9FC71EF7DA2920A8',
                ntype='task', name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id='AE0CC1B973694FB4B76F191B28C642FA',
                        ntype='task', name='subtask A',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    ),
                    astnode.Node(
                        _id='A58ACFFF058849B291D65DFBBC146BB8',
                        ntype='task', name='subtask B',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    )
                ]
            )

            new_node = astnode.Node(
                _id='233662903DE54C4E9FC71EF7DA2920A8',
                ntype='task', name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id='A58ACFFF058849B291D65DFBBC146BB8',
                        ntype='task', name='subtask B',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    )
                ]
            )
            old_node.update(new_node)
            assert old_node.children[0].id == new_node.children[0].id

        def test_update_add_child(self):
            old_node = astnode.Node(
                _id='233662903DE54C4E9FC71EF7DA2920A8',
                ntype='task', name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id='A58ACFFF058849B291D65DFBBC146BB8',
                        ntype='task', name='subtask B',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    )
                ]
            )

            new_node = astnode.Node(
                _id='233662903DE54C4E9FC71EF7DA2920A8',
                ntype='task', name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id='AE0CC1B973694FB4B76F191B28C642FA',
                        ntype='task', name='subtask A',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    ),
                    astnode.Node(
                        _id='A58ACFFF058849B291D65DFBBC146BB8',
                        ntype='task', name='subtask B',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                    )
                ]
            )

            old_node.update(new_node)
            assert len(old_node.children) == 2
            assert old_node.children[1].id == 'A58ACFFF058849B291D65DFBBC146BB8'

        def test_update_name_also_updates_modified(self):
            params = dict(
                _id=None,
                ntype='task',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            node_A = astnode.Node(name='task A', **params)
            node_B = astnode.Node(name='task B', **params)

            node_A.update(node_B)
            assert node_A.data.modified != node_B.data.modified

    class Test_is_complete:
        def test_taskchain_completion_file(self):
            """ files must resolve as false, at least until
            I figure out a mechanism for archiving an entire taskfile,
            and if that is even desirable.
            """
            task = astnode.Node(
                _id=None,
                ntype='file',
                name='home/todo.mtask',
                data={},
                children=None,
            )
            assert task.is_complete() is False

        def test_taskchain_completion_empty_section(self):
            """ empty sections resolve as false, they are likely there
            as markers for what is to come next.
            """
            task = astnode.Node(
                _id=None,
                ntype='section',
                name='kitchen',
                data={},
                children=None,
            )
            assert task.is_complete() is False

        def test_taskchain_completion_section_with_children(self):
            """ entirely completed sections resolve as true.
            """
            task = astnode.Node(
                _id=None,
                ntype='section',
                name='kitchen',
                data={},
                children=[
                    astnode.Node(
                        _id=None,
                        ntype='task',
                        name='kitchen',
                        data={
                            'status': 'done',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                        children=None,
                    )
                ],
            )
            assert task.is_complete() is True

        def test_taskchain_completion_top_task_incomplete(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='kitchen',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=None,
            )
            assert task.is_complete() is False

        def test_taskchain_completion_child_task_incomplete(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='kitchen',
                data={
                    'status': 'done',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id=None,
                        ntype='task',
                        name='kitchen',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                        children=None,
                    )
                ],
            )
            assert task.is_complete() is False

        def test_taskchain_completion_child_and_parent_complete(self):
            task = astnode.Node(
                _id=None,
                ntype='task',
                name='kitchen',
                data={
                    'status': 'done',
                    'created': None,
                    'finished': None,
                    'modified': None,
                },
                children=[
                    astnode.Node(
                        _id=None,
                        ntype='task',
                        name='kitchen',
                        data={
                            'status': 'skip',
                            'created': None,
                            'finished': None,
                            'modified': None,
                        },
                        children=None,
                    )
                ],
            )
            assert task.is_complete() is True
