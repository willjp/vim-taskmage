#!/usr/bin/env python
"""
Name :          mfw_osTest.py
Created :       February 28 2015
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   checks operating system running maya so adjustments can be made to paths and
                environment
________________________________________________________________________________
"""
# builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
import uuid
import copy
# package
from taskmage2.parser import lexers, iostream
# external
import six
import pytest
# internal


_uuid = 'F04A9556B4114BCFB7B072D727E430A6'
_defaulttask = {
    # an empty, but syntactically correct task
    '_id': _uuid,
    'type': 'task',
    'name': 'taskA',
    'indent': 0,
    'parent': None,
    'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
}
_defaultsection = {
    # an empty, but syntactically correct section
    '_id': _uuid,
    'type': 'section',
    'name': 'home',
    'indent': 0,
    'parent': None,
    'data': {},
}

# ========
# Fixtures
# ========


@pytest.fixture
def uid():
    return uuid.UUID(_uuid)

# =====
# Utils
# =====

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


def defaulttask(changes=None):
    """
    Args:
        changes (dict):
            A dictionary with nothing but the changes
            to _defaulttask.
    """
    taskcopy = copy.deepcopy(_defaulttask)

    if changes:
        if 'data' in changes:
            taskcopy['data'].update(changes.pop('data'))
        taskcopy.update(changes)

    return taskcopy


def defaultsection(changes=None):
    headercopy = copy.deepcopy(_defaultsection)

    if changes:
        headercopy.update(changes)

    return headercopy
