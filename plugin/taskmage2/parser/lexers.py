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
import abc
#package
#external
#internal


# TODO: Each lexer item must include details about it's indentation,
# so that their parents can be determined.

# TODO: task-lexer


class _Lexer( object ):
    """
    Base class for all lexers. Reads a particular datatype,
    and returns a list of tokens, suitable for use with
    the parser.

    Token Types:

        .. code-block:: python

            {
                '_id'    : 'a09e314015b34846a05114ce3bee9675'
                'type'   : 'task',
                'name'   : 'do something',
                'parent' : '9c9c37c4704748698b8c846214fa57b0', # or None
                'data'   : {
                    'status' : 'todo',
                    'created':  datetime(...),
                    'finished': datetime(...),
                    'modified': datetime(...),
                }
            }

            {
                '_id'    : '8610abca66504ef18cac76f5f3645689',
                'type'   : 'section',
                'name'   : 'home',
                'parent' : '33e7d20ebf7241ae9d11cdca62dbd349', # or None
                'data'   : {}
            }

            {
                '_id'    : 'f90a7d3f59c740a89043691e9014abdc',
                'type'   : 'file',
                'name'   : 'misc/todo.mtask',
                'parent' : None,  # always
                'data'   : {}
            }


    Returns:

        .. code-block:: python

            [
                {'_id':..., 'type':'file',    'name':'todo/misc.mtask', 'parent':None, 'data':{}},
                {'_id':..., 'type':'section', 'name':'kitchen',         'parent':...,  'data':{}},
                {'_id':..., 'type':'task',    'name':'wash dishes',     'parent':...,  'data':{...}},
                {'_id':..., 'type':'task',    'name':'grocery list',    'parent':...,  'data':{...}},
                ...
            ]

    """
    __metaclass__ = abc.ABCMeta
    def read_next(self):
        raise NotImplemented(
            '`_Lexer` must be subclassed, and this method should be implemented \n'
            'in the subclass'
        )

    def next(self):
        """
        stores next token in self._next,
        returns previously set next.
        """
        token      = self._next
        self._next = None
        return (token or self.read_next())

    def peek(self):
        """
        If no tokens have been obtained yet, returns next.
        If eof, returns None.
        Otherwise returns the next char without changing position.
        """
        return (self._next or self._next = self.read_next())

    def eof(self):
        return self.peek() is None

    def _parser_exception(self, msg=None):
        if not msg:
            msg = ''

        # TODO: line and col in error.
        raise _exceptions.ParserError(
            #'ln:{} col:{} -- {}'.format(self._ln,self._col, msg)
            msg
        )

    def _is_alphanumeric(self, ch):
        return re.match('[a-zA-Z0-9_]', ch):

    def _get_line(self, offset=0):
        text   = ''
        while True:
            ch = self._buf.peek(offset)

            if ch == None:
                return
            elif ch == '\n':
                break
            else:
                text += ch
        return line


