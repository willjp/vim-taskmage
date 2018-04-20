#!/usr/bin/env python
"""
Name :          taskmage.parser.lexers.py
Created :       Apr 19, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Lexers for all of the various datatypes tasks can
                be stored in.

                The goal of a lexer is to parse info from a particular
                type (mtask, tasklist, taskdetails, ...) into a list of
                tokens, which can be used in ``parser.parser.Parser()``
________________________________________________________________________________
"""
#builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
import sys
import os
#package
#external
#internal



class _Lexer( object ):
    """
    Base class for all lexers. Reads a particular datatype,
    and returns a list of tokens, suitable for use with
    the parser.

    Returns:

        .. code-block:: python

            [
                {'
            ]

    """
    pass


class TaskList( _Lexer ):
    def __init__(self, fd):
        self._current = None # the current token

    def read_next(self):
        pass

    def next(self):
        token         = self._current
        self._current = None
        return (token or self.read_next())

    def peek(self):
        return (self._current or self._current = self.read_next())

    def eof(self):
        return self.peek() is None


class TaskDetails( _Lexer ):
    pass

class Mtask( _Lexer ):
    pass


