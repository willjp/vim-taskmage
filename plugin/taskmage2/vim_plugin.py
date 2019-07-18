#!/usr/bin/env python
import os
import functools

import vim

from taskmage2.parser import iostream, parsers
from taskmage2.asttree import renderers
from taskmage2.project import projects, taskfiles


_search_buffer = 'taskmage-search'


def handle_open_mtask():
    """ converts buffer from Mtask(JSON) to TaskList(rst)
    """
    # reading directly off disk is MUCH faster
    with open(vim.current.buffer.name, 'r') as fd_py:
        fd = iostream.FileDescriptor(fd_py)
        ast = parsers.parse(fd, 'mtask')
        render = ast.render(renderers.TaskList)

    vim.current.buffer[:] = render
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
        buffer_ast.finalize()
        render = buffer_ast.render(renderers.Mtask)
    else:
        with open(vim.current.buffer.name, 'r') as fd_py:
            fd = iostream.FileDescriptor(fd_py)
            saved_ast = parsers.parse(fd, 'mtask')
        saved_ast.update(buffer_ast)
        saved_ast.finalize()
        render = saved_ast.render(renderers.Mtask)

    # replace vim-buffer with updated Mtask render
    vim.current.buffer[:] = render
    return render


def handle_postsave_mtask():
    """ converts buffer back from Mtask(JSON) to TaskList(rst) after save.
    """
    render = handle_open_mtask()
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
    project.archive_completed(vimfile)

    # reload from disk
    with open(vimfile, 'r') as fd_py:
        fd = iostream.FileDescriptor(fd_py)
        ast = parsers.parse(fd, 'mtask')
        render = ast.render(renderers.TaskList)

    vim.current.buffer[:] = render
    return render


def create_project():
    """ Interactive Vim Prompt to create a new TaskMage project.
    ( in any location )
    """
    vim.command('call inputsave()')
    vim.command("let projectroot=input('Create New Ptask Project at: ', '.', 'file' )")
    vim.command('call inputrestore()')
    projectroot = vim.eval('projectroot')

    if not projectroot:
        print('No project defined. aborting')
        return

    project = projects.Project.create(projectroot)
    return project


def open_counterpart(open_command=None):
    """ Opens archived taskfile if in active, or opposite.

    Args:
        open_command (str): ``(ex: None, '', 'vs', 'e', 'split', ...)``
            The vim command to use to open the file.
            Defaults to 'edit'.
    """
    if not open_command:
        open_command = 'edit'

    # load project
    vimfile = os.path.abspath(vim.current.buffer.name)
    project = projects.Project()
    project.load(vimfile)

    counterpart = project.get_counterpart(vimfile)
    vim.command("{} {}".format(open_command, counterpart))


def search(searchterm):
    """ Searches 'name' field of all tasks (complete and incomplete),
    dumps results in taskmage's searchbuffer.

    Args:
        searchterm (str):
            if word is contained within task's name, it is added to the list.
    """
    # get project
    vimfile = os.path.abspath(vim.current.buffer.name)
    project = projects.Project()
    project.load(vimfile)

    # get taskfiles
    taskfiles_ = project.iter_taskfiles()

    # get tasks (and format as lines)
    taskfilters = [
        functools.partial(taskfiles.TaskFilter.search, searchterm),
    ]
    lines = []
    for taskfile in taskfiles_:
        for task in taskfile.filter_tasks(taskfilters):
            lines.append(r'||{}|{}|{}'.format(str(taskfile), task['_id'], task['name']))

    # populate taskmage-search buffer with results
    vim.command('let contents = pyeval("{}")'.format(lines))
    vim.command('call taskmage#searchbuffer#set_contents(contents)')