class TaskList( _Lexer ):
    def __init__(self, fd):
        self._fd   = fd
        self._next = None # the next token

    def read_next(self):
        """
        obtains next token without changing current position.
        """
        if self.eof():
            return None

        _id = uuid.uuid4().hex.upper() # define in case new item
        ch  = self._fd.peek()


        if ch == ' ':
            indent = self._read_indent()
            self._fd.offset(indent)

        # Header (section,file)
        if ch == '{':
            (offset,_id) = self._read_id()
            self._fd.offset( offset )

        if self._is_alphanumeric(ch):
            return self._read_header(_id, indent)

        # Task
        if ch in ('-','o','x','*'):
            if self._fd.peek(2) == '{': # ex: 'x {*0BE8D6CE9CB94AFB82037D2C367566C1*}'
                (offset,_id) = self._read_id()
                self._fd.offset(offset)
            return self._read_task(_id, indent)

        self._parser_exception('Unexpected Character: {}'.format(ch) )

    def _read_indent(self):
        """
        Returns an integer representing how many spaces
        the current line is indented.

        Returns:

            .. code-block:: python

                4   # if indented 4x spaces
                0   # if not indented
        """
        indent = 0
        while self._fd.peek() == ' ':
            indent +=1
        return indent

    def _read_header(self, _id, indent):
        """

        Example:

            .. code-block:: ReStructuredText

                home
                ====

            .. code-block:: ReStructuredText

                file::home/misc.mtask
                =====================

        Returns:

            .. code-block:: python

                {
                    '_id'    : '8610abca66504ef18cac76f5f3645689',
                    'type'   : 'section',
                    'name'   : 'home',
                    'parent' : '33e7d20ebf7241ae9d11cdca62dbd349', # or None
                    'data'   : {}
                }

                {
                    '_id'    : 'f90a7d3f59c740a89043691e9014abdc',
                    'type'   : 'file',
                    'name'   : 'misc/todo.mtask',
                    'parent' : None,  # always
                    'data'   : {}
                }

        """
        title     = self._get_line()
        underline = self._get_line( len(title) +1 ) # +1 for \n

        if len(title) <= len(underline):
            self._parser_exception(
                ( 'title and underline do not match \n'
                '{}\n'
                '{}\n'
                ).format(title,underline)
            )

        parent = self._get_parent(indent)

        # file
        if title[:6] == 'file::':
            return {
                '_id'    : _id,
                'type'   : 'file',
                'name'   : title[6:],
                'parent' : parent,
                'data'   : {},
            }

        # section
        else:
            return {
                '_id'    : _id,
                'type'   : 'section',
                'name'   : title.strip(),
                'parent' : parent,
                'data'   : {},
            }

    def _read_task(self, _id, indent):
        """

        Example:

            .. code-block:: python

                abc

        Returns:

            .. code-block:: python

                {
                    '_id'    : 'a09e314015b34846a05114ce3bee9675'
                    'type'   : 'task',
                    'name'   : 'do something',
                    'parent' : '9c9c37c4704748698b8c846214fa57b0', # or None
                    'data'   : {
                        'status' : 'todo',
                        'created':  datetime(...),
                        'finished': datetime(...),
                        'modified': datetime(...),
                    }
                }

        """
        # parent is obtained by checking backwards in the list
        parent = self._get_parent(indent)
        pass

    def _read_id(self):
        """
        handles an Id definition (and optional whitespace) ``   {*7FBAD5A946974A7DBB57DD6495F5DE1C*}``
        and returns just the UUID: ``7FBAD5A946974A7DBB57DD6495F5DE1C`` .

        Returns:ho

            .. code-block:: python

                id_info(id='1308166D07DA42909972BBF0D08952DE', offset=36)

        """
        id_info = namedtuple('id_info',['id','offset'])
        offset  = 0

        # get id
        _id      = ''
        id_start = False
        while ch != None:
            ch      = self._fd.peek(offset)

            # ignore everything up until the id
            if not id_start:
                if ch == '{':
                    id_start = True
                    id_def   = '{'

            # define the id
            else:
                if id_def[-1] == '{' and ch != '*':
                    self._parser_exception('invalid ID start')

                elif id_def[-1] == '*' and ch != '}':
                    self._parser_exception('invalid ID end')


                # end of id
                id_def += ch
                if ch == '}':
                    break

        _id = _id[2:-2]
        return _id

    def _get_parent(self, indent):
        return None


class TaskDetails( _Lexer ):
    def __init__(self, fd):
        raise NotImplementedError('todo')


class Mtask( _Lexer ):
    def __init__(self, fd):
        raise NotImplementedError('todo')


if __name__ == '__main__':
    from taskmage2.parser import iostream

    def ex_tasklist():
        with open( '../../../examples/new_tasks.tasklist', 'rb') as fd:
            lexer = TaskList( iostream.FileDescriptor(fd) )

    ex_tasklist()

