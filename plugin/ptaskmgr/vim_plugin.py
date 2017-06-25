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
import sys
import os
#package
import ptaskmgr.parser
#external
import vim
#internal



def read_ptaskfile( ptaskdata_filepath ):
    """
    Replaces the entire contents (JSON)
    of the file with the user-friendly editable version.


    Example:

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

        to

        .. code-block:: ReStructuredText

            -{*40429D679A504ED99F97D0D16067B2B3*} A task under a different category
            *{*E061DCB183EF4C418E97DEE63332C1A0*} A test comment within a category


    """
    filepath = vim.current.buffer.name

    parsed = ptaskmgr.parser.PtaskFile( filepath )
    vim.current.buffer[:] = parsed.split('\n')
    vim.command('set ft=ptaskmgr')





