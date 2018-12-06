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
from taskmage2.ast import astnode, ast


# package
# external
# internal


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

    def parse(self, touch=False):
        """ Parses lexer into a nexted list of Nodes.

        Args:
            touch (bool):
                If True, updates last-modified timestamp, adds
                id if none present, etc.

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
            allnodes[token['_id']] = astnode.Node(
                _id=token['_id'],
                ntype=token['type'],
                name=token['name'],
                data=token['data'],
            )

        # create AST
        AST = ast.AbstractSyntaxTree()
        for token in self.__lexer.data:
            if token['parent']:
                child = allnodes[token['_id']]
                parent = allnodes[token['parent']]
                parent.children.append(child)
            else:
                node = allnodes[token['_id']]
                AST.append(node)

        return AST


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
            print(parser.renderers(taskmage2.ast.renderers.TaskList))

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
            print(parser.renderers(taskmage2.ast.renderers.Mtask))

    ex_tasklist()
    print('---')
    ex_mtask()
