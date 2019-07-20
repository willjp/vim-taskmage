from taskmage2.project import taskfiles
import json

import mock


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
