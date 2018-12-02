from taskmage2.parser import lexers, iostream, renderers, parsers
import vim


_presave_cursor_pos = None


def handle_open_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)

    vim.command('set ft=taskmage2')
    vim.current.buffer[:] = render
    return render


def handle_presave_mtask():
    """ converts buffer to JSON before save.
    """
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.TaskList(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.Mtask, touch=True)

    # TODO: read saved-data, re-adding `created`, `finished`, etc to formats
    #       that do not encode them (like tasklist)

    vim.command('syntax off')
    vim.current.buffer[:] = render
    return render


def handle_postsave_mtask():
    """ reloads buffer from JSON after save.
    """
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)

    vim.current.buffer[:] = render
    vim.command('syntax on')
    return render
