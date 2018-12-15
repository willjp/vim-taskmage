#!/usr/bin/env python
"""
Name :          taskmage2.parser.renderers.py
Created :       Jul 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   A collection of classes to render a Parser object
                into different formats.
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
import os
import abc
import json
from taskmage2.parser import fmtdata


# external
# internal


class Renderer(object):
    """ Abstract-Base-class for all renderers. Renders a
    :py:obj:`taskmage2.parser.parsers.Parser` object into various formats.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, ast):
        super(Renderer, self).__init__()
        self._ast = ast

    @property
    def ast(self):
        return self._ast

    def render(self):
        """ render AST in provided format.
        """
        raise NotImplementedError


class TaskList(Renderer):
    """ `AST` to ReStructuredText inspired TaskList format.
    Displays files/sections/tasks, hierarchy, and status.

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

    def __init__(self, ast):
        super(TaskList, self).__init__(ast)

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
        render = []

        for node in self.ast:
            render = self._render_node(render, node, parent=None, indent=0)

        return render

    def _render_node(self, render, node, parent, indent=0):
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
            'file':    self._render_fileheader,
            'section': self._render_sectionheader,
            'task':    self._render_task,
        }
        if node.type not in node_renderer_map:
            raise NotImplementedError(
                'unexpected nodetype: {}'.format(repr(node))
            )
        render.extend(
            node_renderer_map[node.type](node, parent, indent)
        )

        for child in node.children:
            # indentation is reset at 0 for tasks within sections/files
            if all([
                node.type in ('section', 'file'),
                child.type == 'task',
            ]):
                render = self._render_node(render, child, node, indent=0)
            else:
                render = self._render_node(render, child, node, indent=indent + 1)

        return render

    def _render_fileheader(self, node, parent, indent=0):
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
            header_title = ''.join(['{*', node.id, '*}']) + header_title

        return [
            '',
            header_title,
            char * len(header_title),
            '',
        ]

    def _render_sectionheader(self, node, parent, indent=0):
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
            char * len(node.name),
            '',
        ]

    def _render_task(self, node, parent, indent=0):
        """
        Renders a single task node.

        Returns:

            .. code-block:: python

                ['* wash dishes']
                ['*{*FF3DB940B75948A6A7C5BBBF4B0AFD0B*} clean counters']

        """
        # produce `data`
        data = {
            'status_char': '',
            'id_str': '',
            'indent_spc': '',
            'name': node.name,
        }

        fmtdata.TaskList.statuschar(node.data.status)

        data['status_char'] = fmtdata.TaskList.statuschar(node.data.status)

        if node.id:
            data['id_str'] = ''.join(['{*', node.id, '*}'])

        data['indent_spc'] = ' ' * (4 * indent)

        lines = node.name.split('\n')

        # format output
        returns = ['{indent_spc}{status_char}{id_str} '.format(**data) + lines[0]]
        for i in range(1, len(lines)):
            returns.append('{}  {}'.format(data['indent_spc'], lines[i]))

        return returns


class TaskDetails(Renderer):
    """ `AST` to an INI inspired view of a single task's info.
    """
    def __init__(self, ast):
        raise NotImplementedError()


class Mtask(Renderer):
    """ `AST` to JSON - stores all info.
    """
    def __init__(self, ast):
        super(Mtask, self).__init__(ast)

    def render(self):
        """
        Renders the parser's Abstract-Syntax-Tree (list of `data.Node` s ) into a JSON string.

        Returns:

            .. code-block:: python

                [
                    'line1',
                    'line2',
                    'line3',
                    ...
                ]

        """
        render = []

        for node in self.ast:
            render = self._render_node(render, node, indent=0)

        render_as_json = json.dumps(render, indent=2)
        render = render_as_json.split('\n')
        render.append('')
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
            'task':    self._render_task,
            'section': self._render_sectionheader,
            'file':    self._render_fileheader,
        }
        if node.type not in node_renderer_map:
            raise NotImplementedError(
                'unexpected nodetype: {}'.format(repr(node))
            )
        render.append(
            node_renderer_map[node.type](render, node, indent)
        )

        for child in node.children:
            render = self._render_node(render, child, indent=indent + 1)

        return render

    def _get_parent(self, render, node, indent):
        if indent == 0:
            return None

        for i in reversed(range(len(render))):
            if render[i]['indent'] < indent:
                return render[i]['_id']

        raise RuntimeError('could not find parent')

    def _render_fileheader(self, render, node, indent=0):
        """
        Returns:

            .. code-block:: python


        """

        return {
            '_id': node.id,
            'type': node.type,
            'name': node.name,
            'indent': indent,
            'parent': self._get_parent(render, node, indent),
            'data': {},
        }

    def _render_sectionheader(self, render, node, indent=0):
        return {
            '_id': node.id,
            'type': node.type,
            'name': node.name,
            'indent': indent,
            'parent': self._get_parent(render, node, indent),
            'data': {},
        }

    def _render_task(self, render, node, indent=0):
        created = None
        finished = False
        modified = None

        if node.data.created is not None:
            created = node.data.created.isoformat()

        if node.data.finished:
            finished = node.data.finished.isoformat()

        if node.data.modified is not None:
            modified = node.data.modified.isoformat()

        return {
            '_id': node.id,
            'type': node.type,
            'name': node.name,
            'indent': indent,
            'parent': self._get_parent(render, node, indent),
            'data': {
                'status': node.data.status,
                'created': created,
                'finished': finished,
                'modified': modified,
            },
        }


if __name__ == '__main__':
    from taskmage2.parser import lexers, iostream, parser

    dirname = os.path.dirname(os.path.abspath(__file__))
    for i in range(3):
        dirname = os.path.dirname(dirname)

    def ex_tasklist():
        print('========')
        print('Tasklist')
        print('========')
        print()

        with open('{}/examples/example.tasklist'.format(dirname), 'rb') as fd:
            lexer = lexers.TaskList(iostream.FileDescriptor(fd))
            parser_ = parser.Parser(lexer)
            renderer = TaskList(parser_)
            for line in renderer.render():
                print(line)

    def ex_mtask():
        print('=====')
        print('Mtask')
        print('=====')
        print()

        with open('{}/examples/example.mtask_'.format(dirname), 'rb') as fd:
            lexer = lexers.Mtask(fd)
            parser_ = parser.Parser(lexer)
            renderer = Mtask(parser_)
            for line in renderer.render():
                print(line)

    ex_tasklist()
    ex_mtask()
