#!/usr/bin/env python
import os

import vim

from taskmage2.parser import lexers, iostream, parsers
from taskmage2.ast import renderers


def handle_open_mtask():
    """ converts buffer from Mtask(JSON) to TaskList(rst)
    """
    # reading directly off disk is MUCH faster
    with open(vim.current.buffer.name, 'r') as fd_py:
        fd = iostream.FileDescriptor(fd_py)
        ast = parsers.parse(fd, 'mtask')
        render = ast.render(renderers.TaskList)

    vim.current.buffer[:] = render
    vim.command('set ft=taskmage2')
    return render


def handle_presave_mtask():
    """ converts buffer to Mtask(JSON) before writing to disk.
    Also updates modified time, finished time, etc.
    """
    # convert vim-buffer to Mtask
    fd = iostream.VimBuffer(vim.current.buffer)
    buffer_ast = parsers.parse(fd, 'tasklist')
    # NOTE: doubling of entire buffer is happening here...

    # merge overtop of savedfile if exists
    if not os.path.isfile(vim.current.buffer.name):
        buffer_ast.touch()
        render = buffer_ast.render(renderers.Mtask)
    else:
        with open(vim.current.buffer.name, 'r') as fd_py:
            fd = iostream.FileDescriptor(fd_py)
            saved_ast = parsers.parse(fd, 'mtask')
        saved_ast.update(buffer_ast)
        saved_ast.touch()
        render = saved_ast.render(renderers.Mtask)

    # replace vim-buffer with updated Mtask render
    vim.command('syntax off')
    vim.current.buffer[:] = render
    return render


def handle_postsave_mtask():
    """ converts buffer back from Mtask(JSON) to TaskList(rst) after save.
    """
    render = handle_open_mtask()
    vim.command('syntax on ')
    return render


def archive_completed_tasks():
    """ saves current buffer, then archives all entirely-complete task-branches
    within the tree.
    """
    # save file, so saved copy is up to date
    vimfile = os.path.abspath(vim.current.buffer.name)
    if not os.path.isfile(vimfile):
        raise RuntimeError('cannot archive completed tasks in unsaved file')
    vim.command('w')

    # archive completed tasks on disk
    project = projects.Project()
    project.load(vimfile)
    project.archive_completed_tasks(vimfile)

    # reload from disk
    vim.command('e "{}"'.format(vimfile))

