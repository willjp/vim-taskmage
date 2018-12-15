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
# builtin
from __future__ import absolute_import, division, print_function
from collections import namedtuple
import os
import json
import abc
import uuid
import re
import sys
# external
# internal
from taskmage2.utils import excepts, timezone
from taskmage2.parser import fmtdata
if sys.version_info[0] < 3:
    from taskmage2.vendor import enum
else:
    import enum


class LexerTypes(enum.Enum):
    tasklist = 'tasklist'
    taskdetails = 'taskdetails'
    mtask = 'mtask'


class _Lexer(object):
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
                'indent' : 0,  # number of spaces task is indented
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
                'indent' : 0,  # incremented by 1 for each new header-level
                'data'   : {}
            }

            {
                '_id'    : 'f90a7d3f59c740a89043691e9014abdc',
                'type'   : 'file',
                'name'   : 'misc/todo.mtask',
                'parent' : None,  # always
                'indent' : 0,  # incremented by 1 for each new header-level
                'data'   : {}
            }


    Returns:

        .. code-block:: python

            [
                {'_id':..., 'type':'file',    'name':'todo/misc.mtask', 'indent':0, 'parent':None, 'data':{}},
                {'_id':..., 'type':'section', 'name':'kitchen',         'indent':0, 'parent':...,  'data':{}},
                {'_id':..., 'type':'task',    'name':'wash dishes',     'indent':0, 'parent':...,  'data':{...}},
                {'_id':..., 'type':'task',    'name':'grocery list',    'indent':0, 'parent':...,  'data':{...}},
                ...
            ]

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """
        Constructor.

        Args:
            iostream (iostream.IOStream):
                Special Parser File-Descriptor
        """
        self.data = []  # list of token dictionaries, as they appear.

    def read(self):
        """ Lex the entire source until EOF.
        """
        raise NotImplementedError()

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
        token = self._next
        self._next = None
        return (token or self.read_next())

    def peek(self):
        """
        If no tokens have been obtained yet, returns next.
        If eof, returns None.
        Otherwise returns the next char without changing position.
        """
        if self._next:
            return self._next
        else:
            self._next = self.read_next()
        return self._next()

    def eof(self):
        return self.peek() is None

    def _parser_exception(self, msg=None):
        if not msg:
            msg = ''

        # TODO: line and col in error.
        raise excepts.ParserError(
            # 'ln:{} col:{} -- {}'.format(self._ln,self._col, msg)
            msg
        )

    def _is_alphanumeric(self, ch):
        return re.match('[a-zA-Z0-9_]', ch)


