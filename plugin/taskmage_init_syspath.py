#!/usr/bin/env python
"""
Name :          plugin/taskmage_init_syspath.py
Created :       Jun 25, 2017
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   adds `taskmage` package to sys.path
________________________________________________________________________________
"""
#builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
import sys
#package
#external
import vim
#internal


filedir = vim.eval('s:scriptroot')

if filedir not in sys.path:
    sys.path.append( filedir )

