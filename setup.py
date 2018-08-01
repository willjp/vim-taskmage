#!/usr/bin/env python
"""
Name :          setup.py
Created :       Jul 31, 2018
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   installs dependencies for taskmage2
________________________________________________________________________________
"""
# builtin
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# package
# external
import setuptools
# internal
import taskmage2

__version__ = taskmage2.__version__

setuptools.setup(
    name='taskmage',
    version=__version__,
    author='Will Pittman',
    license='BSD',
    install_requires=[
        'dateutils',
        'six',
    ],
)
