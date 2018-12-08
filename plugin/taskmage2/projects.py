

class Project(object):
    def __init__(self, path):
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

    @property
    def root(self):
        return self._root

    @classmethod
    def create(cls, root):
        """ Create a new taksmage project in directory `rootdir` .

        Args:
            rootdir (str):
                Path to the root of your taskmage project.
        """
        pass

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
        pass

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
