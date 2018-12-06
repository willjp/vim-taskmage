import uuid
import mock

from taskmage2 import data


ns = data.__name__


class Test_Node(object):
    def test_task_without_data(self):
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
