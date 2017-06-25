#!/usr/bin/env python
"""
Name :          plugin/ptaskmgr_init_syspath.py
Created :       Jun 25, 2017
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   adds `ptaskmgr` package to sys.path
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
#internal

filedir = '/'.join(__file__.replace('\\','/').split('/')[:-1])
if filedir not in sys.path:
    sys.path.append( filedir )

