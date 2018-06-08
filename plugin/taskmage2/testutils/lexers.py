#!/usr/bin/env python
import six
from taskmage2.parser import lexers, iostream


# ==========================
# Build Lexer around Fake FD
# ==========================

def _lexer(contents, cls):
    fd = six.StringIO()
    fd.write(contents)
    iofd = iostream.FileDescriptor(fd)

    lexer = cls(iofd)
    _lexertokens = []
    token = ''
    while token is not None:
        token = lexer.read_next()
        if token is not None:
            _lexertokens.append(token)

    return _lexertokens


def tasklist(contents):
    return _lexer(contents, lexers.TaskList)


def mtask(contents):
    fd = six.StringIO()
    fd.write(contents)
    fd.seek(0)

    lexer = lexers.Mtask(fd)
    _lexertokens = []
    token = ''
    while token is not None:
        token = lexer.read_next()
        if token is not None:
            _lexertokens.append(token)

    return _lexertokens
