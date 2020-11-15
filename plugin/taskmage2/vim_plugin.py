#!/usr/bin/env python
import os
import functools

import vim

from taskmage2.parser import iostream, parsers
from taskmage2.asttree import renderers
from taskmage2.parser import fmtdata
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
    vim.command('call taskmage#searchbuffer#pop_and_run_postcmds()')
    vim.command('set filetype=taskmage')
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

    projectroot = projects.Project.create(projectroot)
    project = projects.Project(projectroot)
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


def search_latest(filter_paramstr=None):
    """ Lists tasks sorted by modified-date in descending order in the search-buffer.

    Args:
        filter_paramstr (str): ``(ex: '"active:1","status:todo","created:>2018-01-01"' )``
            Filters you'd like to apply to tasks
            (if not set, active: defaults to 1)
    """
    # get project
    project = projects.Project.from_path(vim.current.buffer.name)

    # parse filters
    filter_params = []
    if filter_paramstr:
        filter_paramstr = filter_paramstr[1:-1]  # strip quotes
        filter_params = filter_paramstr.split('","')

    # defaults
    if not filter(lambda x: x.split(':')[0] == 'active', filter_params):
        filter_params.append('active:1')

    # create filters
    # TODO: command patternize this
    file_filters = []
    task_filters = [lambda t: t.get('type', None) == 'task']
    for filterp in filter_params:
        (filtername, val) = filterp.split(':')
        if filtername == 'active':
            def filter_active(value, taskfile):
                return ('.taskmage/' not in taskfile.filepath) == value
            expects = bool(int(val))
            file_filters.append(functools.partial(filter_active, expects))
        elif filtername == 'finished':
            def filter_finished(value, taskdict):
                return bool(taskdict['data']['finished']) is value
            expects = bool(int(val))
            task_filters.append(functools.partial(filter_finished, expects))
        elif filtername == 'status':
            def filter_status(value, taskdict):
                return taskdict['data']['status'] == value
            task_filters.append(functools.partial(filter_status, val))
        elif filtername in ('modified', 'created'):
            def filter_date(key, value, taskdict):
                if value.startswith('<'):
                    operator = '__lt__'
                    value = value[1:]
                elif value.startswith('>'):
                    operator = '__gt__'
                    value = value[1:]
                else:
                    operator = '__eq__'
                val_dt = timezone.parse_local_isodate(value)
                task_dt = timezone.parse_utc_iso8601(taskdict['data'][key])
                return getattr(task_dt, operator)(val_dt)
            task_filters.append(functools.partial(filter_date, filtername, val))
        else:
            print('[taskmage] invalid filter provided: {}'.format(filtername))
            return

    # get tasks (and format as lines)
    tasks_w_filepath = []  # [{...}, ..]
    for taskfile in project.filter_taskfiles(file_filters):
        for task in taskfile.filter_tasks(task_filters):
            if not task['data'].get('modified', None):
                continue
            task['filepath'] = taskfile
            tasks_w_filepath.append(task)

    # sort tasks by date-modified
    tasks_w_filepath.sort(key=lambda x: x['data']['modified'], reverse=True)
    lines = [_format_searchresult(t['filepath'], t) for t in tasks_w_filepath]

    # show/populate searchbuffer
    _set_searchbuffer_contents(lines)


def _format_searchresult(filepath, node_dict):
    """ Formats a node for the search-buffer.

    Args:
        filepath (str):
            absolute filepath to the file containing the node_dict

        node_dict (dict):
            a node dictionary. See :py:mod:`taskmage2.asttree.nodedata`

    Returns:
        str:

            '||/path/to/file.mtask|988D1C7D019D469E8767821FCB50F301|2019-01-01 1:00| do something'

    """
    desc = node_dict['name'].split('\n')[0]
    if 'status' in node_dict['data']:
        status = node_dict['data']['status']
        status_ch = fmtdata.TaskList.statuschar(status)
        desc = '{} {}'.format(status_ch, desc)

    modified_str = ''
    if 'modified' in node_dict['data']:
        modified = timezone.parse_utc_iso8601(node_dict['data']['modified'])
        modified_local = modified.astimezone(timezone.LocalTimezone())
        modified_str = modified_local.strftime('%Y-%m-%d %H:%M')

    result = r'||{filepath}|{uuid}|({modified})| {desc}'.format(
        filepath=str(filepath),
        uuid=node_dict['_id'],
        modified=modified_str,
        desc=desc,
    )
    return result


def _set_searchbuffer_contents(lines):
    vim.command('call taskmage#searchbuffer#open()')
    vim.command('call taskmage#searchbuffer#clear()')
    bufnr = vim.eval('taskmage#searchbuffer#bufnr()')
    vim.buffers[int(bufnr)][:] = lines

