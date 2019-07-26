import uuid
import datetime

import mock
import pytest

from taskmage2.asttree import nodedata
from taskmage2.utils import timezone


ns = nodedata.__name__


class Test__NodeData:
    class Test__init__:
        def test_no_attrs_runs_without_except(self):
            class MyData(nodedata._NodeData):
                _attrs = tuple()
            MyData(tuple())

        def test_missing_attrs_tuple_raises_except(self):
            class MyData(nodedata._NodeData):
                pass

            with pytest.raises(AttributeError):
                data = (1, 2, 3)
                MyData(data)

        def test_incorrect_number_of_params_raises_except(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            with pytest.raises(RuntimeError):
                data = (1, 2)
                MyData(data)

    class Test__repr__:
        def test(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            mydata = MyData((1, 2, 3))
            mydata_repr = repr(mydata)
            expects = 'MyData(one=1, two=2, three=3)'
            assert expects == mydata_repr

    class Test__getattr__:
        def test_valid_attr(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            mydata = MyData((1, 2, 3))
            assert mydata.two == 2

        def test_invalid_attr_raises_attributeerror(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            mydata = MyData((1, 2, 3))
            with pytest.raises(AttributeError):
                mydata.four

    class Test__eq__:
        def test_equality(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            data_A = MyData((1, 2, 3))
            data_B = MyData((1, 2, 3))
            assert data_A == data_B

        def test_class_inequality(self):
            class DataA(nodedata._NodeData):
                _attrs = ('one', 'two')

            class DataB(nodedata._NodeData):
                _attrs = ('one', 'two')

            data_A = DataA((1, 2))
            data_B = DataB((1, 2))

            with pytest.raises(TypeError):
                data_A == data_B

        def test_data_inequality(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two')

            data_A = MyData((1, 2))
            data_B = MyData((3, 4))
            assert data_A != data_B

    class Test_as_dict:
        def test(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two')

            data = MyData((1, 2))
            assert data.as_dict() == {'one': 1, 'two': 2}

    class Test_copy:
        def test_exact_copy(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two')

            data_a = MyData((1, 2))
            data_b = data_a.copy()
            assert data_a == data_b

        def test_copy_modified_with_args(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            data_a = MyData((1, 2, 3))
            data_b = data_a.copy(4, 5)
            assert data_b != data_a
            assert data_b.as_dict() == {
                'one': 4,
                'two': 5,
                'three': 3,
            }

        def test_copy_modified_with_kwargs(self):
            class MyData(nodedata._NodeData):
                _attrs = ('one', 'two', 'three')

            data_a = MyData((1, 2, 3))
            data_b = data_a.copy(three=6)
            assert data_b != data_a
            assert data_b.as_dict() == {
                'one': 1,
                'two': 2,
                'three': 6,
            }


class Test_TaskData:
    class Test__init__:
        @pytest.mark.parametrize(
            'status', ('todo', 'skip', 'done', 'wip'),
        )
        def test_status_valid(self, status):
            taskdata = nodedata.TaskData(status=status)
            assert getattr(taskdata, 'status') == status

        def test_status_invalid(self):
            with pytest.raises(TypeError):
                nodedata.TaskData(status='incomplete')

        @pytest.mark.parametrize(
            'created', (None, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())),
        )
        def test_created_valid(self, created):
            taskdata = nodedata.TaskData(status='todo', created=created)
            assert getattr(taskdata, 'created') == created

        def test_created_invalid(self):
            with pytest.raises(TypeError):
                nodedata.TaskData(status='todo', created='November 1st')

        def test_finished_defaults_to_false(self):
            taskdata = nodedata.TaskData(
                 status='todo',
                 created=None,
                 finished=None,
                 modified=None,
            )
            assert taskdata.finished is False

        def test_finished_valid(self):
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData('todo', finished=dt)
            assert taskdata.finished == dt

        def test_finished_missing_timezone(self):
            with pytest.raises(TypeError):
                dt = datetime.datetime(2018, 1, 1, 0, 0, 0)
                nodedata.TaskData('todo', finished=dt)

        @pytest.mark.parametrize(
            'modified', (None, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())),
        )
        def test_modified_valid(self, modified):
            taskdata = nodedata.TaskData(status='todo', modified=modified)
            assert getattr(taskdata, 'modified') == modified

        def test_modified_invalid(self):
            with pytest.raises(TypeError):
                nodedata.TaskData(status='todo', modified='November 1st')

    class Test_touch:
        def test_assigns_modified(self):
            taskdata = nodedata.TaskData(status='todo')
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())

            new_taskdata = self.touch(taskdata, dt)
            assert new_taskdata.modified == dt

        def test_overwrites_modified(self):
            taskdata = nodedata.TaskData(
                status='todo',
                modified=datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            )
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())

            new_taskdata = self.touch(taskdata, dt)
            assert new_taskdata.modified == dt

        def test_assigns_created(self):
            taskdata = nodedata.TaskData(status='todo')
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())

            new_taskdata = self.touch(taskdata, dt)
            assert new_taskdata.created == dt

        def test_does_not_overwrite_created(self):
            created_dt = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            current_dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', created=created_dt)

            new_taskdata = self.touch(taskdata, current_dt)
            assert new_taskdata.created == created_dt

        def test_updates_finished(self):
            # 'status' and 'finished' are inconsistent
            taskdata = nodedata.TaskData(status='done', finished=False)
            dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())

            new_taskdata = self.touch(taskdata, dt)
            assert new_taskdata.finished == dt

        def touch(self, taskdata, current_dt):
            with mock.patch('{}.datetime'.format(ns)) as mock_datetime:
                # NOTE: make isinstance(x, datetime.datetime) return true
                with mock.patch('{}.isinstance'.format(ns), return_value=True):
                    mock_datetime.datetime = mock.MagicMock(spec='datetime.datetime')
                    mock_datetime.datetime.now = mock.Mock(return_value=current_dt)
                    new_taskdata = taskdata.touch()
                    return new_taskdata

    class Test_finalize:
        def test_sets_modified_when_null(self):
            taskdata = nodedata.TaskData(status='todo', modified=None)
            now_dt = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            new_taskdata = self.finalize(taskdata, now_dt)
            assert new_taskdata.modified == now_dt

        def test_does_not_change_non_null_modified(self):
            modified = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', modified=modified)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.modified == modified

        def test_sets_created_if_null(self):
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', created=None)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.created == now

        def test_does_not_set_created_already_set(self):
            created = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', created=created)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.created == created

        def test_sets_finished_when_task_complete_and_finished_is_null(self):
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='done', finished=None)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.finished == now

        def test_does_not_set_finished_when_task_incomplete_and_finished_is_null(self):
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', finished=None)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.finished is False

        def test_does_not_overwrite_finished_when_task_complete_and_finished_is_set(self):
            finished = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='done', finished=finished)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.finished == finished

        def test_clears_finished_when_task_incomplete(self):
            finished = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            now = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(status='todo', finished=finished)
            new_taskdata = self.finalize(taskdata, now)
            assert new_taskdata.finished is False

        def finalize(self, taskdata, current_dt):
            with mock.patch('{}.datetime'.format(ns)) as mock_datetime:
                # NOTE: make isinstance(x, datetime.datetime) return true
                with mock.patch('{}.isinstance'.format(ns), return_value=True):
                    mock_datetime.datetime = mock.MagicMock(spec='datetime.datetime')
                    mock_datetime.datetime.now = mock.Mock(return_value=current_dt)
                    new_taskdata = taskdata.finalize()
                    return new_taskdata

    class Test_update:
        def test_sets_modified_when_changed(self):
            old_modified_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            new_modified_date = datetime.datetime(2018, 2, 2, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='todo', modified=old_modified_date)
            new_data = nodedata.TaskData(status='wip', modified=new_modified_date)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.modified == current_date

        def test_does_not_set_modified_when_identical(self):
            task_dt = datetime.datetime(2018, 1, 1, 0, 0, 0, 0, tzinfo=timezone.UTC())
            current_dt = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())
            taskdata = nodedata.TaskData(
                status='todo',
                modified=task_dt,
                created=task_dt,
                finished=False,
            )

            merged_data = self.update(taskdata, taskdata, current_dt)
            assert merged_data.modified == task_dt

        def test_does_not_set_modified_if_status_identical_and_no_changes(self):
            task_dt = datetime.datetime(2018, 1, 1, 0, 0, 0, 0, tzinfo=timezone.UTC())
            current_dt = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())
            old_data = nodedata.TaskData(
                status='todo',
                modified=task_dt,
                created=task_dt,
                finished=False,
            )
            new_data = nodedata.TaskData(
                status='todo',
                modified=None,
                created=None,
                finished=None,
            )

            merged_data = self.update(old_data, new_data, current_dt)
            assert merged_data.modified == task_dt

        def test_status(self):
            old_modified_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            new_modified_date = datetime.datetime(2018, 2, 2, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='todo', modified=old_modified_date)
            new_data = nodedata.TaskData(status='wip', modified=new_modified_date)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.status == 'wip'

        def test_created(self):
            old_created_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            new_created_date = datetime.datetime(2018, 2, 2, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='todo', created=old_created_date)
            new_data = nodedata.TaskData(status='todo', created=new_created_date)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.created == new_created_date

        def test_created_no_new_data(self):
            old_created_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='todo', created=old_created_date)
            new_data = nodedata.TaskData(status='todo', created=None)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.created == old_created_date

        def test_finished_to_unfinished(self):
            old_finished_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='done', finished=old_finished_date)
            new_data = nodedata.TaskData(status='todo')

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.finished is False

        def test_unfinished_to_finished_without_date(self):
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='todo')
            new_data = nodedata.TaskData(status='done')

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.finished == current_date

        def test_unfinished_to_finished_with_date(self):
            new_finished_date = datetime.datetime(2018, 2, 2, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='wip')
            new_data = nodedata.TaskData(status='done', finished=new_finished_date)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.finished == new_finished_date

        def test_finished_with_date_when_already_finished(self):
            old_finished_date = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            new_finished_date = datetime.datetime(2018, 2, 2, 0, 0, 0, tzinfo=timezone.UTC())
            current_date = datetime.datetime(2018, 3, 3, 0, 0, 0, 0, tzinfo=timezone.UTC())

            old_data = nodedata.TaskData(status='done', finished=old_finished_date)
            new_data = nodedata.TaskData(status='done', finished=new_finished_date)

            merged_data = self.update(old_data, new_data, current_date)
            assert merged_data.finished == old_finished_date

        def update(self, taskdata, newtaskdata, current_dt):
            with mock.patch('{}.datetime'.format(ns)) as mock_datetime:
                # NOTE: make isinstance(x, datetime.datetime) return true
                with mock.patch('{}.isinstance'.format(ns), return_value=True):
                    mock_datetime.datetime = mock.MagicMock(spec='datetime.datetime')
                    mock_datetime.datetime.now = mock.Mock(return_value=current_dt)
                    merged_taskdata = taskdata.update(newtaskdata)
                    return merged_taskdata

    class Test__eq__:
        @pytest.mark.parametrize(
            'params', [
                ('todo', datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()), False, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())),
            ]
        )
        def test_equality(self, params):
            task_A = nodedata.TaskData(*params)
            task_B = nodedata.TaskData(*params)
            assert task_A == task_B

        @pytest.mark.parametrize(
            'params', [
                (datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()), False, datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())),
            ]
        )
        def test_inequality(self, params):
            task_A = nodedata.TaskData('todo', *params)
            task_B = nodedata.TaskData('skip', *params)
            assert task_A != task_B


