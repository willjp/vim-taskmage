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

    Returns:

        .. code-block:: python

            '/path/to/project' ## (directory containing .ptaskmgr directory)
            False              ## if no project is found

    """

    cwd = os.path.abspath( cwd )
    if cwd[-1] == '/':
        cwd = cwd[:-1]

    if os.path.isfile( cwd ):
        (cwd,filename) = os.path.split( cwd )

    cwd      = cwd.replace('\\','/')
    dirpaths = cwd.split('/')

    while dirpaths:
        testdir = '/'.join(dirpaths) +'/.ptaskmgr'
        if os.path.isdir( testdir ):
            return '/'.join(dirpaths)
        dirpaths = dirpaths[:-1]

    return False

def create_projectroot( dirpath ):
    """
    Creates a project root directory.

    This directory stores completed tasks, and any other info.


    Args:
        dirpath (str): ``(ex: '/home/project/root', '/home/project/root/.ptaskmgr' )``
            The path to your projectroot.

    """

    dirpath = dirpath.replace('\\','/')

    # if dirpath includes the .ptaskmgr dir, remove
    lastdir = dirpath.split('/')[-1]
    if lastdir == '.ptaskmgr':
        dirpath = '/'.join( dirpath.split('/')[:-1] )

    if not os.path.isdir( dirpath + '/.ptaskmgr' ):
        os.makedirs( dirpath + '/.ptaskmgr' )






if __name__ == '__main__':
    pass

