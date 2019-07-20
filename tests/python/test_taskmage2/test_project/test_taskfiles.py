from taskmage2.project import taskfiles
from taskmage2.asttree import asttree, astnode
from taskmage2.utils import timezone
import os
import shutil
import tempfile
import json
import datetime

import mock

ns = taskfiles.__name__


current_dt = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())


def get_taskfile(data):
    """ Get a TaskFile object, with fake-read-data.

    Args:
        data (object):
            a native-python collection. it will be
            encoded as json.
    """
    json_data = json.dumps(data)
    taskfile = taskfiles.TaskFile('/var/tmp/fakefile.mtask')

    taskfile.read = mock.Mock(return_value=json_data)
    return taskfile


class Test_TaskFile:
    class Test__str__:
        def test(self):
            taskfile = taskfiles.TaskFile('/var/tmp/file.mtask')
            assert str(taskfile) == taskfile.filepath

    class Test__eq__:
        def test_equality(self):
            taskfile_a = taskfiles.TaskFile('/var/tmp/a.mtask')
            taskfile_b = taskfiles.TaskFile('/var/tmp/a.mtask')
            assert taskfile_a == taskfile_b

        def test_inequality(self):
            taskfile_a = taskfiles.TaskFile('/var/tmp/a.mtask')
            taskfile_b = taskfiles.TaskFile('/var/tmp/b.mtask')
            assert taskfile_a != taskfile_b

    class Test_iter_tasks:
        def test(self):
            filedata = [
                {
                    "indent": 0,
                    "name": "task A",
                    "parent": None,
                    "data": {"status": "todo",
                             "finished": False,
                             "modified": "2019-04-26T16:38:35.030309+00:00",
                             "created": "2019-04-26T16:38:35.030309+00:00"},
                    "_id": "F689D346A57E4D59B49CC56CB18AFB41",
                    "type": "task"
                },
                {
                    "indent": 0,
                    "name": "task B",
                    "parent": None,
                    "data": {"status": "todo",
                             "finished": False,
                             "modified": "2019-04-26T16:38:35.030309+00:00",
                             "created": "2019-04-26T16:38:35.030309+00:00"},
                    "_id": "254AC3AB533E4C6DA63060A9CE0CA006",
                    "type": "task"
                }
            ]
            taskfile = get_taskfile(filedata)
            assert list(taskfile.iter_tasks()) == filedata

    class Test_filter_tasks:
        def test(self):
            filedata = [
                {
                    "indent": 0,
                    "name": "task A",
                    "parent": None,
                    "data": {"status": "todo",
                             "finished": False,
                             "modified": "2019-04-26T16:38:35.030309+00:00",
                             "created": "2019-04-26T16:38:35.030309+00:00"},
                    "_id": "F689D346A57E4D59B49CC56CB18AFB41",
                    "type": "task"
                },
                {
                    "indent": 0,
                    "name": "task B",
                    "parent": None,
                    "data": {"status": "todo",
                             "finished": False,
                             "modified": "2019-04-26T16:38:35.030309+00:00",
                             "created": "2019-04-26T16:38:35.030309+00:00"},
                    "_id": "254AC3AB533E4C6DA63060A9CE0CA006",
                    "type": "task"
                }
            ]
            taskfile = get_taskfile(filedata)

            # filter
            def name_is_task_A(task):
                return task['name'] == 'task A'

            # verify we filtered out task B
            result = list(taskfile.filter_tasks([name_is_task_A]))
            expects = [filedata[0]]
            assert result == expects

    class Test_write:
        ast_tree = asttree.AbstractSyntaxTree([
            astnode.Node(
                _id='533C54F7A87A4AAB99296D213314FB2D',
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'modified': current_dt,
                    'created': current_dt,
                    'finished': False,
                },
            )
        ])
        mtask_tree = [
            {
                "indent": 0,
                "_id":   "533C54F7A87A4AAB99296D213314FB2D",
                "name":  "task A",
                "parent": None,
                "type": "task",
                "data": {"status": "todo",
                         "finished": False,
                         "modified": "1970-01-01T00:00:00+00:00",
                         "created": "1970-01-01T00:00:00+00:00"},
            }
        ]
        current_dt = current_dt

        def test(self):
            """ This is a very evil test.. I need to figure out how to clean this up.
            """
            tempdir = tempfile.mkdtemp()
            filepath = '{}/file.mtask'.format(tempdir)
            taskfile = taskfiles.TaskFile(filepath)
            try:
                mock_open = mock.mock_open()
                with mock.patch(ns + '.open', mock_open, create=True):
                    taskfile.write(self.ast_tree)
                    written_data = mock_open().write.call_args[0][0]
                    data = json.loads(written_data)
                    assert data == self.mtask_tree
            finally:
                if os.path.isdir(tempdir):
                    shutil.rmtree(tempdir)

    class Test__hash__:
        def test_taskfiles_with_same_file_share_hash_value(self):
            taskfile_a = taskfiles.TaskFile('todo.mtask')
            taskfile_b = taskfiles.TaskFile('todo.mtask')
            assert hash(taskfile_a) == hash(taskfile_b)

        def test_taskfiles_with_different_file_do_not_share_hash_value(self):
            taskfile_a = taskfiles.TaskFile('todo.mtask')
            taskfile_b = taskfiles.TaskFile('other.mtask')
            assert hash(taskfile_a) != hash(taskfile_b)

        def test_taskfile_hash_is_different_from_string(self):
            taskfile = taskfiles.TaskFile('todo.mtask')
            assert hash(taskfile) != hash(taskfile.filepath)

