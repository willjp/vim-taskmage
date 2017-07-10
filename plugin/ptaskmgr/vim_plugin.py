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
import ptaskmgr.parser
#external
import vim
import six
#internal



def read_ptaskfile():
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

    parsed = ptaskmgr.parser.PtaskFile( filepath )
    vim.current.buffer[:] = parsed.split('\n')
    vim.command('set ft=ptaskmgr')

def buffer_to_ptaskfile():
    """
    Converts a ReStructuredText formatted *.ptask file in a vim-buffer
    back to JSON (within the vim-buffer).

    This runs whenever vim saves a *.ptask buffer. The file is temporarily
    converted back to JSON before save, then the saved-file is re-read
    and converted back to ReStructuredText so the user can continue
    editing tasks within vim.
    """

    # saved JSON data
    taskdata     = ptaskmgr.parser.PtaskDataFile( vim.current.buffer.name )
    new_taskdata = []

    now = datetime.datetime.utcnow()

    try:
        # vim Rst contents parsed into taskinfo
        conts        = vim.current.buffer[:]
        buffer_info  = ptaskmgr.parser.PtaskFile().ptask_taskinfo( conts )


        for task in buffer_info:
            new_task = {
                'status': task.status,
                'text'  : task.text,
                '_id'   : task.uuid,
            }

            # finished
            if task.status in ('skip','done'):
                new_task['finished'] = True
            else:
                new_task['finished'] = False


            # created timestamp
            if task.isnew:
                new_task['created'] = now.isoformat()


            # parent info
            if task.parent_type == 'root':
                pass

            elif task.parent_type == 'task':
                new_task['parenttask'] = task.parent

            elif task.parent_type == 'section':
                new_task['section'] = task.parent


            new_taskdata.append( new_task )

    except:
        vim.current.buffer[:] = json.dumps( list(taskdata), indent=2 ).split('\n')
        six.reraise( *sys.exc_info() )


    vim.current.buffer[:] = json.dumps( list(new_taskdata), indent=2 ).split('\n')



if __name__ == '__main__':
    pass
