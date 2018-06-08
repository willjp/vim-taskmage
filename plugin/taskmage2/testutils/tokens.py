import copy
from taskmage2.testutils import core


# ============
# Lexer Tokens
# ============


def task(changes=None):
    """
    Args:
        changes (dict):
            A dictionary with nothing but the changes
            to _defaulttask.
    """
    taskcopy = copy.deepcopy(core.defaulttask)

    if changes:
        if 'data' in changes:
            taskcopy['data'].update(changes.pop('data'))
        taskcopy.update(changes)

    return taskcopy


def section(changes=None):
    headercopy = copy.deepcopy(core.defaultsection)

    if changes:
        headercopy.update(changes)

    return headercopy


def file(changes=None):
    filecopy = copy.deepcopy(core.defaultfile)

    if changes:
        filecopy.update(changes)

    return filecopy
