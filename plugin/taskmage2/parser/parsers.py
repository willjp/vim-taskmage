#!/usr/bin/env python
"""
Name :          taskmage2.parser.parsers.py
Created :       Jun 08, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Using a lexer, parses a file into an AST
                (Abstract Syntax Tree).
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
import os
# package
# external
# internal
from taskmage2 import data
from taskmage2.parser import renderers


class Parser(object):
    """ The parser transforms the tokens collected in the Lexer
    into a AST tree of Nodes. It can then render that AST
    tree into various output formats.

    Example:

        Example that converts a tasklist file to a mtask file.

        .. code-block:: python

            from taskmage2.parser import lexers, iostream, renderers

            with open('/path/file.tasklist', 'rb') as fd:
                lexer = lexers.TaskList(iostream.FileDescriptor(fd))
                parser = Parser(lexer)
                parser.render(render.Mtask)
                >>> [{'_id':.., ...}, {'_id':.., ...}, ...]

    """
    def __init__(self, lexer):
        """ Constructor.

        Args:
            lexer (taskmage2.lexers.Lexer):
                A lexer subclass instance, (TaskList, Mtask, ...),
                that has been loaded with data.
        """
        self.__lexer = lexer
        self.__lexer.read()

    def parse(self):
        """ Parses lexer into a nexted list of Nodes.

        Returns:

            .. code-block:: python

                [
                    Node('name':'home', 'type':'section', ... children=[
                        Node('name':'laundry', ... children=[]),
                        Node('name':'dishes', ... children=[]),
                        ...
                    ]),
                    Node('name':'taskA', ...children=[])
                ]

        """
        # create dictionary of id:node
        allnodes = {}  # {id:node}
        for token in self.__lexer.data:
            allnodes[token['_id']] = data.Node(
                _id=token['_id'],
                ntype=token['type'],
                name=token['name'],
                data=token['data'],
            )

        # create AST
        AST = []
        for token in self.__lexer.data:
            if token['parent']:
                child = allnodes[token['_id']]
                parent = allnodes[token['parent']]
                parent.children.append(child)
            else:
                node = allnodes[token['_id']]
                AST.append(node)

        return AST

    def render(self, renderer):
        """ Render this parser to an output format.

        Args:
            renderer (taskmage2.parser.renderers.Renderer):
                An un-initialized renderer subclass
                that will be used to render this parser
                object.

        Example:

            .. code-block:: python

                with open(path, 'rb') as fd:
                    lexer = TaskList(iostream.FileDescriptor(fd))
                    parser = Parser(lexer)
                    parser.render(render.Mtask)

        Returns:
            The output depends on the renderer.

        """
        if not issubclass(renderer, renderers.Renderer):
            raise TypeError(
                'Must specify output format'
            )

        renderer_inst = renderer(self)
        return renderer_inst.render()


if __name__ == '__main__':
    from taskmage2.parser import lexers, iostream, renderers

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
            parser = Parser(lexer)
            print(parser.parse())
            print()
            print(parser.renderers(renderers.TaskList))

    def ex_mtask():
        print('=====')
        print('Mtask')
        print('=====')
        print()

        with open('{}/examples/example.mtask_'.format(dirname), 'rb') as fd:
            lexer = lexers.Mtask(fd)
            parser = Parser(lexer)
            print(parser.parse())
            print()
            print(parser.renderers(renderers.Mtask))

    ex_tasklist()
    print('---')
    ex_mtask()
