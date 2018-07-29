#!/usr/bin/env python
"""
Name :          taskmage2.parser.render.py
Created :       Jul 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   A collection of classes to render a Parser object
                into different formats.
________________________________________________________________________________
"""
# builtin
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
# package
from taskmage2.parser import fmtdata
# external
# internal


class _Renderer(object):
    def __init__(self, parser):
        super(_Renderer, self).__init__()
        self._parser = parser

    @property
    def parser(self):
        return self._parser

    def render(self):
        raise NotImplementedError


class TaskList(_Renderer):
    """
    Renders a :py:obj:`taskmage2.parser.Parser` object into the
    tasklist format.

    Example:

        Example of a ``TaskList`` format file.

        .. code-block:: ReStructuredText

            * {*768D3CDC543044488462C9CE6B823404*} saved task
                * new task
                o started task
                - skipped task
                x finished task
                    * another subtask

            home
            ====

            * clean kitchen
    """
    indent_lvl_chars = fmtdata.TaskList.indent_lvl_chars

    def __init__(self, parser):
        super(TaskList, self).__init__(parser)

    def render(self):
        """
        Renders the parser's Abstract-Syntax-Tree.

        Returns:

            .. code-block:: python

                [
                    '* task1',
                    '    * subtask1',
                    '* task2',
                    ...
                ]

        """
        ast = self.parser.parse()
        render = []

        for node in ast:
            render = self._render_node(render, node, indent=0)

        return render

    def _render_node(self, render, node, indent=0):
        """
        Recursively renders a node, until all children have been descended
        into.

        Returns:
            The current render.

            .. code-block:: python

                [
                    'line1',
                    'line2',
                    'line3',
                    ...
                ]

        """
        node_renderer_map = {
            'file':     self._render_fileheader,
            'section':  self._render_sectionheader,
            'task':     self._render_task,
        }
        if node.type not in node_renderer_map:
            raise NotImplementedError(
                'unexpected nodetype: {}'.format(repr(node))
            )
        render.extend(
            node_renderer_map[node.type](node, indent)
        )

        for child in node.children:
            render = self._render_node(render, child, indent=indent+1)

        return render

    def _render_fileheader(self, node, indent=0):
        """
        renders a single file-header node.

        Returns:
            Each list-entry is a separate line.

            .. code-block:: python

                [
                    '',
                    'file::home/misc.task',
                    '====================',
                    '',
                ]

                [
                    '',
                    '{*A8347624443342C1AA3A959622521E23*}file::home/misc.task',
                    '========================================================',
                    '',
                ]

        """
        char = self.indent_lvl_chars[indent]

        header_title = 'file::{}'.format(node.name)
        if node.id:
            header_title = ''.join(['{*', node.id, '*}'])

        return [
            '',
            header_title,
            char * len(header_title),
            '',
        ]

    def _render_sectionheader(self, node, indent=0):
        """
        renders a single section-header node.

        Returns:

            .. code-block:: python

                [
                    '',
                    'kitchen tasks',
                    '=============',
                    '',
                ]

                [
                    '',
                    '{*CE1AFBD934064E298ABFDA94AE58D838*} admin tasks',
                    '================================================',
                    '',
                ]

        """
        char = self.indent_lvl_chars[indent]

        header_title = ''
        if node.id:
            header_title += ''.join(['{*', node.id, '*}'])

        header_title += node.name

        return [
            '',
            header_title,
            char * len(header_title),
            '',
        ]

    def _render_task(self, node, indent=0):
        """
        Renders a single task node.

        Returns:

            .. code-block:: python

                ['* wash dishes']
                ['* {*FF3DB940B75948A6A7C5BBBF4B0AFD0B*} clean counters']

        """
        data = {
            'status_char':  '',
            'id_str':       '',
            'indent_spc':   '',
            'name':         node.name,
        }

        fmtdata.TaskList.statuschar(node.data['status'])

        data['status_char'] = fmtdata.TaskList.statuschar(node.data['status'])

        if node.id:
            data['id_str'] = ''.join(['{*', node.id, '*}', ' '])

        data['indent_spc'] = ' ' * (4 * indent)

        lines = node.name.split('\n')

        returns = ['{indent_spc}{status_char} {id_str} '.format(**data) + lines[0]]
        for i in range(1, len(lines)):
            returns.append('{}  {}'.format(data['indent_spc'], lines[i]))

        return returns


class TaskDetails(_Renderer):
    def __init__(self, parser):
        pass


class Mtask(_Renderer):
    def __init__(self, parser):
        super(TaskList, self).__init__(parser)

    def render(self):
        """
        Renders the parser's Abstract-Syntax-Tree.

        Returns:

            .. code-block:: python

                [
                    'line1',
                    'line2',
                    'line3',
                    ...
                ]

        """
        ast = self.parser.parse()
        render = []

        for node in ast:
            render = self._render_node(render, node, indent=0)

        return render

    def _render_node(self, render, node, indent=0):
        """
        Recursively renders a node, until all children have been descended
        into.

        Returns:
            The current render.

            .. code-block:: python

                [
                    {'_id':..., 'type':'file',    'name':'todo/misc.mtask', 'indent':0, 'parent':None, 'data':{}},
                    {'_id':..., 'type':'section', 'name':'kitchen',         'indent':0, 'parent':...,  'data':{}},
                    {'_id':..., 'type':'task',    'name':'wash dishes',     'indent':0, 'parent':...,  'data':{...}},
                    {'_id':..., 'type':'task',    'name':'grocery list',    'indent':0, 'parent':...,  'data':{...}},
                    ...
                ]

        """
        node_renderer_map = {
            'file':     self._render_fileheader,
            'section':  self._render_sectionheader,
            'task':     self._render_task,
        }
        if node.type not in node_renderer_map:
            raise NotImplementedError(
                'unexpected nodetype: {}'.format(repr(node))
            )
        render.extend(
            node_renderer_map[node.type](node, indent)
        )

        for child in node.children:
            render = self._render_node(render, child, indent=indent+1)

        return render

    def _render_fileheader(self, render, node, indent=0):
        """
        Returns:

            .. code-block:: python


        """
        pass

    def _render_sectionheader(self, render, node, indent=0):
        pass

    def _render_task(self, render, node, indent=0):
        pass


if __name__ == '__main__':
    from taskmage2.parser import lexers, iostream, parser

    dirname = os.path.dirname(os.path.abspath(__file__))
    for i in range(3):
        dirname = os.path.dirname(dirname)

    with open('{}/examples/example.tasklist'.format(dirname), 'rb') as fd:
        lexer = lexers.TaskList(iostream.FileDescriptor(fd))
        parser_ = parser.Parser(lexer)
        renderer = TaskList(parser_)
        for line in renderer.render():
            print(line)
