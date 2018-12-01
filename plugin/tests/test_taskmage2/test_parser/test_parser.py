#!/usr/bin/env python
"""
Name :          test_parsers.py
Created :       Jun 08, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   tests parsers.
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
# package
from taskmage2.parser import parsers
from taskmage2 import data
# external
import mock
# internal


class Test_Parser:
    """ The parser converts a lexed format into nodes.
    """
    def test_task(self):
        parsed = self.parser([{
            # an empty, but syntactically correct task
            '_id': '6ed88ae2e7d94d2c88249a954782fc46',
            'type': 'task',
            'name': 'taskA',
            'indent': 0,
            'parent': None,
            'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
        }])
        assert parsed == [
            data.Node(
                _id='6ed88ae2e7d94d2c88249a954782fc46',
                ntype='task',
                name='taskA',
                data={'status': 'todo', 'created': None, 'finished': False, 'modified': None},
                children=None,
            )
        ]

    def test_section(self):
        parsed = self.parser([{
            '_id': 'e19cb28f203e476686f2fb5f2f0faae6',
            'type': 'section',
            'name': 'home',
            'indent': 0,
            'parent': None,
            'data': {},
        }])
        assert parsed == [
            data.Node(
                _id='e19cb28f203e476686f2fb5f2f0faae6',
                ntype='section',
                name='home',
                data={},
                children=None,
            )
        ]

    def test_file(self):
        parsed = self.parser([{
            '_id': '805c36f82cd74de5b44edff2b07bc125',
            'type': 'file',
            'name': 'path/home.mtask',
            'indent': 0,
            'parent': None,
            'data': {},
        }])
        assert parsed == [
            data.Node(
                _id='805c36f82cd74de5b44edff2b07bc125',
                ntype='file',
                name='path/home.mtask',
                data={},
                children=None,
            )
        ]

    def test_subtask(self):
        parsed = self.parser([
            {
                '_id': '6ed88ae2e7d94d2c88249a954782fc46',
                'type': 'task',
                'name': 'taskA',
                'indent': 0,
                'parent': None,
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            },
            {
                '_id': '032012b832f546d7bdc13a08ade41ba0',
                'type': 'task',
                'name': 'subtaskA',
                'indent': 4,
                'parent': '6ed88ae2e7d94d2c88249a954782fc46',
                'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
            },
        ])
        expected = [
            data.Node(
                _id='6ed88ae2e7d94d2c88249a954782fc46',
                ntype='task',
                name='taskA',
                data={'status': 'todo', 'created': None, 'finished': False, 'modified': None},
                children=[
                    data.Node(
                        _id='032012b832f546d7bdc13a08ade41ba0',
                        ntype='task',
                        name='subtaskA',
                        data={'status': 'todo', 'created': None, 'finished': False, 'modified': None},
                        children=None,
                    ),
                ]
            )
        ]
        assert parsed == expected

    def parser(self, lexed_list):
        """
        Produce a parser object, whose data is set
        to `lexer_contents`

        Args:
            lexed_list (list):

                 .. code-block:: python
                    [
                        {
                            '_id'    : 'a09e314015b34846a05114ce3bee9675'
                            'type'   : 'task',
                            'name'   : 'do something',
                            'parent' : '9c9c37c4704748698b8c846214fa57b0', # or None
                            'indent' : 0,  # number of spaces task is indented
                            'data'   : {
                                'status' : 'todo',
                                'created':  datetime(...),
                                'finished': datetime(...),
                                'modified': datetime(...),
                            }
                        }
                        ...
                    ]

        """
        # each lexer is a IterableUserDict,
        # `data` is it's value.
        lexer = mock.Mock()
        lexer.data = lexed_list

        parser = parsers.Parser(lexer)
        parser.lexer = lexer
        return parser.parse()
