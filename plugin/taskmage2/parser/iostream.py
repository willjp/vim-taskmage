#!/usr/bin/env python
"""
Name :          taskmage2.parser.iostream.py
Created :       Apr 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   Classes to abstract reading from file, stream, etc. to
                facilitate writing parsers.
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
from collections import namedtuple
import abc
# external
# internal


class IOStream(object):
    """ Base Interface for iostream objects.
    """
    __metaclass__ = abc.ABCMeta

    def next(self, offset=0):
        """ get next character, adjusting cursor position.
        """
        raise NotImplementedError()

    def peek(self, offset=0):
        """ get next character, without changing cursor position.
        """
        raise NotImplementedError()

    def peek_line(self, offset=0):
        """ Read until the end of the line (returns text)
        or the end of the file (returns None).

        Example:

            If ``^`` marks the current position of the cursor,

            ::
                'abcdefg'
                 ^ peek(0)
                returns 'abcdefg'


                'abcdefg'
                   ^ peek(2)
                returns 'cdefg'

        Returns:
            Nonetype: if current position is EOF
            str: if current position is a valid line
        """
        text = ''
        while True:
            ch = self.peek(offset)

            if ch is None:
                return None
            elif ch == '\n':
                return text
            else:
                text += ch
            offset += 1

    def offset(self, offset):
        """ Change the position of the cursor.

        Args:
            offset (int):
                desired position of cursor.
        """
        raise NotImplementedError()

    def eof(self):
        """ Returns True/False is the cursor at the end-of-file?
        """
        raise NotImplementedError()

    def read(self):
        """ Reads the entire stream.

        Returns:
            str:
                the file contents as a single, newline separated string.

                .. code-block:: python

                    'abc\ndef\nghi\n'

        """
        contents = ''
        offset = 0

        while True:
            line = self.peek_line(offset)
            if line is None:
                break
            contents += '{}\n'.format(line)
            offset += len(line) + 1  # line + '\n'

        return contents


class VimBuffer(IOStream):
    """ Abstracts vim python buffer object, so can read it as if it were raw-bytes.
    Adds functionality like `peek` , so can read ahead without changing the
    current position in the file.

    Notes:
        vim buffers themselves are a list of lines contained in a file.
        They do not include the carriage-return characters.

    Example:

        .. code-block:: python

            stream = VimBuffer(vim.current.buffer)
            vimbuf = VimBuffer(stream)

    """

    def __init__(self, buf=None):
        """
        Args:
            buf (vim.api.buffer.Buffer):
                A vim buffer. For example: ``vim.current.buffer`` .
        """
        super(VimBuffer, self).__init__()
        self._buf = buf
        self.line = -1
        self.col = -1

    def next(self, offset=0):
        """ Change position forwards, and retrieves the next character

        Returns:

            .. code-block:: python

                'a'     # a single character
                None    # if peek is at, or beyond the end-of-file

        """
        ch_info = self._peek()
        if not ch_info:
            return None
        else:
            self.line = ch_info.line
            self.col = ch_info.col
            return ch_info.char

    def peek(self, offset=0):
        """ Look at next character without changing positions.

        Returns:

            .. code-block:: python

                'a'     # a single character
                None    # if peek is at, or beyond the end-of-file

        """
        ch_info = self._peek(offset)
        if not ch_info:
            return None
        else:
            return ch_info.char

    def _peek(self, offset=0):
        """
        Obtains character at the position of `offset` .

        Returns:

            .. code-block:: python

                ch_info(line=1,col=5,char='b')  ## character info
                None                            ## if reached EOF
        """
        ch_info = namedtuple('ch_info', ['line', 'col', 'char'])

        ch = None
        col = self.col
        line = self.line

        # advance from current pos until `offset` is consumed.
        while offset >= 0:

            # line/col not initialized. new buffer.
            if line < 0:
                line = 0
                if col < 0:
                    col = 0
                ch = self._buf[line][col]

            # if column-index is valid within current line, return char
            elif col < (len(self._buf[line]) - 1):
                col += 1
                ch = self._buf[line][col]

            # if column-index is equal to the length of current line,
            # return newline char
            elif col == (len(self._buf[line]) - 1):
                col += 1
                ch = '\n'

            # if column-index is larger than line, overflow onto next line
            elif line < (len(self._buf) - 1):
                line += 1
                col = 0
                ch = self._buf[line][col]

            # EOF
            else:
                return None

            offset -= 1

        if hasattr(ch, 'decode'):
            ch = ch.decode()
        return ch_info(line, col, ch)

    def offset(self, offset):
        self.next(offset - 1)

    def eof(self):
        return self.peek() is None


class FileDescriptor(IOStream):
    """ Abstracts a python file-descriptor so files can be read
    one byte at a time. This is mostly for testing.

    Example:

        .. code-block:: python

            with open('/path/todo.tasklist', 'rb') as fd:
                filedesc = FileDescriptor(fd)

    """

    def __init__(self, fd):
        super(FileDescriptor, self).__init__()
        self._fd = fd
        self.pos = -1

    def next(self, offset=0):
        ch = self._peek(offset + 1)
        self.pos += offset + 1
        return ch

    def peek(self, offset=0):
        orig_pos = self.pos
        if orig_pos < 0:
            orig_pos = 0
        ch = self._peek(offset + 1)
        self._fd.seek(orig_pos)
        return ch

    def _peek(self, offset=0):
        pos = self.pos + offset
        self._fd.seek(pos)
        ch = self._fd.read(1)

        if hasattr(ch, 'decode'):
            ch = ch.decode()

        if ch == '':
            return None
        return ch

    def offset(self, offset):
        """
        Move the current file-position by an offset.

        Args:
            offset (int): the number of characters to offset the position by.
        """
        self.next(offset - 1)

    def eof(self):
        return self.peek() is None
