from taskmage2.parser import lexers, iostream, renderers, parsers
import vim


def handle_open_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.TaskList)
    vim.command('set ft=taskmage2')
    vim.current.buffer[:] = render


def handle_presave_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.TaskList(fd)
    parser = parsers.Parser(lexer)
    render = parser.render(renderers.Mtask)
    print(render)


def handle_postsave_mtask():
    pass
