#!/usr/bin/env python
import setuptools
import os
import sys
_rootdir = os.path.dirname(os.path.abspath(__file__))
_plugindir = '{}/plugin'.format(_rootdir)
sys.path.insert(0, _plugindir)
import taskmage2

__version__ = taskmage2.__version__

setuptools.setup(
    name='taskmage',
    version=__version__,
    author='Will Pittman',
    license='BSD',
    install_requires=[],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
)
