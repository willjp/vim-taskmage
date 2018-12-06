import uuid

import mock
import pytest

from taskmage2.ast import astnode, nodedata

ns = astnode.__name__


class Test_Node(object):
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

    def test_touch_assigns_id_if_missing(self):
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