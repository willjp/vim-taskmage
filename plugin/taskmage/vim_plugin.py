#!/usr/bin/env python
"""
Name :          taskmage/vim_plugin.py
Created :       Jun 25, 2017
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   The vim plugin portion of the code.
________________________________________________________________________________
"""
#builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
import datetime
import json
import sys
import os
#package
from taskmage.parser  import TaskData
from taskmage         import project
#external
import vim
import six
#internal


# Core Functions
# ==============

def _read_jsonfile( filepath ):
    json_taskdata = ''
    if os.path.isfile( filepath ):
        with open( filepath, 'r' ) as fd:
            json_taskdata = fd.read()

    if not json_taskdata.strip():
        json_taskdata = '[]'

    return json_taskdata

def jsonfile_to_rst():
    """
    Replaces a *.mtask file (JSON) opened in vim
    with a parsed, ReStructuredText-inspired task format.


    Example:

        *from:*

        .. code-block:: python

            [
                {
                    "_id":      "40429D679A504ED99F97D0D16067B2B3",
                    "section":  "other",
                    "created":  "2017-06-11T22:40:52.460849-04:00",
                    "finished": null,
                    "text":     "A task under a different category",
                    "status":   "skip"
                },
                {
                    "_id":      "E061DCB183EF4C418E97DEE63332C1A0",
                    "section":  "misc",
                    "created":  "2017-06-11T22:40:52.460849-04:00",
                    "finished": null,
                    "text":     "A test comment within a category",
                    "status":   "todo"
                },
            ]

        *to:*

        .. code-block:: ReStructuredText

            -{*40429D679A504ED99F97D0D16067B2B3*} A task under a different category
            *{*E061DCB183EF4C418E97DEE63332C1A0*} A test comment within a category


    """
    filepath = vim.current.buffer.name

    taskdata     = TaskData( _read_jsonfile(filepath), TaskData.datafmt.json )
    rst_taskdata = taskdata.render_datafmt( TaskData.datafmt.rst )


    vim.current.buffer[:] = rst_taskdata.split('\n')
    vim.command('set ft=taskmage')

def rst_to_json():
    """
    Converts a ReStructuredText formatted *.mtask file in a vim-buffer
    back to JSON (within the vim-buffer).

    This runs whenever vim saves a *.mtask buffer. The file is temporarily
    converted back to JSON before save, then the saved-file is re-read
    and converted back to ReStructuredText so the user can continue
    editing tasks within vim.

    Side Effect:

        Current buffer (mtask in ReStructuredText mode)
        is parsed back into JSON within the current vim buffer.

    """

    # currently saved JSON data
    filepath = vim.current.buffer.name

    current_taskdata = TaskData(
        taskdata = _read_jsonfile( filepath ),
        datafmt  = TaskData.datafmt.json,
    )
    now = datetime.datetime.utcnow()


    # parse vim buffer's RST --> JSON
    try:
        conts = vim.current.buffer[:]

        new_taskdata = TaskData(
            taskdata = '\n'.join( conts ),
            datafmt  = TaskData.datafmt.rst,
            datapath = filepath,
        )

        vim.current.buffer[:] = (
            new_taskdata.render_datafmt(
                TaskData.datafmt.json
            ).split('\n')
        )



    # restore original saved TASKDATA on error
    except:
        json_taskdata = current_taskdata.render_datafmt(
            TaskData.datafmt.json
        )
        if not json_taskdata.strip():
            json_taskdata = '[]'

        vim.current.buffer[:] = json_taskdata.split('\n')
        six.reraise( *sys.exc_info() )


def archive_completed_tasks():
    """
    Archives all completed task-branches.
    (from opened *.mtask file in ReStructuredText format)
    if their status is *complete*.


    Example:

        .. code-block:: ReStructuredText

            ## a,b, and c will be archived
            ## (entire task-branch completed)
            x a
               x b
               x c


            ## nothing will be archived
            ## (task-branch is not entirely completed)
            x a
               x b
               * c


    Args:
        taskIds ('FFC02020BC984711838327B888EFAD1C', '51DAD4BC86C54C07B8B5829ECFAE4B5E'):

    Returns:
       A subset of the provided taskIds that were
        successfully archived.

        .. code-block:: python

            set(['FFC02020BC984711838327B888EFAD1C', ...])
    """

    filepath = vim.current.buffer.name
    fmt_rst  = TaskData.datafmt.rst
    fmt_json = TaskData.datafmt.json

    # get path to archived tasks
    projectroot = get_projectroot()
    if not projectroot: # handle user-cancelled
        return

    root2task_path    = filepath[ len(projectroot) : ]
    archivedtask_path = projectroot +'/.taskmage'+ root2task_path


    # convert current vim buffer(rst) to json,
    # and obtain contents of archived taskfile
    conts = vim.current.buffer[:]
    vimbuf_taskdata   = TaskData( '\n'.join(conts), fmt_rst, filepath )
    archived_taskdata = TaskData( _read_jsonfile(archivedtask_path), fmt_json )

    # move tasks from vimbuf_taskdata to archived_taskdata
    removed_tasks = vimbuf_taskdata.remove_completed()
    for taskinfo in removed_tasks:
        archived_taskdata.add_taskinfo( taskinfo )

    # create archive, if does not exist yet
    if not os.path.isdir( os.path.dirname(archivedtask_path) ):
        os.makedirs( os.path.dirname(archivedtask_path) )

    # write changes to vimbuffer/archived taskfiles
    with open( filepath, 'w' ) as fd:
        fd.write( vimbuf_taskdata.render_datafmt(fmt_json) )

    with open( archivedtask_path, 'w' ) as fd:
        fd.write( archived_taskdata.render_datafmt(fmt_json) )

    # reopen
    vim.command('edit "%s"' % filepath)

