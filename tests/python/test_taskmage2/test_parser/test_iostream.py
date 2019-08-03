#!/usr/bin/env python
"""
Name :          test_iostream.py
Created :       Jul 27, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   tests iostream class.
________________________________________________________________________________
"""
# builtin
from __future__ import absolute_import, division, print_function
# package
# external
import six
# internal
from taskmage2.parser import iostream


# =======
# Helpers
# =======


def get_vimbuffer(contents):
    """

    Args:
        contents (list):
            A list of lines within the vim buffer.
            No newline/carriage-return characters please.

            .. code-block:: python

                [
                    'line 1',
                    'line 2',
                    ...
                ]

    """
    buf = iostream.PureVimBuffer()
    buf._buf = contents
    return buf


# =====
# Tests
# =====


class Test_PureVimBuffer(object):
    class Test_peek:
        def test_peek_overflow(self):
            buf = get_vimbuffer(['a', 'b', 'c'])
            result = []
            for i in range(7):
                result.append(buf.peek(i))
            assert result == ['a', '\n', 'b', '\n', 'c', '\n', None]

        def test_peek_with_empty_line(self):
            buf = get_vimbuffer(['', 'a', 'b', 'c'])
            result = []
            for i in range(8):
                result.append(buf.peek(i))
            assert result == ['\n', 'a', '\n', 'b', '\n', 'c', '\n', None]

        def test_peek_with_empty_lines(self):
            buf = get_vimbuffer(['', '', '', 'a', 'b', 'c'])
            result = []
            for i in range(10):
                result.append(buf.peek(i))
            assert result == ['\n', '\n', '\n', 'a', '\n', 'b', '\n', 'c', '\n', None]

        def test_next_overflow(self):
            buf = get_vimbuffer(['a', 'b', 'c'])
            result = []
            for i in range(7):
                result.append(buf.next())
            assert result == ['a', '\n', 'b', '\n', 'c', '\n', None]

        def test_peek_does_not_change_current_line_column(self):
            buf = get_vimbuffer(['abc', 'def'])
            buf.peek(4)
            assert buf.col == -1
            assert buf.line == -1

        def test_peek_variable_line_lengths(self):
            buf = get_vimbuffer(['abc', 'd', 'efghij'])
            result = []
            for i in range(14):
                result.append(buf.peek(i))
            assert result == ['a', 'b', 'c', '\n', 'd', '\n', 'e', 'f', 'g', 'h', 'i', 'j', '\n', None]

        def test_peek_from_empty_file_returns_none(self):
            buf = get_vimbuffer([])
            assert buf.peek() is None

    class Test_peek_line:
        def test_peek_line_from_linestart(self):
            buf = get_vimbuffer(['abc', 'defg'])
            assert buf.peek_line() == 'abc'

        def test_peek_line_from_midline(self):
            buf = get_vimbuffer(['abc', 'defg'])
            buf.col = 1
            assert buf.peek_line() == 'bc'

        def test_peek_line_at_eof(self):
            buf = get_vimbuffer(['abc', 'defg'])
            buf.line = 1
            buf.col = 8  # 'abc\ndefg\n'
            assert buf.peek_line() is None

        def test_peek_offset(self):
            buf = get_vimbuffer(['abc', 'defg'])
            assert buf.peek_line(1) == 'bc'

    class Test_offset:
        def test_offset_changes_pos(self):
            buf = get_vimbuffer(['abc'])
            buf.offset(1)
            ch = buf.peek()
            assert ch == 'b'

    class Test_eof:
        def test_eof_returns_false_before_end_of_file(self):
            buf = get_vimbuffer(['a'])
            assert buf.eof() is False

        def test_eof_returns_true_at_end_of_file(self):
            buf = get_vimbuffer(['a'])
            buf.offset(2)  # once for 'a', once for '\n'
            assert buf.eof() is True

        def test_eof_returns_true_in_empty_file(self):
            buf = get_vimbuffer([])
            assert buf.eof() is True

    class Test_read:
        def test_read(self):
            buf = get_vimbuffer(['abc', 'defg'])
            assert buf.read() == 'abc\ndefg\n'


class Test_FileDescriptor(object):
    def test_peek_overflow(self):
        buf = self.filedescriptor('a\nb\nc\n')
        result = []
        for i in range(7):
            result.append(buf.peek(i))
        assert result == ['a', '\n', 'b', '\n', 'c', '\n', None]

    def test_next_overflow(self):
        buf = self.filedescriptor('a\nb\nc\n')
        result = []
        for i in range(7):
            result.append(buf.next())
        assert result == ['a', '\n', 'b', '\n', 'c', '\n', None]

    def test_peek_variable_line_lengths(self):
        buf = self.filedescriptor('abc\nd\nefghij\n')
        result = []
        for i in range(14):
            result.append(buf.peek(i))
        assert result == ['a', 'b', 'c', '\n', 'd', '\n', 'e', 'f', 'g', 'h', 'i', 'j', '\n', None]

    def test_peek_line_from_linestart(self):
        buf = self.filedescriptor('abc\ndefg')
        assert buf.peek_line() == 'abc'

    def test_peek_line_from_midline(self):
        buf = self.filedescriptor('abc\ndefg')
        buf.offset(1)
        assert buf.peek_line() == 'bc'

    def test_peek_line_at_eof(self):
        buf = self.filedescriptor('abc\ndefg')
        buf.offset(8)  # 'abc\ndefg\n'
        assert buf.peek_line() is None

    def test_peek_offset(self):
        buf = self.filedescriptor('abc\ndefg')
        assert buf.peek_line(1) == 'bc'

    def test_read(self):
        buf = self.filedescriptor('abc\ndefg\n')
        assert buf.read() == 'abc\ndefg\n'


    def filedescriptor(self, contents):
        """

        Args:
            contents (str):
                A string representing a file in it's entirety.

                .. code-block:: python

                    'line_1\nline_2\n'
        """
        fd = six.moves.StringIO(contents)
        return iostream.FileDescriptor(fd)
