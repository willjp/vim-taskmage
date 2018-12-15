import os
import shutil
import tempfile

from taskmage2.utils import filesystem
from taskmage2.ast import ast, renderers
from taskmage2.parser import iostream, parsers


class Project(object):
    def __init__(self, root=None):
        """ Constructor.

        Args:
            path (str): ``(ex: '/src/project/subdir/file.mtask', '/src/project', '/src/project/.taskmage' )``
                Path to your projectroot, or a file/directory within
                your taskmage project root.

                .. code-block:: python

                    '/src/project'
                    '/src/project/subdir/file.mtask'
                    '/src/project/.taskmage'

        """
        self._root = None

        if root:
            self.load(root)

    @property
    def root(self):
        """ The root directory of a project. Contains ``.taskmage`` directory.

        Returns:

            .. code-block:: python

                '/src/project'

        """
        return self._root

    @classmethod
    def create(cls, root):
        """ Create a new taksmage project in directory `rootdir` .

        Args:
            rootdir (str):
                Path to the root of your taskmage project.

        Returns:
            taskmage.projects.Project: a project instance.
        """

        if os.path.basename(root) == '.taskmage':
            root = os.path.dirname(root)

        if os.path.exists(root):
            if not os.path.isdir(root):
                raise OSError(
                    'unable to create taskmage project, provided '
                    'path exists and is not a directory. "{}"'.format(root)
                )

        taskmage_dir = '{}/.taskmage'.format(root)
        if os.path.exists(taskmage_dir):
            if not os.path.isdir(taskmage_dir):
                raise OSError(
                    'unable to create taskmage project, provided '
                    'path exists and is not a directory. "{}"'.format(taskmage_dir)
                )
            return Project(root)

        os.makedirs(taskmage_dir)
        return Project(root)

    @staticmethod
    def find(path):
        path = filesystem.format_path(os.path.abspath(path))

        # /src/project/.taskmage
        if os.path.basename(path) == '.taskmage':
            return os.path.dirname(path)

        # /src/project
        # /src/project/sub-path
        for parent_dir in filesystem.walk_parents(path):
            if os.path.isdir('{}/.taskmage'.format(parent_dir)):
                return parent_dir

        raise RuntimeError('unable to find taskmage project')

    def load(self, path):
        """ Loads a taskmage project from a path.

        Args:
            path (str): ``(ex: '/src/project/subdir/file.mtask', '/src/project', '/src/project/.taskmage' )``
                Path to your projectroot, or a file/directory within
                your taskmage project root.

                .. code-block:: python

                    '/src/project'
                    '/src/project/subdir/file.mtask'
                    '/src/project/.taskmage'

        """
        projectroot = self.find(path)
        self._root = projectroot

    def archive_completed(self, filepath=None):
        """ Archives all completed task-branches.

        Example:

            .. code-block:: ReStructuredText

                ## a,b, and c will be archived
                ## (entire task-branch completed)
                x a
                   x b
                   x c


                ## nothing will be archived
                ## (task-branch is not entirely completed)
                x a
                   x b
                   * c

        Args:
            filepath (str, optional): ``(ex: '/src/project/file.mtask' )``
                Optionally, archive completed tasks in a single target file.
        """
        if filepath is not None:
            self._archive_completed(filepath)
        else:
            # for every mtask file in the entire project...
            raise NotImplementedError('todo - archive completed tasks from all mtask files')

    def is_project_path(self, filepath):
        """ Test if a file is within this project.
        """
        if filepath.startswith('{}/'.format(self.root)):
            return True
        return False

    def is_archived_path(self, filepath):
        """ Test if file is an archived mtask file.
        """
        if filepath.startswith('{}/.taskmage/'.format(self.root)):
            return True
        return False

    def is_active_path(self, filepath):
        """ Test if file is an active (non-archived) mtask file.
        """
        if self.is_project_path(filepath) and not self.is_archived_path(filepath):
            return True
        return False

    def get_archived_path(self, filepath):
        """ Returns filepath to corresponding archived mtask file's (from un-archived mtask file).
        """
        if not self.is_project_path(filepath):
            raise RuntimeError(
                ('filepath not within current taskmage project. \n'
                 'project "{}"\n'
                 'filepath "{}\n').format(self.root, filepath)
            )
        if self.is_archived_path(filepath):
            return filepath

        filepath = filesystem.format_path(filepath)
        relpath = filepath[len(self.root) + 1:]
        archived_path = '{}/.taskmage/{}'.format(self.root, relpath)
        return archived_path

    def get_active_path(self, filepath):
        """ Returns filepath to corresponding un-archived mtask file (from archived mtask file).
        """
        if not self.is_project_path(filepath):
            raise RuntimeError(
                ('filepath not within current taskmage project. \n'
                 'project "{}"\n'
                 'filepath "{}\n').format(self.root, filepath)
            )
        if not self.is_archived_path(filepath):
            return filepath

        filepath = filesystem.format_path(filepath)
        taskdir = '{}/.taskmage'.format(self.root)
        relpath = filepath[len(taskdir) + 1:]
        active_path = '{}/{}'.format(self.root, relpath)
        return active_path

    def _archive_completed(self, filepath):
        (active_ast, archive_ast) = self._archive_completed_as_ast(filepath)

        # render ASTs
        active_mtask_contents = active_ast.render(renderers.Mtask)
        archive_mtask_contents = archive_ast.render(renderers.Mtask)

        # create tempdir (prevent writing bad data)
        tempdir = tempfile.mkdtemp()
        active_tempfile = '{}/active.mtask'.format(tempdir)
        archive_tempfile = '{}/archive.mtask'.format(tempdir)
        try:
            # write contents to tempfiles
            with open(active_tempfile, 'w') as fd:
                fd.write('\n'.join(active_mtask_contents))
            with open(archive_tempfile, 'w') as fd:
                fd.write('\n'.join(archive_mtask_contents))

            # overwrite real files
            archive_path = self.get_archived_path(filepath)
            archive_dir = os.path.dirname(archive_path)
            if not os.path.isdir(archive_dir):
                os.makedirs(archive_dir)

            shutil.copyfile(archive_tempfile, archive_path)
            shutil.copyfile(active_tempfile, filepath)
        finally:
            # delete tempdir
            if os.path.isdir(tempdir):
                shutil.rmtree(tempdir)

    def _archive_completed_as_ast(self, filepath):
        """
        Returns:

            .. code-block:: python

                (
                    ast.AbstractSyntaxTree(),  # new active AST
                    ast.AbstractSyntaxTree(),  # new archive AST
                )
        """
        # get active AST
        active_ast = self._get_mtaskfile_ast(filepath)

        # get archive AST
        archive_path = self.get_archived_path(filepath)
        archive_ast = self._get_mtaskfile_ast(archive_path)

        # perform archive
        archive_ast = active_ast.archive_completed(archive_ast)
        return (active_ast, archive_ast)

    def _get_mtaskfile_ast(self, filepath):
        if not os.path.isfile(filepath):
            return ast.AbstractSyntaxTree()

        with open(filepath, 'r') as fd_src:
            fd = iostream.FileDescriptor(fd_src)
            AST = parsers.parse(fd, 'mtask')
        return AST