def open_counterpart( open_command='edit' ):
    """
    If a task archive is opened in the current vim buffer,
    creates/opens it's taskfile in the current buffer.

    If a taskfile is opened in the current vim buffer,
    creates/opens it's archive in the current buffer.

    Args:
        open_command (str, optional): ``(ex: 'edit', 'split', 'vsplit' )``
            Optionally, you may provide the command used to
            open the file.

    """

    taskfile_path = find_counterpart()

    if open_command not in (
        'e','edit',
        's','split',
        'vs','vsplit',
    ):
        raise RuntimeError(
            'invalid `open_command` value: %s' % open_command
        )
    vim.command("{open_command} {taskfile_path}".format(**locals()) )




# Fine Grain Controls
# ===================

def get_projectroot():
    """
    Obtains/Returns project.
    If no project is found, prompts the user to
    specify a project directory.

    Returns:

        The path to the existing project (creating if necessary)

        .. code-block:: python

            '/home/user/todos'  # the projectroot dir
            False               # if cancelled by user

    """

    filepath = vim.current.buffer.name

    # if projectroot exists, return
    projectroot = project.get_projectroot( filepath )
    if projectroot:
        return projectroot

    # if not exists, prompt user to create new projectroot
    try:
        vim.command('call inputsave()')
        vim.command("let projectroot=input( 'Create New Ptask Project at:', '.', 'file' )")
        vim.command('call inputrestore()')
        projectroot = vim.eval('projectroot')
    except( KeyboardInterrupt ):
        print('Operation Cancelled By User')
        return False

    if not projectroot:
        print( 'User Defined project is empty. Aborting.' )
        return False

    projectroot = os.path.abspath( projectroot )

    if projectroot not in filepath:
        raise RuntimeError(
            'User Defined project is not a parent directory of current file'
        )


    # create/return the new projectroot
    project.create_projectroot( projectroot )
    return projectroot

def create_project():
    """
    Interactive Vim Prompt to create a new PtaskMgr project
    ( in any location )
    """
    vim.command('call inputsave()')
    vim.command("let projectroot=input( 'Create New Ptask Project at:', '.', 'file' )")
    vim.command('call inputrestore()')
    projectroot = vim.eval('projectroot')

    if not projectroot:
        print('No project defined. aborting')
        return

    project.create_project( projectroot )



def archive_selected():
    """
    Archives any completed tasks within visual selection (if present),
    or if not present, a completed task touching the current cursor.
    """
    pass

def complete_selected():
    """
    Completes
    """

# Utility
# =======

def get_tasks_under_cursor():
    """
    Obtains task under cursor (if no visual selection)
    or all tasks touched by visual-selection.
    """

def find_counterpart():
    """
    If a task archive is opened in the current vim buffer, returns it's taskfile.
    If a taskfile is opened in the current vim buffer, returns it's archive.

    Return:

        The path to the active taskfile, or the archived taskfile.

        .. code-block:: python

            '/path/to/.taskmage/file.mtask'
    """

    filepath = vim.current.buffer.name

    # archived taskdata
    if '.taskmage' in filepath:
        projectroot  = filepath.split( '.taskmage' )[0]
        rel_taskpath = filepath[ len(projectroot) + len('/.taskmage') : ]
        taskpath     = projectroot + rel_taskpath

        return taskpath

    else:
        projectroot       = get_projectroot()
        if not projectroot:
            raise RuntimeError(
                'current file is not within a taskmage project'
            )

        rel_taskpath      = filepath[ len(projectroot)+1 : ]
        archived_taskpath = '{projectroot}/.taskmage/{rel_taskpath}'.format(**locals())

        return archived_taskpath





if __name__ == '__main__':
    pass
