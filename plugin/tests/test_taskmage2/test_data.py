import uuid
import datetime

from dateutil import tz
import mock
import pytest

from taskmage2 import data, nodedata

ns = data.__name__


class Test_Node(object):
    def test_task_without_metadata_not_modified(self):
        task = data.Node(
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
        task = data.Node(
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
        node_A = data.Node(
            _id='24B7213E055B43C2A182FB2CEDC9D36F',
            **params
        )
        node_B = data.Node(
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
        with mock.patch('{}.TaskData'.format(nodedata.__name__)):
            node_A = data.Node(name='task A', **params)
            node_B = data.Node(name='task B', **params)

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
        with mock.patch(
            '{}.TaskData'.format(nodedata.__name__),
            spec='{}.TaskData'.format(nodedata.__name__),
            return_value=mock.Mock(),
        ) as mock_taskdata:
            node_A = data.Node(**params)
            node_B = data.Node(**params)

            node_A.update(node_B)
            assert mock_taskdata.update.called_with(node_B)


