import os
from taskmage2.utils import filesystem


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
        path = filesystem.format_path(path)

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

    def archive_completed_tasks(self, filepath=None):
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
        # I think this belongs on the AST intead...
        pass

    def is_archived_path(self, filepath):
        pass

    def is_active_path(self, filepath):
        pass

    def get_archived_path(self, filepath):
        """ Returns filepath to corresponding archived mtask file's (from un-archived mtask file).
        """
        pass

    def get_active_path(self, filepath):
        """ Returns filepath to corresponding un-archived mtask file (from archived mtask file).
        """
        pass


