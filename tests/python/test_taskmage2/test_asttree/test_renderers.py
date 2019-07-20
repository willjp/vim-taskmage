#!/usr/bin/env python
"""
Name :          test_renderers.py
Created :       Jul 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   tests renderers.
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
import datetime
import json
from taskmage2.asttree import astnode, renderers
from taskmage2.utils import timezone


# external
# internal


class Test_TaskList(object):
    def test_status_todo(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == ['* task A']

    def test_status_done(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'done',
                    'created': None,
                    'finished': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == ['x task A']

    def test_status_started(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'wip',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == ['o task A']

    def test_status_skip(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'skip',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == ['- task A']

    def test_task_with_id(self):
        render = self.render([
            astnode.Node(
                _id='5F831BF3088A42209AF644CDD8962D3A',
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == ['*{*5F831BF3088A42209AF644CDD8962D3A*} task A']

    def test_task_multiline(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='line A\nline B\nline C',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == [
            '* line A',
            '  line B',
            '  line C',
        ]

    def test_task_multiline_with_id(self):
        render = self.render([
            astnode.Node(
                _id='CB1B055F2A38477D9D944E22D3608E6A',
                ntype='task',
                name='line A\nline B\nline C',
                data={
                    'status': 'todo',
                    'created': None,
                    'finished': False,
                    'modified': None,
                },
                children=None,
            )
        ])

        assert render == [
            '*{*CB1B055F2A38477D9D944E22D3608E6A*} line A',
            '  line B',
            '  line C',
        ]

    def test_section_without_id(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='section',
                name='cleanup',
                data={},
                children=None,
            )
        ])

        assert render == [
            '',
            'cleanup',
            '=======',
            '',
        ]

    def test_section_with_id(self):
        render = self.render([
            astnode.Node(
                _id='E083C4632F0D41CCA4C9712F3D4BD980',
                ntype='section',
                name='cleanup',
                data={},
                children=None,
            )
        ])

        assert render == [
            '',
            '{*E083C4632F0D41CCA4C9712F3D4BD980*}cleanup',
            '=======',
            '',
        ]

    def test_file_without_id(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='file',
                name='path/projectA.mtask',
                data={},
                children=None,
            )
        ])

        assert render == [
            '',
            'file::path/projectA.mtask',
            '=========================',
            '',
        ]

    def test_file_with_id(self):
        render = self.render([
            astnode.Node(
                _id='E083C4632F0D41CCA4C9712F3D4BD980',
                ntype='file',
                name='path/projectA.mtask',
                data={},
                children=None,
            )
        ])

        assert render == [
            '',
            '{*E083C4632F0D41CCA4C9712F3D4BD980*}file::path/projectA.mtask',
            '=============================================================',
            '',
        ]

    def test_section_with_tasks(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='section',
                name='cleanup',
                data={},
                children=[
                    astnode.Node(
                        _id=None,
                        ntype='task',
                        name='subtask A',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': False,
                            'modified': None,
                        },
                        children=None,
                    ),
                    astnode.Node(
                        _id=None,
                        ntype='task',
                        name='subtask B',
                        data={
                            'status': 'todo',
                            'created': None,
                            'finished': False,
                            'modified': None,
                        },
                        children=None,
                    ),
                ]
            )
        ])

        assert render == [
            '',
            'cleanup',
            '=======',
            '',
            '* subtask A',
            '* subtask B',
        ]

    def test_subsection_with_task_subtasks(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='section',
                name='cleanup',
                data={},
                children=[
                    astnode.Node(
                        _id=None,
                        ntype='section',
                        name='kitchen',
                        data={},
                        children=[
                            astnode.Node(
                                _id=None,
                                ntype='task',
                                name='oven',
                                data={
                                    'status': 'todo',
                                    'created': None,
                                    'finished': False,
                                    'modified': None,
                                },
                                children=[
                                    astnode.Node(
                                        _id=None,
                                        ntype='task',
                                        name='elements',
                                        data={
                                            'status': 'todo',
                                            'created': None,
                                            'finished': False,
                                            'modified': None,
                                        },
                                        children=None,
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            )
        ])
        print(render)

        assert render == [
            '',
            'cleanup',
            '=======',
            '',
            '',
            'kitchen',
            '-------',
            '',
            '* oven',
            '    * elements',
        ]

    def render(self, ast):
        """ Render parser_data using a TaskList renderer.

        Args:
            parser_data (list):
                A list of nodes, as returned from :py:meth:`taskmage2.parser.parsers.Parser.parse` .

                .. code-block:: python

                    [
                        Node('name':'home', 'type':'section', ... children=[
                            Node('name':'laundry', ... children=[]),
                            Node('name':'dishes', ... children=[]),
                            ...
                        ]),
                        Node('name':'taskA', ...children=[])
                    ]

        Returns:
            list:
                A list of lines.
        """
        tasklist = renderers.TaskList(ast)
        return tasklist.render()


class Test_Mtask(object):
    """
    the AST is essentially the same as JSON .mtask -- not many tests needed here.
    """
    def test_status_todo(self):
        render = self.render([
            astnode.Node(
                _id=None,
                ntype='task',
                name='task A',
                data={
                    'status': 'todo',
                    'created': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                    'finished': False,
                    'modified': datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC()),
                },
                children=None,
            )
        ])
        assert render == [
            {
                '_id': None,
                'type': 'task',
                'name': 'task A',
                'indent': 0,
                'data': {
                    'status': 'todo',
                    'created': '2018-01-01T00:00:00+00:00',
                    'finished': False,
                    'modified': '2018-01-01T00:00:00+00:00',
                },
                'parent': None,
            }
        ]

    def render(self, ast):
        """ Render parser_data using a TaskList renderer.

        Args:
            parser_data (list):
                A list of nodes, as returned from :py:meth:`taskmage2.parser.parsers.Parser.parse` .

                .. code-block:: python

                    [
                        Node('name':'home', 'type':'section', ... children=[
                            Node('name':'laundry', ... children=[]),
                            Node('name':'dishes', ... children=[]),
                            ...
                        ]),
                        Node('name':'taskA', ...children=[])
                    ]

        Returns:
            list:
                the parsed MTASK file as a list-of-dicts.
        """
        mtask = renderers.Mtask(ast)
        mtask_str = '\n'.join(mtask.render())
        return json.loads(mtask_str)