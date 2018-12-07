#!/usr/bin/env python
import os

import vim

from taskmage2.parser import lexers, iostream, parsers
from taskmage2.ast import renderers


def handle_open_mtask():
    """ converts buffer from Mtask(JSON) to TaskList(rst)
    """
    fd = iostream.VimBuffer(vim.current.buffer)
    ast = parsers.parse(fd, 'mtask')
    render = ast.render(renderers.TaskList)

    vim.command('syntax off')
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

    # merge overtop of savedfile if exists
    if not os.path.isfile(vim.current.buffer.name):
        buffer_ast.touch()
        render = buffer_ast.render(renderers.Mtask)
    else:
        with open(vim.current.buffer.name, 'r') as fd:
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
    fd = iostream.VimBuffer(vim.current.buffer)
    ast = parsers.parse(fd, 'tasklist')
    render = ast.render(renderers.TaskList)

    vim.current.buffer[:] = render
    vim.command('syntax on')
    return render
