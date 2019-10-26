import pytest

from taskmage2.parser import fmtdata


class Test_TaskList:
    class Test_statuschar:
        def test_obtains_statuschar(self):
            char = fmtdata.TaskList.statuschar('todo')
            assert char == '*'

        def test_raises_keyerror_if_invalid_status(self):
            with pytest.raises(KeyError):
                fmtdata.TaskList.statuschar('invalid')

    class Test_status:
        def test_obtains_status(self):
            status = fmtdata.TaskList.status('*')
            assert status == 'todo'

        def test_raises_keyerror_if_invalid_status(self):
            with pytest.raises(KeyError):
                fmtdata.TaskList.status('.')
