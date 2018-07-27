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
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
from collections import namedtuple
import abc
# package
# external
# internal

class IOStream(object):
    """
    Base Interface for iostream objects.
    """
    __metaclass__ = abc.ABCMeta
    def next(self, offset=0):
        raise NotImplemented()

    def peek(self, offset=0):
        raise NotImplemented()

    def peek_line(self, offset=0):
        """
        Read until the end of the line (returns text)
        or the end of the file (returns None).
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
        raise NotImplemented()

    def eof(self):
        raise NotImplemented()


class VimBuffer(IOStream):
    """
    Abstracts vim python buffer object, so can read it as if it were raw-bytes.
    Adds functionality like `peek` , so can read ahead without changing the
    current position in the file.

    Example:

        .. code-block:: python

            stream = VimBuffer(vim.current.buffer)
            vimbuf = VimBuffer(stream)

    """

    def __init__(self, buf):
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
        """
        change position forwards, and retrieves the next character

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
        """
        look at next character without changing positions

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

        # calculate offset
        while offset >= 0:
            if line < 0:
                line = 0
                col = 0
                ch = self._buf[line][col]

            elif col < (len(self._buf[line]) - 1):
                col += 1
                ch = self._buf[line][col]

            elif col == (len(self._buf[line]) - 1):
                col += 1
                ch = '\n'

            elif line < (len(self._buf) - 1):
                line += 1
                col = 0
                ch = self._buf[line][col]

            else:
                return None  # EOF

            offset -= 1

        if hasattr(ch, 'decode'):
            ch = ch.decode()
        return ch_info(line, col, ch)

    def offset(self, offset):
        self.next(offset - 1)

    def eof(self):
        return self.peek() is None


class FileDescriptor(IOStream):
    """
    Abstracts a python file-descriptor so files can be read
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