class TaskList(_Lexer):
    """ Lexer for the TaskList format (that appears within vim).

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
    statuses = fmtdata.TaskList.statuses

    def __init__(self, iostream):
        super(TaskList, self).__init__()
        self._next = None  # the next token
        self._iostream = iostream   # file-descriptor abstracted into an iostream.IOStream

        self._headerchar_order = []  # underline character used for each level of
        # header indent. ex: ['=', '-', '.'] if
        # header lv1 is underlined with '==='
        # header lv2 is underlined with '---'
        # header lv3 is underlined with '...'
        # ...etc

    def read(self):
        """ Lexes the entire file-descriptor into a list of tokens.

        Returns:
            list: a list of dictionaries (each representing a token)

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
        token = self.read_next()
        while token is not None:
            token = self.read_next()
        return self.data

    def read_next(self):
        """ Obtains next token, saves to ``self.data`` , and returns it.

        Returns:

            A single token. See :py:obj:`_Lexer` for a list of all
            tokens.

            .. code-block:: python

                {
                    '_id'    : 'a09e314015b34846a05114ce3bee9675'
                    'type'   : 'task',
                    'name'   : 'do something',
                    'parent' : '9c9c37c4704748698b8c846214fa57b0', # or None
                    'indent' : 0,
                    'data'   : {
                        'status' : 'todo',
                        'created':  datetime(...),
                        'finished': datetime(...),
                        'modified': datetime(...),
                    }
                }
        """
        token = self._read_next()
        if token is not None:
            self.data.append(token)
        return token

    def _read_next(self):
        """
        Obtains next token.
        """

        _id = uuid.uuid4().hex.upper()  # define in case new item
        ch = self._iostream.peek()

        # EOF
        if ch is None:
            return None

        offset = 0
        indent = 0

        # =============
        # Handle Indent
        # =============
        if ch == ' ':
            indent = self._read_indent()
            self._iostream.offset(offset + indent)
            ch = self._iostream.peek()
            offset = 0

        # ===============================================
        # Newline (outside of taskdef, ignore & continue)
        # ===============================================
        if ch == '\n':
            self._iostream.offset(offset + 1)
            return self._read_next()

        # =====================
        # Header (section,file)
        # =====================
        # header with id
        if ch == '{':
            (offset, _id) = self._read_id()
            self._iostream.offset(offset)
            offset = 0
            ch = self._iostream.peek()
            header = self._read_header(_id, indent)
            return header

        # header without id
        if self._is_header(indent, offset):
            return self._read_header(_id, indent)

        # ====
        # Task
        # ====
        if ch in self.statuses:
            status = self.statuses[ch]
            self._iostream.offset(1)

            # ex: 'x{*0BE8D6CE9CB94AFB82037D2C367566C1*} task'
            if '{*' == '{}{}'.format(self._iostream.peek(), self._iostream.peek(1)):
                (offset, _id) = self._read_id()
                self._iostream.offset(offset)

            return self._read_task(status, _id, indent)

        self._parser_exception('Unexpected Character: {}\nline: {}'.format(repr(ch), self._iostream.peek_line()))

    def _read_indent(self, offset=0):
        """
        Returns an integer representing how many spaces
        the current line is indented.

        Returns:

            .. code-block:: python

                4   # if indented 4x spaces
                0   # if not indented
        """
        indent = 0
        while self._iostream.peek(offset + indent) == ' ':
            indent += 1
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
        title = self._iostream.peek_line()

        if title is None:
            raise RuntimeError('Expected a title. Received: "{}"'.format(title))

        underline = self._iostream.peek_line(len(title) + 1)  # +1 for \n

        if len(title.strip()) > len(underline):
            self._parser_exception(
                ('title and underline do not match \n'
                 '"{}"\n'
                 '"{}"\n'
                 ).format(title, underline)
            )

        (indent, parent) = self._get_header_hierinfo(underline[0])

        self._iostream.offset(sum([
            len(title) + 1,
            len(underline) + 1,
        ]))

        # file
        if title[:6] == 'file::':
            return {
                '_id': _id,
                'type': 'file',
                'name': title[6:],
                'parent': parent,
                'indent': indent,
                'data': {},
            }

        # section
        else:
            return {
                '_id': _id,
                'type': 'section',
                'name': title.strip(),
                'parent': parent,
                'indent': indent,
                'data': {},
            }

    def _read_task(self, status, _id, indent):
        """

        Example:

            By this stage, the status, and id will have been parsed.
            This method is responsible for identifying:

                * file (if one)
                * parent
                * status-name
                * metadata

            .. code-block:: python

                #
                # status     id (optional)              name
                #  /            |                        |
                # /             |                        |

                * {*42D4C5B8B83547468DB9D9BC738AE587*} todo task
                o {*1EE4C290F1CC4FA1B33FD1DBABF512B3*} wip task
                x {*1EE4C290F1CC4FA1B33FD1DBABF512B3*} finished task
                - {*F46AD99478AE480081DA356201E0229E*} skipped task

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
        offset = 0
        newline = False
        name = ''

        parent = self._get_task_parent(indent)

        task = {
            '_id': _id,
            'type': 'task',
            'name': '',
            'indent': indent,
            'parent': parent,
            'data': {
                'status': status,
                'created': None,
                'finished': None,  # do not assign date here
                'modified': None,  # utcnow() if changed only
            },
        }

        while True:
            ch = self._iostream.peek(offset)

            # EOL encountered
            if ch is None:
                self._iostream.offset(offset)
                task['name'] = name.strip()
                return task

            # parse indentation of newline
            if newline:
                _indent = self._read_indent(offset)
                ch_after_indent = self._iostream.peek(offset + _indent)

                # newline is the start of something else
                # *NOT* a continuation of this task
                if any([
                    _indent < indent,
                    ch_after_indent in self.statuses,
                    self._is_header(_indent, offset),
                ]):
                    self._iostream.offset(offset)
                    task['name'] = name.strip()
                    return task

                # newline is a continuation of task.
                # continute reading - at least until end of line
                newline = False
                if _indent:
                    offset += _indent - 1  # so later offset+=1 still works

            if ch == '\n':
                newline = True
                name = name.strip()
            name += ch
            offset += 1

    def _read_id(self):
        """
        handles an Id definition (and optional whitespace) ``   {*7FBAD5A946974A7DBB57DD6495F5DE1C*}``
        and returns just the UUID: ``7FBAD5A946974A7DBB57DD6495F5DE1C`` .

        Returns:

            .. code-block:: python

                id_info(offset=36, id='1308166D07DA42909972BBF0D08952DE')

        """
        id_info = namedtuple('id_info', ['offset', 'id'])
        offset = -1

        # get id
        _id = ''
        ch = ''
        id_start = False
        while ch is not None:
            offset += 1
            ch = self._iostream.peek(offset)

            # ignore everything up until the id
            if not id_start:
                if ch == '{':
                    id_start = True
                    id_def = '{'

            # define the id
            else:
                if id_def[-1] == '{' and ch != '*':
                    self._parser_exception('invalid ID start')

                elif id_def[:2] == '{*':
                    pass

                elif id_def[-1] == '*' and ch != '}':
                    self._parser_exception('invalid ID end')

                # end of id
                id_def += ch
                if ch == '}':
                    offset += 1
                    break

        _id = id_def[2:-2]
        return id_info(offset, _id)

    def _is_header(self, indent, offset):

        title = self._iostream.peek_line(offset)

        if title is None:
            return False

        # title may or may not have id (depending on when is_header() is run)
        title_without_id = re.sub('^{\\*[A-Z0-9]+\\*}', '', title)

        # underlines must be at least as long as title
        # ex:   title
        #       ======
        underline = self._iostream.peek_line(offset + len(title) + 1)  # +1 for \n

        if not underline:
            return False

        if len(title_without_id) > len(underline):
            return False

        # underlines must be made of the same character
        # ex: '======='
        uline_ch = underline[0]
        for ch in underline:
            if ch != uline_ch:
                return False

        return True

    def _get_task_parent(self, indent):
        """ Finds the nearest parent of a token with the provided `indent`.

        Searches previously encountered tokens (section, task, ...)
        for a token with a smaller indent than `indent`.

        Args:
            indent (int): The number of characters a token is indented.

        Returns:

            .. code-block:: python

                'f2e2dc9f37d24709a5eede3b3499be3f' # the id of the parent
                None                               # if item has no parents

        """

        if indent == 0:
            # return the nearest section-header if one
            # occurs before task
            for token in reversed(self.data):
                if token['type'] == 'section':
                    return token['_id']
            # otherwise return None
            return None

        # if the task is indented, return the nearest
        # less-indented tokenid. Note that this might
        # be a task, section, or file.
        for token in reversed(self.data):
            if token['indent'] < indent:
                return token['_id']
        return None

    def _get_header_hierinfo(self, underline_char):
        """
        Returns:

            A tuble with the indent (header-level), and parent header.

            .. code-block:: python

                (indent=1, parent='dd9eabde5f054c7c8557b408e9d81887')
                (indent=0, parent=None)
        """

        _returnval = namedtuple('header_hierinfo', ['indent', 'parent'])

        if not self._headerchar_order:
            self._headerchar_order.append(underline_char)
            indent = 0
        elif underline_char in self._headerchar_order:
            indent = self._headerchar_order.index(underline_char)
        else:
            self._headerchar_order.append(underline_char)
            indent = len(self._headerchar_order) - 1

        if indent == 0:
            return _returnval(indent=0, parent=None)

        # find the nearest header or file with a lower
        # level of indentation.
        for token in reversed(self.data):
            if all([
                token['indent'] < indent,
                token['type'] in ('section', 'file')
            ]):
                return _returnval(indent=indent, parent=token['_id'])

        self._parser_exception(
            (
                'Header underline character "{}" indicates it is a \n'
                'header-level of "{}", but no headers above it were found. \n'
            ).format(underline_char, indent)
        )


class TaskDetails(_Lexer):
    """ Displays editable Mtask details for a single task.

    Exposes details Mtask details that are not present within TaskList.
    """
    def __init__(self, iostream):
        self._iostream = iostream  # file-desriptor to the file being parsed.
        raise NotImplementedError('todo')


class Mtask(_Lexer):
    """ Lexer for  ``*.mtask``  files (JSON).

    Example:

        Example of an *.mtask file (stored in the same format as the Lexer object).

        .. code-block:: python

            [
                {'_id':'...', 'type':'task', 'name':'do something', 'parent':..., 'indent':0, 'data':{...}},
                {'_id':'...', 'type':'task', 'name':'do something', 'parent':..., 'indent':0, 'data':{...}},
                ...
            ]

    """
    statuses = {
        'done',
        'skip',
        'wip',
        'todo',
    }

    def __init__(self, fd):
        """
        Constructor:

            Args:
                fd:
                    A python file-descriptor (as returned by ``open`` )
        """
        super(Mtask, self).__init__()
        self._fd = fd
        self._rawdata = []  # the JSON file data, serialized into a python list
        self._index = -1    # current place in of self._rawdata[]
        self._read()

    def read(self):
        token = ''
        while token is not None:
            token = self.read_next()
        return self.data

    def _read(self):
        data = self._fd.read()
        if not data:
            self._rawdata = []
        else:
            self._rawdata = json.loads(data)

    def read_next(self):
        token = self._read_next()
        if token:
            self.data.append(token)
        return token

    def _read_next(self):
        """ Reads the JSON object (serialized into python), validates,
        and makes any more required type changes.
        """
        self._index += 1
        index = self._index

        type_map = dict(
            task=self._read_task,
            section=self._read_section,
            file=self._read_filedef,
        )

        if self._index >= len(self._rawdata):
            return None

        type_ = self._rawdata[index].get('type', None)
        if type_ in type_map:
            return type_map[type_](index)

        self._parser_exception(
            (
                'Invalid entry in mtaskfile: \n'
                'key "type" has unexpected value: "{}"\n'
                '{}\n'
            ).format(self._rawdata[index]['type'], repr(self._rawdata[index]))
        )

    def _read_task(self, index):
        dtype = self._rawdata[index]

        self._validate_keys(
            index=index,
            data=dtype,
            reqd_keys={'_id', 'type', 'name', 'parent', 'indent', 'data'},
            desc='task',
        )

        self._validate_keys(
            index=index,
            data=dtype['data'],
            reqd_keys={'status', 'created', 'finished', 'modified'},
            desc='task',
        )

        if dtype['data']['status'] not in self.statuses:
            self._parser_exception('Invalid status: {}'.format(dtype['data']['status']))

        # parse date into
        for key in ('created', 'finished', 'modified'):
            if dtype['data'][key]:
                isodate = dtype['data'][key]
                dtype['data'][key] = timezone.parse_utc_iso8601(isodate)

        return dtype

    def _read_section(self, index):
        dtype = self._rawdata[index]

        self._validate_keys(
            index=index,
            data=dtype,
            reqd_keys={'_id', 'type', 'name', 'parent', 'indent', 'data'},
            desc='task',
        )

        self._validate_keys(
            index=index,
            data=dtype['data'],
            reqd_keys=set(),
            desc='task',
        )

        return dtype

    def _read_filedef(self, index):
        dtype = self._rawdata[index]

        self._validate_keys(
            index=index,
            data=dtype,
            reqd_keys={'_id', 'type', 'name', 'parent', 'indent', 'data'},
            desc='task',
        )

        self._validate_keys(
            index=index,
            data=dtype['data'],
            reqd_keys=set(),
            desc='task',
        )

        return dtype

    def _validate_keys(self, index, data, reqd_keys, desc):
        """
        Args:
            index (int):
                The current location in list.

            data (dict):
                The dictionary we are validating

            reqd_keys (list)
        """
        missing_keys = set(data.keys()) - set(reqd_keys)
        extra_keys = set(reqd_keys) - set(data.keys())

        if missing_keys:
            self._parser_exception((
                'Token at index {} is formatted improperly: \n'
                '{}\n'
                'missing keys: {}\n'
                'received: {}\n'
            ).format(index, desc, data, missing_keys, data)
            )

        if extra_keys:
            self._parser_exception((
                'Task at index {} is formatted improperly: \n'
                '{}\n'
                'missing keys: {}\n'
                'received: {}\n'
            ).format(index, desc, data, missing_keys, data)
            )


def get_lexer(iostream, lexertype):
    lexertype = LexerTypes(lexertype)
    lexertype_map = {
        LexerTypes.tasklist:    TaskList,
        LexerTypes.taskdetails: TaskDetails,
        LexerTypes.mtask:       Mtask,
    }
    return lexertype_map[lexertype](iostream)


if __name__ == '__main__':
    from taskmage2.parser import iostream

    def ex_tasklist():
        print(
            '\n'
            '========\n'
            'TaskList\n'
            '========\n'
        )

        _scriptdir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(
            '{}/../../../examples/sample_tasks.tasklist'.format(_scriptdir)
        )
        with open(path, 'rb') as fd:
            lexer = TaskList(iostream.FileDescriptor(fd))

            token = ''
            while token is not None:
                token = lexer.read_next()
                print(token)

    def ex_mtask():
        print(
            '\n'
            '=====\n'
            'Mtask\n'
            '=====\n'
        )
        _scriptdir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.abspath(
            '{}/../../../examples/sample_tasks.mtask'.format(_scriptdir)
        )
        with open(path, 'r') as fd:
            lexer = Mtask(fd)

            token = ''
            while token is not None:
                token = lexer.read_next()
                print(token)

    ex_tasklist()
    ex_mtask()
