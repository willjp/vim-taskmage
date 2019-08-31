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
import pprint
import datetime
import six
# external
import pytest
import mock
# internal
from taskmage2.parser import iostream, lexers
from taskmage2.utils import excepts
from taskmage2.utils import timezone


ns = lexers.__name__


# =====
# Utils
# =====

def get_lexer_tasklist(text):
    fd = six.StringIO()
    fd.write(text)
    iofd = iostream.FileDescriptor(fd)
    lexer = lexers.TaskList(iofd)
    return lexer


def get_lexer_mtask(text):
    fd = six.StringIO()
    fd.write(text)
    fd.seek(0)
    lexer = lexers.Mtask(fd)
    return lexer


def mock_uuid():
    patch = mock.patch('uuid.uuid4', side_effect=uid)
    return patch


def uid():
    return uuid.UUID('481ae479e4ab4c9b81653db9b92469c0')


# =====
# Tests
# =====


class Test_TaskList:
    class Test_read:
        def test_status_todo(self):
            tokens = self.tasklist('* taskA')
            assert tokens == [
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': None,
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                }
            ]

        def test_status_done(self):
            """
            Notes:
                despite being newly finished, the finished datetime is not recorded
                until `ast.touch()` is performed just before writing to disk.

                TaskList does not store finished information, so it cannot tell if
                the finished-date must be udpated.
            """
            tokens = self.tasklist('x taskA')
            assert tokens == [
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': None,
                    'data': {'status': 'done', 'created': None, 'finished': None, 'modified': None},
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
                    'data': {'status': 'skip', 'created': None, 'finished': None, 'modified': None},
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
                    'data': {'status': 'wip', 'created': None, 'finished': None, 'modified': None},
                }
            ]

        def test_toplevel_task_with_leading_whitespace(self):
            tokens = self.tasklist_data('\n\n* taskA')

            assert tokens == [
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': None,
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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

        def test_multiple_sections_at_same_indentation(self):
            tokens = self.tasklist(
                'home\n'
                '====\n'
                '\n'
                'work\n'
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
                },
                {
                    '_id': uid().hex.upper(),
                    'type': 'section',
                    'name': 'work',
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

        def test_section_after_task(self):
            tokens = self.tasklist(
                '*{*251CCE3BF1E34693B0E3BB8CD8331EA3*} pay bills\n'
                '\n'
                'kitchen\n'
                '=======\n'
            )
            print(tokens)
            assert tokens == [
                {
                    '_id': '251CCE3BF1E34693B0E3BB8CD8331EA3',
                    'type': 'task',
                    'name': 'pay bills',
                    'indent': 0,
                    'parent': None,
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                },
                {
                    '_id': uid().hex.upper(),
                    'type': 'section',
                    'name': 'kitchen',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                }
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
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
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
                    'indent': 0,
                    'parent': uid().hex.upper(),
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                }
            ]

        def test_subsection_with_task(self):
            tokens = self.tasklist(
                '{*0EB83AE8F0F346ACB4C2A0485DA430C2*}home\n'
                '========================================\n'
                '\n'
                '{*66A4CCF279E4410B90B920FA1BC5C744*}kitchen\n'
                '-------------------------------------------\n'
                '\n'
                '* taskA\n'
            )
            assert tokens == [
                {
                    '_id': '0EB83AE8F0F346ACB4C2A0485DA430C2',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                },
                {
                    '_id': '66A4CCF279E4410B90B920FA1BC5C744',
                    'type': 'section',
                    'name': 'kitchen',
                    'indent': 1,
                    'parent': '0EB83AE8F0F346ACB4C2A0485DA430C2',
                    'data': {},
                },
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': '66A4CCF279E4410B90B920FA1BC5C744',
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                }
            ]

        def test_subsection_with_task_subtask(self):
            tokens = self.tasklist(
                '{*0EB83AE8F0F346ACB4C2A0485DA430C2*}home\n'
                '========================================\n'
                '\n'
                '{*66A4CCF279E4410B90B920FA1BC5C744*}kitchen\n'
                '-------------------------------------------\n'
                '\n'
                '*{*8675386FD62D4355AD4B613054C3E463*} taskA\n'
                '    * subtaskA\n'
            )
            assert tokens == [
                {
                    '_id': '0EB83AE8F0F346ACB4C2A0485DA430C2',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                },
                {
                    '_id': '66A4CCF279E4410B90B920FA1BC5C744',
                    'type': 'section',
                    'name': 'kitchen',
                    'indent': 1,
                    'parent': '0EB83AE8F0F346ACB4C2A0485DA430C2',
                    'data': {},
                },
                {
                    '_id': '8675386FD62D4355AD4B613054C3E463',
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': '66A4CCF279E4410B90B920FA1BC5C744',
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                },
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'subtaskA',
                    'indent': 4,
                    'parent': '8675386FD62D4355AD4B613054C3E463',
                    'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
                }
            ]

        def test_invalid_character_raises_parseerror(self):
            with pytest.raises(excepts.ParserError):
                self.tasklist('^')

        def test_parsererror_if_section_without_title(self):
            with pytest.raises(excepts.ParserError):
                self.tasklist('====\n')

        def test_parsererror_if_section_title_length_exceeds_underline(self):
            with pytest.raises(excepts.ParserError):
                self.tasklist('ABCDEFGHI\n====\n')

        def test_parsererror_if_bad_uuid_indicator_start(self):
            with pytest.raises(excepts.ParserError):
                self.tasklist('{A49FFE9027384D23A269EF07CC3B6A51*}SEC\n===\n')

        def test_parsing_empty_file_does_not_produce_error(self):
            self.tasklist('')

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

        def tasklist_data(self, filecontents):
            with mock.patch('{}.uuid.uuid4'.format(ns), side_effect=uid):
                # initialize TaskList()
                fd = six.StringIO()
                fd.write(filecontents)
                iofd = iostream.FileDescriptor(fd)
                lexer = lexers.TaskList(iofd)

                # read until end of TaskList
                lexer.read()
                return lexer.data

    class Test_peek:
        def test_peek_from_start(self):
            # test
            lexer = get_lexer_tasklist('* task A')
            with mock_uuid():
                token = lexer.peek()

            assert token == {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'task A',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
            }

        def test_peek_after_started(self):
            lexer = get_lexer_tasklist('* task A\n* task B\n')
            with mock_uuid():
                lexer.read_next()  # changes position
                token_B = lexer.peek()       # does not change pos

            assert token_B == {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'task B',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
            }

        def test_peek_does_not_change_pos(self):
            # 3x calls to lexer.peek() all should return same 'task A'
            lexer = get_lexer_tasklist('* task A')
            with mock_uuid():
                token = lexer.peek()
                token = lexer.peek()
                token = lexer.peek()

            assert token == {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'task A',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': None, 'modified': None},
            }

    class Test_eof:
        def test_returns_false_if_not_eof(self):
            lexer = get_lexer_tasklist('* task A')
            assert lexer.eof() is False

        def test_returns_true_if_eof(self):
            lexer = get_lexer_tasklist('* task A')
            lexer.read_next()
            assert lexer.eof() is True


