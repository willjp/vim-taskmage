from taskmage2.parser import lexers, parsers, iostream, renderers
import vim


def handle_open_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)
    vim.command('set ft=taskmage')
    vim.current.buffer[:] = render


def handle_save_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.TaskList(fd)
    parser = parsers.Parser(lexer)
    parser.render(renderers.Mtask)


