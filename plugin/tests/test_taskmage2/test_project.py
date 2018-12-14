import os

import mock
import pytest

from taskmage2 import projects


ns = projects.__name__


class Test_Project(object):
    def test_find_projectroot(self):
        project_root = self.find('/src/project', root='/src/project')
        assert project_root == '/src/project'

    def test_find_projectfile(self):
        project_root = self.find('/src/project/subdir/file.mtask', root='/src/project')
        assert project_root == '/src/project'

    def test_find_taskmagedir(self):
        project_root = self.find('/src/project/.taskmage', root='/src/project')
        assert project_root == '/src/project'

    def test_create_sets_up_filesystem(self):
        (mock_os, project) = self.create('/src/project')
        mock_os.makedirs.called_with('/src/project/.taskmage')

    def test_create_sets_root_attribute(self):
        (mock_os, project) = self.create('/src/project')
        assert project.root == '/src/project'

    def test_create_ignores_existing(self):
        with mock.patch('{}.os'.format(ns)) as mock_os:
            mock_os.path.isdir = mock.Mock(return_value=True)
            projects.Project.create('/src/project')

    def test_load_sets_root(self):
        with mock.patch('{}.Project.find'.format(ns), return_value='/src/project'):
            project = projects.Project()
            project.load('/src/project')
        assert project.root == '/src/project'

#    def test_archive_all_completed(self):
#        assert False
#
#    def test_archive_completed_in_file(self):
#        assert False
#
#    def test_is_archived_path(self):
#        assert False
#
#    def test_is_not_archived_path(self):
#        assert False
#
#    def test_is_active_path(self):
#        assert False
#
#    def test_is_not_active_path(self):
#        assert False
#
#    def test_get_archived_path(self):
#        assert False
#
#    def test_get_active_path(self):
#        assert False

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

    def create(self, root):
        with mock.patch('{}.os'.format(ns)) as mock_os:
            project = projects.Project.create(root)
            return (mock_os, project)
