import uuid
import datetime

from dateutil import tz
import mock
import pytest

from taskmage2 import data


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


class Test_TaskData(object):

    @pytest.mark.parametrize(
        'status', ('todo', 'skip', 'done', 'wip'),
    )
    def test_status_valid(self, status):
        taskdata = data.TaskData(status=status)
        assert getattr(taskdata, 'status') == status

    def test_status_invalid(self):
        with pytest.raises(TypeError):
            data.TaskData(status='incomplete')

    @pytest.mark.parametrize(
        'created', (None, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)),
    )
    def test_created_valid(self, created):
        taskdata = data.TaskData(status='todo', created=created)
        assert getattr(taskdata, 'created') == created

    def test_created_invalid(self):
        with pytest.raises(TypeError):
            data.TaskData(status='todo', created='November 1st')

    def test_finished_defaults_to_false(self):
        taskdata = data.TaskData(
             status='todo',
             created=None,
             finished=None,
             modified=None,
        )
        assert taskdata.finished is False

    def test_finished_valid(self):
        dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)
        taskdata = data.TaskData('todo', finished=dt)
        assert taskdata.finished == dt

    def test_finished_missing_timezone(self):
        with pytest.raises(TypeError):
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0)
            data.TaskData('todo', finished=dt)

    @pytest.mark.parametrize(
        'modified', (None, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)),
    )
    def test_modified_valid(self, modified):
        taskdata = data.TaskData(status='todo', modified=modified)
        assert getattr(taskdata, 'modified') == modified

    def test_modified_invalid(self):
        with pytest.raises(TypeError):
            data.TaskData(status='todo', modified='November 1st')

    def test_touch_assigns_modified(self):
        taskdata = data.TaskData(status='todo')
        dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)

        new_taskdata = self.touch(taskdata, dt)
        assert new_taskdata.modified == dt

    def test_touch_overwrites_modified(self):
        taskdata = data.TaskData(
            status='todo',
            modified=datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=tz.UTC)
        )
        dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)

        new_taskdata = self.touch(taskdata, dt)
        assert new_taskdata.modified == dt

    def test_touch_assigns_created(self):
        taskdata = data.TaskData(status='todo')
        dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)

        new_taskdata = self.touch(taskdata, dt)
        assert new_taskdata.created == dt

    def test_touch_does_not_overwrite_created(self):
        created_dt = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=tz.UTC)
        current_dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)
        taskdata = data.TaskData(status='todo', created=created_dt)

        new_taskdata = self.touch(taskdata, current_dt)
        assert new_taskdata.created == created_dt

    def test_touch_updates_finished(self):
        # 'status' and 'finished' are inconsistent
        taskdata = data.TaskData(status='done', finished=False)
        dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=tz.UTC)

        new_taskdata = self.touch(taskdata, dt)
        assert new_taskdata.finished == dt

    def touch(self, taskdata, dt):
        with mock.patch('{}.datetime'.format(ns)) as mock_datetime:
            # NOTE: make isinstance(x, datetime.datetime) return true
            with mock.patch('{}.isinstance'.format(ns), return_value=True):
                mock_datetime.datetime = mock.MagicMock(spec='datetime.datetime')
                mock_datetime.datetime.now = mock.Mock(return_value=dt)
                new_taskdata = taskdata.touch()
                return new_taskdata
