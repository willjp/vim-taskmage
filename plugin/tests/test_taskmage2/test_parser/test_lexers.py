#!/usr/bin/env python
"""
Name :          test_lexers.py
Created :       May 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   checks operating system running maya so adjustments can be made to paths and
                environment
________________________________________________________________________________
"""
# builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
import uuid
# package
# external
import pytest
import six
import mock
# internal
from taskmage2.parser import lexers, iostream

_uuid = 'F04A9556B4114BCFB7B072D727E430A6'


# ========
# Fixtures
# ========

@pytest.fixture
def uid():
    return uuid.UUID(_uuid)

# =====
# Utils
# =====

def tasklist(contents):
    fd = six.StringIO()
    fd.write(contents)
    iofd = iostream.FileDescriptor(fd)

    lexer = lexers.TaskList(iofd)
    _tasklist = []
    token = ''
    while token is not None:
        token = lexer.read_next()
        if token is not None:
            _tasklist.append(token)

    return _tasklist

# =====
# Tests
# =====

class Test_TaskList:
    @pytest.mark.parametrize(
        '    conts,   expected', [
            (
                '* taskA',
                [{
                    '_id':  _uuid,
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': None,
                    'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
                }],
            )
        ]
    )
    def test_read(self, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)
        assert output == expected
