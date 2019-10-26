import os


def format_path(path):
    # format path
    path = path.replace('\\', '/')
    while len(path) > 1 and path.endswith('/'):
        path = path[:-1]
    return path


def walk_parents(path):
    path = format_path(path)
    yield path

    last_dir = path
    parent_dir = os.path.dirname(last_dir)
    while parent_dir and last_dir != parent_dir:
        yield parent_dir
        last_dir = parent_dir
        parent_dir = os.path.dirname(last_dir)


def make_directories(path):
    if os.path.isdir(path):
        return
    elif os.path.exists(path):
        raise OSError('Path Exists, but is not a directory: "{}"'.format(path))
    os.makedirs(path)
