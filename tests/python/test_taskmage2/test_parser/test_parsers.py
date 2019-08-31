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
from __future__ import absolute_import, division, print_function
from taskmage2.asttree import astnode, asttree
from taskmage2.parser import parsers, lexers
import mock
import six
import json


# =====
# Utils
# =====


def get_iostream(text):
    fd = six.StringIO()
    fd.write(text)
    fd.seek(0)
    return fd


def get_lexer_mtask(text):
    fd = get_iostream(text)
    lexer = lexers.Mtask(fd)
    return lexer


# =====
# Tests
# =====


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
            astnode.Node(
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
            astnode.Node(
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
            astnode.Node(
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
            astnode.Node(
                _id='6ed88ae2e7d94d2c88249a954782fc46',
                ntype='task',
                name='taskA',
                data={'status': 'todo', 'created': None, 'finished': False, 'modified': None},
                children=[
                    astnode.Node(
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

    def test_subtask_assigns_parent(self):
        """ Children keep a reference to their parent.
        """
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

        assert parsed[0][0].id == '032012b832f546d7bdc13a08ade41ba0'
        assert parsed[0][0].parent.id == '6ed88ae2e7d94d2c88249a954782fc46'

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


class Test_parse:
    def test_produces_ast(self):
        # input
        data = [
                {
                    '_id': 'C5ED1030425A436DABE94E0FCCCE76D6',
                    'type': 'section',
                    'name': 'home',
                    'indent': 0,
                    'parent': None,
                    'data': {},
                },
        ]
        fd = get_iostream(json.dumps(data))
        AST = parsers.parse(fd, lexers.LexerTypes.mtask)

        # expects
        expected_AST = asttree.AbstractSyntaxTree(
            [
                astnode.Node(
                    _id='C5ED1030425A436DABE94E0FCCCE76D6',
                    ntype=astnode.NodeType.section,
                    name='home',
                ),
            ]
        )

        assert AST == expected_AST




    def test_sets_parent_attribute_on_ast_nodes(self):
        assert False
