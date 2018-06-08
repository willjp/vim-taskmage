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
import json
# package
from taskmage2.testutils import lexers, tokens, core
# external
import pytest
import mock
# internal


@pytest.fixture
def uid():
    return uuid.UUID(core.uuid)


class Test_TaskList:
    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('status:todo',
                '* taskA',
                [ tokens.task() ]
            ),
            ('status:done',
                'x taskA',
                 [ tokens.task({'data':{'status': 'done', 'finished': True}}) ]
            ),
            ('status:skip',
                '- taskA',
                [ tokens.task({'data':{'status':'skip'}}) ]
            ),
            ('status:wip',
                'o taskA',
                [ tokens.task({'data':{'status':'wip'}}) ]
            ),
    ])
    def test_status(self, testname, conts, expected, uid):
        with mock.patch.object(uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [

            ('toplevel taskid',
                '* {*C5ED1030425A436DABE94E0FCCCE76D6*} taskA',
                [tokens.task({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6'})]
            ),
            ('subtask taskid',
                '* taskA\n'
                '    * {*C5ED1030425A436DABE94E0FCCCE76D6*} subtaskA\n',
                [tokens.task(), tokens.task({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6', 'name': 'subtaskA', 'indent': 4, 'parent': core.uuid})]
            ),
            ('subtask taskid 2x',
                '* taskA\n'
                '    * {*C5ED1030425A436DABE94E0FCCCE76D6*} subtaskA\n'
                '    * {*AAAAAAA0425A436DABE94E0FCCCE76D6*} subtaskB\n',
                [
                    tokens.task(),
                    tokens.task({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6', 'name': 'subtaskA', 'indent': 4, 'parent': core.uuid}),
                    tokens.task({'_id': 'AAAAAAA0425A436DABE94E0FCCCE76D6', 'name': 'subtaskB', 'indent': 4, 'parent': core.uuid}),
                ],
            ),
            ('toplevel headerid',
                '{*C5ED1030425A436DABE94E0FCCCE76D6*} home\n'
                '====\n',
                [tokens.section({'_id': 'C5ED1030425A436DABE94E0FCCCE76D6'})]
            ),
    ])
    def test_ids(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('header lv1',
                (
                    'home\n'
                    '====\n'
                ),
                [ tokens.section() ]
            ),
            ('file lv1',
                'file::path/home.mtask\n'
                '=====================\n',
                [ tokens.section({'type': 'file', 'name': 'path/home.mtask'}) ]
            ),
            ('header lv2', # NOT IMPLEMENTED YET!
                'home\n'
                '====\n'
                '\n'
                'kitchen\n'
                '-------\n',
                [
                    tokens.section(),
                    tokens.section({'name':'kitchen', 'indent':1, 'parent':core.uuid})
                ]
            ),
    ])
    def test_sections(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
            'testname, conts, expected', [

            ('multiline',
                 '* taskA\n    continued',
                 [tokens.task({'name': 'taskA\n continued'})]
            ),
            ('subtask 1x',
                 '* taskA\n    * subtaskA',
                 [
                     tokens.task(),
                     tokens.task({'name': 'subtaskA', 'indent':4, 'parent':core.uuid})
                 ]
            ),
            ('subtask 2x',
                 (
                    '* taskA\n'
                    '    * subtaskA\n'
                    '    * subtaskB\n'
                 ),
                 [
                     tokens.task(),
                     tokens.task({'name': 'subtaskA', 'indent':4, 'parent':core.uuid}),
                     tokens.task({'name': 'subtaskB', 'indent':4, 'parent':core.uuid}),
                 ],
            )
        ]
    )
    def test_subtasks(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

        print(testname)
        assert output == expected

    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('indent',
                '    * taskA',
                [ tokens.task({'indent':4}) ]
            ),
    ])
    def test_indent(self, testname, conts, expected, uid):
        with mock.patch.object(uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

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
                [ tokens.section(), tokens.task({'parent':core.uuid}) ]
            ),
    ])
    def test_headertasks(self, testname, conts, expected, uid):
        with mock.patch.object( uuid, 'uuid4', return_value=uid):
            output = lexers.tasklist(conts)

        print(testname)
        assert output == expected


class Test_Mtask:
    @pytest.mark.parametrize(
        '    testname, conts, expected', [
            ('task',
                json.dumps([tokens.task()]),
                [tokens.task()],
            ),
            ('section',
                json.dumps([tokens.section()]),
                [tokens.section()],
            ),
            ('filedef',
                 json.dumps([tokens.file()]),
                 [tokens.file()],
            ),
        ]
    )
    def test_working(self, testname, conts, expected):
        output = lexers.mtask(conts)

        print(testname)
        assert output == expected
