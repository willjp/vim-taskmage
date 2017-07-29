#!/usr/bin/env python
"""
Name :          ptaskmgr.py
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
from ptaskmgr.parser  import TaskData
from ptaskmgr.project import get_projectroot, create_projectroot
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
    Replaces a *.ptask file (JSON) opened in vim
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
    vim.command('set ft=ptaskmgr')

def rst_to_json():
    """
    Converts a ReStructuredText formatted *.ptask file in a vim-buffer
    back to JSON (within the vim-buffer).

    This runs whenever vim saves a *.ptask buffer. The file is temporarily
    converted back to JSON before save, then the saved-file is re-read
    and converted back to ReStructuredText so the user can continue
    editing tasks within vim.

    Side Effect:

        Current buffer (ptask in ReStructuredText mode)
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
            datafmt  = TaskData.datafmt.rst
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
    Archives provided taskIds (from opened *.ptask file in ReStructuredText format)
    if their status is *complete*.


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
    projectroot = get_projectroot( filepath )
    if not projectroot:
        raise RuntimeError( 'No project was found in parent '
                            'hierarchy (.ptaskmgr directory)' )
    root2task_path    = filepath[ len(projectroot) : ]
    archivedtask_path = projectroot +'/.ptaskmgr'+ root2task_path


    # convert current vim buffer(rst) to json,
    # and obtain contents of archived taskfile
    conts = vim.current.buffer[:]
    vimbuf_taskdata   = TaskData( '\n'.join(conts), fmt_rst )
    archived_taskdata = TaskData( _read_jsonfile(archivedtask_path), fmt_json )

    # move tasks from vimbuf_taskdata to archived_taskdata
    removed_tasks = vimbuf_taskdata.remove_completed()
    print( removed_tasks )
    for taskinfo in removed_tasks:
        archived_taskdata.add_taskinfo( taskinfo )


    # write changes to vimbuffer/archived taskfiles
    with open( filepath, 'w' ) as fd:
        fd.write( vimbuf_taskdata.render_datafmt(fmt_json) )

    with open( archivedtask_path, 'w' ) as fd:
        fd.write( archived_taskdata.render_datafmt(fmt_json) )

    # reopen
    vim.command('edit "%s"' % filepath)



# Fine Grain Controls
# ===================

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



if __name__ == '__main__':
    pass