class Test_Mtask:
    """ Mtask shouldn't alter raw json
    """

    class Test__init__:
        def test_init_empty_without_error(self):
            get_lexer_mtask('')

    class Test_read_next:
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

        def test_taskdata_converts_mtask_isoformat_to_datetime_objects(self):
            task = {
                '_id': uid().hex.upper(),
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {
                    'status': 'done',
                    'created': '2018-01-01T00:00:00+00:00',
                    'finished': '2018-01-01T00:00:00+00:00',
                    'modified': '2018-01-01T00:00:00+00:00'
                },
            }
            result = self.mtask(json.dumps([task]))

            expects = [
                {
                    '_id': uid().hex.upper(),
                    'type': 'task',
                    'name': 'taskA',
                    'indent': 0,
                    'parent': None,
                    'data': {
                        'status': 'done',
                        'created': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                        'finished': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                        'modified': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                    },
                }
            ]
            pprint.pprint(result)
            print('----')
            pprint.pprint(expects)
            assert result == expects

        def mtask(self, filecontents):
            # load lexer
            lexer = get_lexer_mtask(filecontents)

            # read all tokens
            _lexertokens = []
            token = ''
            while token is not None:
                token = lexer.read_next()
                if token is not None:
                    _lexertokens.append(token)

            return _lexertokens

    class Test_read:
        def test_valid_data(self):
            contents = [
                {
                    '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                },
            ]
            contents_json = json.dumps(contents)
            lexer = get_lexer_mtask(contents_json)
            results = lexer.read()

            assert results == contents

        def test_missing_keys_raises_parsererror(self):
            contents = [
                {
                    '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                    'type': 'section',
                    'name': 'home',
                },
            ]
            contents_json = json.dumps(contents)
            lexer = get_lexer_mtask(contents_json)

            with pytest.raises(excepts.ParserError):
                lexer.read()

        def test_extra_keys_raises_parsererror(self):
            contents = [
                {
                    '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                    'extra_key': 123,
                },
            ]
            contents_json = json.dumps(contents)
            lexer = get_lexer_mtask(contents_json)

            with pytest.raises(excepts.ParserError):
                lexer.read()

        def test_invalid_task_status_raises_parsererror(self):
            contents = [
                {
                    '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {
                        'status': 'invalid-status',  # <-- invalid data
                        'created': None,
                        'finished': None,
                        'modified': None,
                    }
                },
            ]
            contents_json = json.dumps(contents)
            lexer = get_lexer_mtask(contents_json)
            with pytest.raises(excepts.ParserError):
                lexer.read()


class Test_get_lexer:
    def test_get_lexer_from_enum_option_val(self):
        fd = six.StringIO()
        lexer = lexers.get_lexer(fd, 'mtask')
        assert isinstance(lexer, lexers.Mtask)

    def test_get_lexer_from_enum_option(self):
        fd = six.StringIO()
        lexer = lexers.get_lexer(fd, lexers.LexerTypes.mtask)
        assert isinstance(lexer, lexers.Mtask)
