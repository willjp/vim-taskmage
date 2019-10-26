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


# =============
# Test Commands
# =============

class VimTest(setuptools.Command):
    """ ``python setup.py vimtest`` installs vader/jellybeans vim plugins and executes tests.
    """
    description = 'run vimfile tests (using Vader.vim)'
    user_options = [
        ('interactive', 'i', 'instead of printing to stdout, runs vader interactively in vim')
    ]
    requirements = VimRequirements()

    def initialize_options(self):
        self.interactive = False

    def finalize_options(self):
        pass

    def run(self):
        sys.exit(self.run_static(self.interactive))

    @classmethod
    def run_static(cls, interactive=False):
        cls.requirements.install()
        if interactive:
            cmds = ['vim', '-Nu', 'tests/resources/vimrc', '+Vader', 'tests/viml/*']
        else:
            cmds = ['vim', '-Nu', 'tests/resources/vimrc', '-c', 'Vader! tests/viml/*']  # output to console
        returncode = subprocess.call(cmds, universal_newlines=True)
        return returncode


class TotalTest(setuptools.Command):
    description = 'run tests for both vim and python'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # run python tests
        cmds = [sys.executable, 'setup.py', 'test_python']
        py_returncode = subprocess.call(cmds, universal_newlines=True)

        # run vim tests
        vim_returncode = VimTest.run_static()

        # return fail if any of the above failed.
        if any([x != 0 for x in (py_returncode, vim_returncode)]):
            sys.exit(1)
        sys.exit(0)


# ======================
# Test-Coverage Commands
# ======================

class VimCoverage(setuptools.Command):
    """ ``python setup.py vimtest`` installs vader/jellybeans vim plugins and executes tests.

    Notes:
        Requires that you have installed covimerage:

    Example:

        .. code-block:: bash

            python setup.py vim-coverage                # print coverage to stdout
            python setup.py vim-coverage --action=run   # print coverage to stdout

    """
    description = 'print vimfile test-coverage (using covimerage)'
    user_options = []
    requirements = VimRequirements()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.exit(self.run_static())

    @classmethod
    def run_static(cls):
        cls.requirements.install()
        cls._check_path_for_covimerage()
        returncode = cls._run_coverage()
        return returncode

    @classmethod
    def _check_path_for_covimerage(cls):
        try:
            import covimerage
        except(ImportError):
            print('WARNING: covimerage is not installed, command may fail\n'
                  'run:  pip install covimerage')

    @classmethod
    def _run_coverage(cls):
        cmds = ['covimerage', 'run',
                '--source', 'autoload',
                '--source', 'plugin',
                'vim', '-Nu', 'tests/resources/vimrc', '-c', 'Vader! tests/viml/*']
        returncode = subprocess.call(cmds, universal_newlines=True)
        return returncode

    def _run_xml(self):
        cmds = ['covimerage', 'xml']
        subprocess.call(cmds, universal_newlines=True)


class PythonCoverage(setuptools.Command):
    """ ``python setup.py py-coverage`` prints python-core coverage.

    Notes:
        Requires that you have installed covimerage:

    Example:

        .. code-block:: bash

            python setup.py py-coverage                # print coverage to stdout

    """
    description = 'print python-file test-coverage (using pytest-cov)'
    user_options = []

    def __init__(self, *args, **kwargs):
        setuptools.Command.__init__(self, *args, **kwargs)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.exit(self.run_static())

    @staticmethod
    def run_static():
        cmds = [sys.executable, 'setup.py', 'test_python',
                '--addopts', '--cov=plugin/taskmage2']
        returncode = subprocess.call(cmds, universal_newlines=True)
        return returncode


class TotalCoverage(setuptools.Command):
    description = 'get combined coverage of both python AND vim files'
    user_options = [
        ('xml', None, 'in addition to measuring both source-coverage types, produces coverage.xml file'),
        ('html', None, 'in addition to measuring both source-coverage types, produces htmlcov directory'),
    ]

    def initialize_options(self):
        self.xml = False
        self.html = False

    def finalize_options(self):
        self.xml = '--xml' in sys.argv

    def run(self):
        VimCoverage.run_static()
        PythonCoverage.run_static()

        # combine both coverage files into one
        cmds = ['coverage', 'combine', '.coverage', '.coverage_covimerage']
        returncode = subprocess.call(cmds, universal_newlines=True)
        if returncode != 0:
            print('ERROR: covarage command failed: {}'.format(repr(cmds)))

        # (optionally) render xml file
        if self.xml:
            cmds = ['coverage', 'xml']
            sys.exit(subprocess.call(cmds, universal_newlines=True))

        if self.html:
            cmds = ['coverage', 'html']
            sys.exit(subprocess.call(cmds, universal_newlines=True))


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
        'mock',
        'pyfakefs',
    ],
    cmdclass={
        # test_python (configured in setup.cfg)
        'test_vim': VimTest,
        'test': TotalTest,

        'coverage_vim': VimCoverage,
        'coverage_python': PythonCoverage,
        'coverage': TotalCoverage,
    }
)
