import os

import vim

from taskmage2.parser import lexers, iostream, renderers, parsers


def handle_open_mtask():
    """ converts buffer from Mtask(JSON) to TaskList(rst)
    """
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)

    vim.command('set ft=taskmage2')
    vim.current.buffer[:] = render
    return render


def handle_presave_mtask():
    """ converts buffer to Mtask(JSON) before writing to disk.
    Also updates modified time, finished time, etc.
    """
    # convert vim-buffer to Mtask
    fd = iostream.VimBuffer(vim.current.buffer)
    buffer_lexer = lexers.TaskList(fd)
    buffer_parser = parsers.Parser(buffer_lexer)

    # merge overtop of savedfile if exists
    if not os.path.isfile(vim.current.buffer.name):
        render = buffer_parser.render(renderers.Mtask, touch=True)
    else:
        with open(vim.current.buffer.name, 'r') as fd:
            disk_lexer = lexers.Mtask(fd)
            disk_parser = parsers.Parser(disk_lexer)

        merged_parser = disk_parser.update(buffer_parser)
        render = merged_parser.render(renderers.Mtask, touch=True)

    # replace vim-buffer with updated Mtask render
    vim.command('syntax off')
    vim.current.buffer[:] = render
    return render


def handle_postsave_mtask():
    """ converts buffer back from Mtask(JSON) to TaskList(rst) after save.
    """
    # NOTE: this step is unecessary if we save the pre-saved, merged, vim-buffer
    raise NotImplementedError()
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)

    vim.current.buffer[:] = render
    vim.command('syntax on')
    return render
