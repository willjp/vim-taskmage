#!/usr/bin/env python
"""
Name :          taskmage2.parser.parser.py
Created :       Jun 08, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Using a lexer, parses a file into an AST
                (Abstract Syntax Tree).
________________________________________________________________________________
"""
# builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
# package
# external
# internal
from taskmage2 import data


class Parser(object):
    """
    The parser transforms the tokens collected in the Lexer
    into a AST tree of Nodes.
    """
    def __init__(self, lexer):
        self.__lexer = lexer
        self.__lexer.read()

    def parse(self):
        """

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
            allnodes[token['id']] = data.Node(
                id=token['_id'],
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
