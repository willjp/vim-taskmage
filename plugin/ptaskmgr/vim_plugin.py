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
    filepath = vim.current.buffer.name

    # create new virtual-buffer: <filename>.ptask
    vim.current.buffer.name = '%s.ptask' % (
        '.'.join( os.path.basename( filepath ).split('.')[:-1] )
    )


    # using ptaskmgr.parser, render to .ptask file
    parsed = ptaskmgr.parser.PtaskFile( filepath )

    # write contents to <filename>.ptask
    vim.current.buffer.append( parsed )




