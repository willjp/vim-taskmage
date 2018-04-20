
# instead of this, try using io.BufferedReader( fd )
# or io.open( fd )




class ReadStream( object ):
    def __init__(self, fd=None):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def next(self):
        pass

    def peek(self):
        pass

    def eof(self):
        pass

    def exception(self, msg):
        pass


class VimBufferStream( object ):
    def __init__(self, buf):
        """
        Args:
            buf (vim.api.buffer.Buffer):
                A vim buffer. For example: ``vim.current.buffer`` .
        """
        self._buf  = buf
        self._line = 0
        self._linechar = 0

    def next(self):
        """
        change position forwards, and retrieve the next character
        """
        # next char on line
        if self._linechar < len(self._buf[ self._line ]):
            self._linechar +=1
            return self._buf[ self._line ][ self._linechar ]
        # first char on next line
        elif self._line < len(self._buf):
            self._line     += 1
            self._linechar  = 0
            return self._buf[self._line][self._linechar]

    def peek(self):
        """
        look at next character without changing positions
        """
        # next char on line
        if self._linechar < len(self._buf[ self._line ]):
            linechar = (self._linechar +1)
            return self._buf[ self._line ][ linechar ]
        # first char on next line
        elif self._line < len(self._buf):
            line     = (self._line + 1)
            linechar = 0
            return self._buf[line][linechar]


