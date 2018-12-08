import mock
import pytest

from taskmage2 import projects


ns = projects.__name__


class Test_Project(object):
    def test_load_projectroot(self):
        project = self.load('/src/project')
        assert project.root == '/src/project'

    def test_load_projectfile(self):
        project = self.load('/src/project/subdir/file.mtask')
        assert project.root == '/src/project'

    def test_load_taskmagedir(self):
        project = self.load('/src/project/.taskmage')
        assert project.root == '/src/project'

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

    def test_archive_all_completed(self):
        assert False

    def test_archive_completed_in_file(self):
        assert False

    def test_is_archived_path(self):
        assert False

    def test_is_not_archived_path(self):
        assert False

    def test_is_active_path(self):
        assert False

    def test_is_not_active_path(self):
        assert False

    def test_get_archived_path(self):
        assert False

    def test_get_active_path(self):
        assert False

    def load(self, path):
        return

    def create(self, root):
        with mock.patch('{}.os'.format(ns)) as mock_os:
            project = None
            return (mock_os, project)
