import os
import json
import fnmatch
from taskmage2.utils import functional


class TaskFile(object):
    def __init__(self, filepath):
        super(TaskFile, self).__init__()
        filepath = os.path.abspath(filepath)
        self._filepath = filepath

    def __str__(self):
        return self._filepath

    @property
    def filepath(self):
        return self._filepath

    def filter_tasks(self, filters):
        """
        Returns:
            Iterable:
                iterable of task-dictionaries.
        """
        tasks = functional.multifilter(filters, self.iter_tasks())
        return tasks

    def read(self):
        with open(self.filepath, 'r') as fd:
            return fd.read()

    def iter_tasks(self):
        """ Iterator that yields task dictionaries contained within taskfile.

        Yields:
            dict:
                see :py:mod:`taskmage2.asttree.nodedata`
        """
        tasks = json.loads(self.read())
        for task in tasks:
            yield task


class TaskFilter(object):
    @staticmethod
    def fnmatch(search, task):
        return fnmatch.fnmatch(task.get('name', ''), search)

    @staticmethod
    def search(searchterm, task):
        return searchterm in task.get('name', '')
