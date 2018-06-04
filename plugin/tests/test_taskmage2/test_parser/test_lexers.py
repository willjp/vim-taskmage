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
import copy
# package
# external
import pytest
import six
import mock
# internal
from taskmage2.parser import lexers, iostream

_uuid = 'F04A9556B4114BCFB7B072D727E430A6'
_defaulttask = {
    # an empty, but syntactically correct task
    '_id': _uuid,
    'type': 'task',
    'name': 'taskA',
    'indent': 0,
    'parent': None,
    'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
}
_defaultsection = {
    # an empty, but syntactically correct section
    '_id': _uuid,
    'type': 'section',
    'name': 'home',
    'indent': 0,
    'parent': None,
    'data': {},
}

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


def defaulttask(changes=None):
    """
    Args:
        changes (dict):
            A dictionary with nothing but the changes
            to _defaulttask.
    """
    taskcopy = copy.deepcopy(_defaulttask)

    if changes:
        if 'data' in changes:
            taskcopy['data'].update(changes.pop('data'))
        taskcopy.update(changes)

    return taskcopy


def defaultsection(changes=None):
    headercopy = copy.deepcopy(_defaultsection)

    if changes:
        headercopy.update(changes)

    return headercopy


# =====
# Tests
# =====


class Test_TaskList:
    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('status:todo',
                '* taskA',
                [ defaulttask() ]
            ),
            ('status:done',
                'x taskA',
                 [ defaulttask({'data':{'status': 'done', 'finished': True}}) ]
            ),
            ('status:skip',
                '- taskA',
                [ defaulttask({'data':{'status':'skip'}}) ]
            ),
            ('status:wip',
                'o taskA',
                [ defaulttask({'data':{'status':'wip'}}) ]
            ),
    ])
    def test_status(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [

            ('toplevel taskid',
                '* {*C5ED1030425A436DABE94E0FCCCE76D6*} taskA',
                [defaulttask({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6'})]
            ),
            ('subtask taskid',
                '* taskA\n'
                '    * {*C5ED1030425A436DABE94E0FCCCE76D6*} subtaskA\n',
                [defaulttask(), defaulttask({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6', 'name': 'subtaskA', 'indent': 4, 'parent': _uuid})]
            ),
            ('toplevel headerid',
                '{*C5ED1030425A436DABE94E0FCCCE76D6*} home\n'
                '====\n',
                [defaultsection({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6'})]
            ),
    ])
    def test_ids(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('header lv1',
                (
                    'home\n'
                    '====\n'
                ),
                [ defaultsection() ]
            ),
            ('header lv2', # NOT IMPLEMENTED YET!
                (
                    'home\n'
                    '====\n'
                    '\n'
                    'kitchen\n'
                    '-------\n'
                ),
                [
                    defaultsection(),
                    defaultsection({'name':'kitchen', 'parent':_uuid})
                ]
            ),
            ('header id',
                (
                    '{*3576C361D7834C80B3F48E93902B0AE4*}home\n'
                    '====\n'
                ),
                [ defaultsection({'_id':'3576C361D7834C80B3F48E93902B0AE4'}) ],
            ),
    ])
    def test_sections(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [

            ('multiline',
                 '* taskA\n    continued',
                 [defaulttask({'name': 'taskA\n continued'})]
            ),
            ('subtask 1x',
                 '* taskA\n    * subtaskA',
                 [
                     defaulttask(),
                     defaulttask({'name': 'subtaskA', 'indent':4, 'parent':_uuid})
                 ]
            ),
            ('subtask 2x',
                 (
                    '* taskA\n'
                    '    * subtaskA\n'
                    '    * subtaskB\n'
                 ),
                 [
                     defaulttask(),
                     defaulttask({'name': 'subtaskA', 'indent':4, 'parent':_uuid}),
                     defaulttask({'name': 'subtaskB', 'indent':4, 'parent':_uuid}),
                 ],
            )
        ]
    )
    def test_subtasks(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('indent',
                '    * taskA',
                [ defaulttask({'indent':4}) ]
            ),
    ])
    def test_indent(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected



    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('header task',
                (
                    'home\n'
                    '====\n'
                    '* taskA\n'
                ),
                [ defaultsection(), defaulttask({'parent':_uuid}) ]
            ),
    ])
    def test_headertasks(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = tasklist(conts)

        print(testname)
        assert output == expected
