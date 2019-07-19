#!/usr/bin/env python
import os
import functools

import vim

from taskmage2.parser import iostream, parsers
from taskmage2.asttree import renderers
from taskmage2.project import projects, taskfiles
from taskmage2.utils import timezone


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
    project = projects.Project.from_path(vimfile)
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
    project = projects.Project.from_path(vimfile)

    # open counterpart
    counterpart = project.get_counterpart(vimfile)
    vim.command("{} {}".format(open_command, counterpart))


def search_keyword(searchterm):
    """ Lists all tasks whose `name` contains the word `searchterm` in the search-buffer.

    Args:
        searchterm (str):
            if word is contained within task's name, it is added to the list.
    """
    # get project
    project = projects.Project.from_path(vim.current.buffer.name)

    # get taskfiles
    taskfiles_ = project.iter_taskfiles()

    # get tasks (and format as lines)
    taskfilters = [functools.partial(taskfiles.TaskFilter.search, searchterm)]
    lines = []
    for taskfile in taskfiles_:
        for task in taskfile.filter_tasks(taskfilters):
            line = _format_searchresult(str(taskfile), task)
            lines.append(line)

    # show/populate searchbuffer
    _set_searchbuffer_contents(lines)


def search_latest():
    """ Lists tasks sorted by modified-date in descending order in the search-buffer.
    """
    # get project
    project = projects.Project.from_path(vim.current.buffer.name)

    # get taskfiles
    taskfiles_ = project.iter_taskfiles()

    # get tasks (and format as lines)
    tasks_w_filepath = []  # [{...}, ..]
    for taskfile in taskfiles_:
        for task in taskfile.iter_tasks():
            if not task['data'].get('modified', None):
                continue
            task['filepath'] = taskfile
            tasks_w_filepath.append(task)

    # sort tasks by date-modified
    tasks_w_filepath.sort(key=lambda x: x['data']['modified'], reverse=True)
    lines = [_format_searchresult(t['filepath'], t) for t in tasks_w_filepath]

    # show/populate searchbuffer
    _set_searchbuffer_contents([])
    bufnr = vim.eval('taskmage#searchbuffer#bufnr()')
    vim.buffers[int(bufnr)][:] = lines


def _format_searchresult(filepath, node_dict):
    """ Formats a node for the search-buffer.

    Args:
        filepath (str):
            absolute filepath to the file containing the node_dict

        node_dict (dict):
            a node dictionary. See :py:mod:`taskmage2.asttree.nodedata`

    Returns:
        str:

            '||/path/to/file.mtask|988D1C7D019D469E8767821FCB50F301|(2019-01-01 1:00) do something'

    """
    taskname = node_dict['name'].split('\n')[0]

    if 'modified' in node_dict['data']:
        modified = timezone.parse_utc_iso8601(node_dict['data']['modified'])
        modified_local = modified.astimezone(timezone.LocalTimezone())
        description = '({}) {}'.format(
            modified_local.strftime('%Y-%m-%d %H:%M'), taskname,
        )
    else:
        description = taskname

    result = r'||{}|{}|{}'.format(str(filepath), node_dict['_id'], description)
    return result


def _set_searchbuffer_contents(lines):
    # populate taskmage-search buffer with results
    vim.command('call taskmage#searchbuffer#close()')
    vim.command('let contents = pyeval("{}")'.format(lines))
    vim.command('call taskmage#searchbuffer#set_contents(contents)')
