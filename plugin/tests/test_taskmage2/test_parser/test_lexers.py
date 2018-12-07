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
from __future__ import absolute_import, division, print_function
import uuid
import json
# package
from taskmage2.parser import iostream, lexers
import six
# external
import pytest
import mock
# internal


ns = lexers.__name__


@pytest.fixture
def uid():
    return uuid.UUID('481ae479e4ab4c9b81653db9b92469c0')


class Test_TaskList:
    """ Tests for the TaskList Lexer
    """
    def test_status_todo(self):
        tokens = self.tasklist('* taskA')
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_status_done(self):
        tokens = self.tasklist('x taskA')
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'done', 'created': None, 'finished': True, 'modified': None},
            }
        ]

    def test_status_skip(self):
        tokens = self.tasklist('- taskA')
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'skip', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_status_wip(self):
        tokens = self.tasklist('o taskA')
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'wip', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_toplevel_task_with_leading_whitespace(self):
        tokens = self.tasklist('\n\n* taskA\n')

        # NOTE: this returns True, but in production it is not working...
        #       I suspect a bug with iostream.VimBuffer()
        assert False

        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_toplevel_task_with_id(self):
        tokens = self.tasklist('*{*C5ED1030425A436DABE94E0FCCCE76D6*} taskA')
        assert tokens == [
            {
                '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_subtask_with_id(self):
        tokens = self.tasklist(
            '* taskA\n'
            '    *{*C5ED1030425A436DABE94E0FCCCE76D6*} subtaskA\n'
        )
        assert tokens[1] == {
            '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
            'type': 'task',
            'name': 'subtaskA',
            'indent': 4,
            'parent': uid().hex.upper(),
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }

    def test_2nd_subtask_with_id(self):
        tokens = self.tasklist(
                '* taskA\n'
                '    *{*C5ED1030425A436DABE94E0FCCCE76D6*} subtaskA\n'
                '    *{*AAAAAAA0425A436DABE94E0FCCCE76D6*} subtaskB\n',
        )
        assert tokens[2] == {
            '_id': 'AAAAAAA0425A436DABE94E0FCCCE76D6',
            'type': 'task',
            'name': 'subtaskB',
            'indent': 4,
            'parent': uid().hex.upper(),
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }

    def test_toplevel_section_with_id_longform(self):
        tokens = self.tasklist(
            '{*C5ED1030425A436DABE94E0FCCCE76D6*} home\n'
            '=========================================\n',
        )
        assert tokens == [
            {
                '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                'type': 'section',
                'name': 'home',
                'indent': 0,
                'parent': None,
                'data': {},
            }
        ]

    def test_toplevel_section_with_id_shortform(self):
        tokens = self.tasklist(
            '{*C5ED1030425A436DABE94E0FCCCE76D6*} home\n'
            '====\n',
        )
        assert tokens == [
            {
                '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                'type': 'section',
                'name': 'home',
                'indent': 0,
                'parent': None,
                'data': {},
            }
        ]

    def test_toplevel_section(self):
        tokens = self.tasklist(
            'home\n'
            '====\n'
        )
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'section',
                'name': 'home',
                'indent': 0,
                'parent': None,
                'data': {},
            }
        ]

    def test_toplevel_file(self):
        tokens = self.tasklist(
            'file::path/home.mtask\n'
            '=====================\n',
        )
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'file',
                'name': 'path/home.mtask',
                'indent': 0,
                'parent': None,
                'data': {},
            },
        ]

    def test_subsection(self):
        tokens = self.tasklist(
            'home\n'
            '====\n'
            '\n'
            'kitchen\n'
            '-------\n',
        )
        assert tokens[1] == {
            '_id': uid().hex.upper(),
            'type': 'section',
            'name': 'kitchen',
            'indent': 1,
            'parent': uid().hex.upper(),
            'data': {},
        }

    def test_multiline_task(self):
        tokens = self.tasklist(
            '* taskA\n'
            '  continued'
        )
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA\n continued',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_multiline_subtask(self):
        tokens = self.tasklist(
            '* taskA\n'
            '    * subtaskA\n'
            '      continued\n'
        )
        assert tokens[1] == {
            '_id': uid().hex.upper(),
            'type': 'task',
            'name': 'subtaskA\n continued',
            'indent': 4,
            'parent': uid().hex.upper(),
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }

    def test_2nd_multiline_subtask(self):
        tokens = self.tasklist(
            '* taskA\n'
            '    * subtaskA\n'
            '      continued\n'
            '    * subtaskB\n'
            '      continued\n'
        )
        assert tokens[2] == {
            '_id': uid().hex.upper(),
            'type': 'task',
            'name': 'subtaskB\n continued',
            'indent': 4,
            'parent': uid().hex.upper(),
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }

    def test_section_subtask_indented(self):
        tokens = self.tasklist(
            'home\n'
            '====\n'
            '\n'
            '    * taskA\n'
        )
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'section',
                'name': 'home',
                'indent': 0,
                'parent': None,
                'data': {},
            },
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 4,
                'parent': uid().hex.upper(),
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def test_section_subtask_non_indented(self):
        tokens = self.tasklist(
            'home\n'
            '====\n'
            '\n'
            '* taskA\n'
        )
        assert tokens == [
            {
                '_id': uid().hex.upper(),
                'type': 'section',
                'name': 'home',
                'indent': 0,
                'parent': None,
                'data': {},
            },
            {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 4,
                'parent': uid().hex.upper(),
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            }
        ]

    def tasklist(self, filecontents):
        """ Initializes a TaskList(), returns the lexed contents as a list.
        """
        with mock.patch('{}.uuid.uuid4'.format(ns), side_effect=uid):
            # initialize TaskList()
            fd = six.StringIO()
            fd.write(filecontents)
            iofd = iostream.FileDescriptor(fd)
            lexer = lexers.TaskList(iofd)

            # read until end of TaskList
            _lexertokens = []
            token = ''
            while token is not None:
                token = lexer.read_next()
                if token is not None:
                    _lexertokens.append(token)

            return _lexertokens


class Test_Mtask:
    """ Mtask shouldn't alter raw json
    """
    def test_task(self):
        task = {
            '_id': uid().hex.upper(),
            'type': 'task',
            'name': 'taskA',
            'indent': 0,
            'parent': None,
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }
        assert self.mtask(json.dumps([task])) == [task]

    def test_section(self):
        section = {
            '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
            'type': 'section',
            'name': 'home',
            'indent': 0,
            'parent': None,
            'data': {},
        }
        assert self.mtask(json.dumps([section])) == [section]

    def test_file(self):
        file_ = {
            '_id': uid().hex.upper(),
            'type': 'file',
            'name': 'path/home.mtask',
            'indent': 0,
            'parent': None,
            'data': {},
        }
        assert self.mtask(json.dumps([file_])) == [file_]

    def mtask(self, filecontents):
        # load lexer
        fd = six.StringIO()
        fd.write(filecontents)
        fd.seek(0)
        lexer = lexers.Mtask(fd)

        # read all tokens
        _lexertokens = []
        token = ''
        while token is not None:
            token = lexer.read_next()
            if token is not None:
                _lexertokens.append(token)

        return _lexertokens
