
uuid = 'F04A9556B4114BCFB7B072D727E430A6'

# =====================================
# Dicts representing fake Lexer Tokens.
# (use functions below instead)
# =====================================
defaulttask = {
    # an empty, but syntactically correct task
    '_id': uuid,
    'type': 'task',
    'name': 'taskA',
    'indent': 0,
    'parent': None,
    'data': {'status': 'todo', 'created': None, 'finished': False, 'modified': None},
}

defaultsection = {
    # an empty, but syntactically correct section
    '_id': uuid,
    'type': 'section',
    'name': 'home',
    'indent': 0,
    'parent': None,
    'data': {},
}

defaultfile = {
    # an empty, but syntactically correct section
    '_id': uuid,
    'type': 'file',
    'name': 'path/home.mtask',
    'indent': 0,
    'parent': None,
    'data': {},
}
