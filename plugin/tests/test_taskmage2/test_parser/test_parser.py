#!/usr/bin/env python
"""
Name :          test_parser.py
Created :       Jun 08, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   tests parser.
________________________________________________________________________________
"""
# builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
# package
from taskmage2.testutils import lexers, nodes, tokens, core
from taskmage2.parser import parser
# external
import pytest
import mock
# internal


def build_parser(lexer_contents):
    """
    Produce a parser object, whose data is set
    to `lexer_contents`
    """
    lexer = mock.Mock()
    lexer.data = lexer_contents

    _parser = parser.Parser(lexer)
    _parser.lexer = lexer
    return _parser


class Test_Parser:
    @pytest.mark.parametrize(
        'testname, lexer_contents, expected', [
        ('default task',
            [tokens.task()],
            [nodes.task()],
        ),
        ('default section',
            [tokens.section()],
            [nodes.section()],
        ),
        ('default file',
            [tokens.file()],
            [nodes.file()],
        ),
    ])
    def test_defaults(self, testname, lexer_contents, expected):
        parserobj = build_parser(lexer_contents)
        ast = parserobj.parse()
        print(testname)
        assert ast == expected

    @pytest.mark.parametrize(
        'testname, lexer_conts, expected', [
        ('subtask',
            [tokens.task(), tokens.task({'_id': '59fd4a25ab6f40c3959c99ecc876f3bb', 'indent': 4, 'parent': core.uuid})],
            [nodes.task( children=[nodes.task(_id='59fd4a25ab6f40c3959c99ecc876f3bb')] )],
        ),
        ('sub, subtask',
            [
                tokens.task(),
                tokens.task({'_id': '59fd4a25ab6f40c3959c99ecc876f3bb', 'indent': 4, 'parent': core.uuid}),
                tokens.task({'_id': '7ef3a697df094a7b902bd670b47492d4', 'indent': 8, 'parent': '59fd4a25ab6f40c3959c99ecc876f3bb'}),
            ],
            [
                nodes.task( children=[
                    nodes.task(_id='59fd4a25ab6f40c3959c99ecc876f3bb', children=[
                        nodes.task(_id='7ef3a697df094a7b902bd670b47492d4')
                    ])
                ])
            ],
         ),
    ])
    def test_hierarchy(self, testname, lexer_conts, expected):
        parserobj = build_parser(lexer_conts)
        ast = parserobj.parse()
        print(testname)
        assert ast == expected
