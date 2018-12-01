from taskmage2.parser import lexers, parser, iostream, renderers
import vim


def handle_open_mtask():
    print('hihi')
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.Mtask(fd)
    parse = parser.Parser(lexer)
    rendered = parse.render(render.TaskList)
    vim.command('set ft=taskmage')
    vim.current.buffer[:] = rendered


def handle_save_mtask():
    fd = iostream.VimBuffer(vim.current.buffer)
    lexer = lexers.TaskList(fd)
    parse = parser.Parser(lexer)
    parse.render(render.Mtask)


