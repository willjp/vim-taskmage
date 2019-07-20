import os

import mock
import pytest

from taskmage2.project import projects, taskfiles

_this_package_dir = os.path.dirname(os.path.abspath(__file__))
_tests_dir = os.path.abspath('{}/../../..'.format(_this_package_dir))

ns = projects.__name__


class Test_Project(object):
    class Test_find:
        def test_find_projectroot(self):
            project_root = self.find('/src/project', root='/src/project')
            assert project_root == '/src/project'

        def test_find_projectfile(self):
            project_root = self.find('/src/project/subdir/file.mtask', root='/src/project')
            assert project_root == '/src/project'

        def test_find_taskmagedir(self):
            project_root = self.find('/src/project/.taskmage', root='/src/project')
            assert project_root == '/src/project'

        def find(self, path, root):
            """

            Args:
                path (str): path whose project we are trying to obtain
                root (str): the root of the project.
            """
            def isdir(path):
                task_dir = '{}/.taskmage'.format(root)
                return path == task_dir

            with mock.patch('{}.os.path.isdir'.format(ns), side_effect=isdir):
                project_root = projects.Project.find(path)
                return project_root

    class Test_create:
        def test_create_sets_up_filesystem(self):
            (mock_os, project) = self.create('/src/project')
            mock_os.makedirs.called_with('/src/project/.taskmage')

        def test_create_ignores_existing(self):
            with mock.patch('{}.os'.format(ns)) as mock_os:
                mock_os.path.isdir = mock.Mock(return_value=True)
                projects.Project.create('/src/project')

        def create(self, root):
            with mock.patch('{}.os'.format(ns)) as mock_os:
                project = projects.Project.create(root)
                return (mock_os, project)

    class Test_load:
        def test_load_sets_root(self):
            with mock.patch('{}.Project.find'.format(ns), return_value='/src/project'):
                project = projects.Project(None)
                project.load('/src/project')
            assert project.root == '/src/project'

    class Test_is_project_path:
        def test_is_project_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_project_path = project.is_project_path('/src/project/subdir/file.mtask')
            assert is_project_path is True

        def test_is_not_project_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_project_path = project.is_project_path('/src/subdir/file.mtask')
            assert is_project_path is False

    class Test_is_archived_path:
        def test_is_archived_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_archived_path = project.is_archived_path('/src/project/.taskmage/subdir/file.mtask')
            assert is_archived_path is True

        def test_is_not_archived_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_archived_path = project.is_archived_path('/src/project/subdir/file.mtask')
            assert is_archived_path is False

    class Test_is_active_path:
        def test_is_active_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_active_path = project.is_active_path('/src/project/subdir/file.mtask')
            assert is_active_path is True

        def test_is_not_active_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            is_active_path = project.is_active_path('/src/project/.taskmage/subdir/file.mtask')
            assert is_active_path is False

    class Test_get_archived_path:
        def test_get_archived_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            archived_path = project.get_archived_path('/src/project/subdir/file.mtask')
            assert archived_path == '/src/project/.taskmage/subdir/file.mtask'

    class Test_get_active_path:
        def test_get_active_path(self):
            project = projects.Project(None)
            project._root = '/src/project'
            archived_path = project.get_active_path('/src/project/.taskmage/subdir/file.mtask')
            assert archived_path == '/src/project/subdir/file.mtask'

    class Test_iter_taskfiles:
        def test(self):
            sample_project_dir = '{}/resources/sample_project'.format(_tests_dir)
            project = projects.Project.from_path(sample_project_dir)
            result = list(project.iter_taskfiles())

            expects = [
                taskfiles.TaskFile('{}/work.mtask'.format(sample_project_dir)),
                taskfiles.TaskFile('{}/home.mtask'.format(sample_project_dir)),
                taskfiles.TaskFile('{}/.taskmage/home.mtask'.format(sample_project_dir)),
            ]

            assert result == expects

    class Test_filter_taskfiles:
        def test(self):
            sample_project_dir = '{}/resources/sample_project'.format(_tests_dir)
            project = projects.Project.from_path(sample_project_dir)

            def is_home_dot_mtask(taskfile):
                return taskfile.filepath.endswith('home.mtask')

            result = list(project.filter_taskfiles([is_home_dot_mtask]))
            expects = [
                taskfiles.TaskFile('{}/home.mtask'.format(sample_project_dir)),
                taskfiles.TaskFile('{}/.taskmage/home.mtask'.format(sample_project_dir)),
            ]
            assert result == expects

    class Test_archive_completed_tasks:
        def test_archive_completed_tasks(self):
            assert False


