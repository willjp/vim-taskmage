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


class VimRequirements(object):
    requirements = [
        'https://github.com/junegunn/vader.vim',
        'https://github.com/nanotech/jellybeans.vim',
    ]

    def install(self):
        """ Installs vim requirements defined in :py:attr:`requirements` .
        """
        self._create_testdeps_dir()
        for url in self.requirements:
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


class VimTest(setuptools.Command):
    """ ``python setup.py vimtest`` installs vader/jellybeans vim plugins and executes tests.
    """
    description = 'run vimfile tests (using Vader.vim)'
    user_options = []

    def __init__(self, *args, **kwargs):
        super(VimTest, self).__init__(*args, **kwargs)
        self.requirements = VimRequirements()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.requirements.install()
        #cmds = ['vim', '-Nu', 'tests/resources/vimrc', '+Vader', 'tests/viml/*']    # interactive
        cmds = ['vim', '-Nu', 'tests/resources/vimrc', '-c', 'Vader! tests/viml/*']  # output to console
        subprocess.call(cmds, universal_newlines=True)


class VimCoverage(setuptools.Command):
    """ ``python setup.py vimtest`` installs vader/jellybeans vim plugins and executes tests.

    Example:

        .. code-block:: bash

            python setup.py vimcoverage                # print coverage to stdout
            python setup.py vimcoverage --action=xml   # write vim-coverage.xml
            python setup.py vimcoverage --action=run   # print coverage to stdout

    """
    description = 'print vimfile test-coverage (using covimerage)'
    user_options = [
        ('xml', None, 'writes vim-coverage.xml instead of printng to stdout'),
    ]

    def __init__(self, *args, **kwargs):
        super(VimCoverage, self).__init__(*args, **kwargs)
        self.requirements = VimRequirements()

    def initialize_options(self):
        self.xml = False

    def finalize_options(self):
        pass

    def run(self):
        self.requirements.install()
        if self.xml:
            self._run_xml()
        else:
            self._run_coverage()

    def _run_coverage(self):
        cmds = ['covimerage', 'run',
                '--source', 'autoload',
                '--source', 'plugin',
                'vim', '-Nu', 'tests/resources/vimrc', '-c', 'Vader! tests/viml/*']
        subprocess.call(cmds, universal_newlines=True)

    def _run_xml(self):
        cmds = ['covimerage', 'xml']
        subprocess.call(cmds, universal_newlines=True)


# see python setup.py --help-commands for all commands
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
        'vimcoverage': VimCoverage,
    }
)
