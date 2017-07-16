#!/usr/bin/env python
"""
Name :          plugin/ptaskmgr/project.py
Created :       Jul 09, 2017
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   functions that operate on the project.
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
#external
#internal


def get_projectroot(cwd='.'):
    """
    Finds the project root

    Args:
        cwd (str, optional): ``(ex: '/home/todo/task/file.py' )``
            Optionally, you may provide a file or directory
            to start searching for the projectroot from.

            (otherwise, the current directory is used)
    """
    cwd = os.path.abspath( cwd )

    if os.path.isfile( cwd ):
        (cwd,filename) = os.path.split( cwd )

    cwd      = cwd.replace('\\','/')
    dirpaths = cwd.split('/')

    while dirpaths:
        if os.path.isdir( '/'.join(cwd) + '.ptaskmgr' ):
            return '/'.join(cwd) + '.ptaskmgr'
        dirpaths = dirpaths[:-1]

    raise RuntimeError(
        'Unable to find project-root'
    )







if __name__ == '__main__':
    pass

