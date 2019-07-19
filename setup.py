#!/usr/bin/env python
import setuptools
import os
import sys
import subprocess
_rootdir = os.path.dirname(os.path.abspath(__file__))
_plugindir = '{}/plugin'.format(_rootdir)
sys.path.insert(0, _plugindir)
import taskmage2


__version__ = taskmage2.__version__


class VimTest(setuptools.Command):
    """ ``python setup.py vimtest`` installs vader/jellybeans vim plugins and executes tests.
    """
    user_options = []
    tests_require = [
        'https://github.com/junegunn/vader.vim',
        'https://github.com/nanotech/jellybeans.vim',
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self._install_requirements()
        #cmds = ['vim', '-Nu', 'tests/resources/vimrc', '+Vader', 'tests/viml/*']    # interactive
        cmds = ['vim', '-Nu', 'tests/resources/vimrc', '-c', 'Vader! tests/viml/*']  # output to console
        subprocess.call(cmds, universal_newlines=True)

    def _install_requirements(self):
        self._create_testdeps_dir()
        for url in self.tests_require:
            self._clone_requirement(url)

    def _create_testdeps_dir(self):
        # create test_deps dir
        if not os.path.isdir('.test_deps'):
            os.makedirs('.test_deps')

    def _clone_requirement(self, url):
        # clone repo
        basename = os.path.basename(url)
        rootdir = '.test_deps/{}'.format(basename)
        gitdir = '.test_deps/{}/.git'.format(basename)
        if not os.path.exists(gitdir):
            cmds = ['git', 'clone', url, rootdir]
            subprocess.call(cmds, universal_newlines=True)


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
    cmdclass={
        'vimtest': VimTest,
    }
)
