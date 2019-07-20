import os
import json
import fnmatch
import shutil
from taskmage2.utils import functional
from taskmage2.asttree import renderers


class TaskFile(object):
    def __init__(self, filepath):
        super(TaskFile, self).__init__()
        filepath = os.path.abspath(filepath)
        self._filepath = filepath

    def __str__(self):
        return self._filepath

    def __eq__(self, other):
        return self.filepath == other.filepath

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

    def write(self, ast):
        """
        Args:
            ast (taskmage2.asttree.asttree.AbstractSyntaxTree):
                writes an AST to a taskfile
        """
        filecontents_list = ast.render(renderers.Mtask)
        filecontents = '\n'.join(filecontents_list)
        filedir = os.path.dirname(self.filepath)

        if not os.path.isdir(filedir):
            os.makedirs(filedir)

        with open(self.filepath, 'w') as fd:
            fd.write(filecontents)

    def copyfile(self, filepath):
        """ Copy this taskfile to another location (creating missing directories).
        """
        # create directory if not exists
        filedir = os.path.dirname(self.filepath)
        if not os.path.isdir(filedir):
            os.makedirs(filedir)

        # copy the file
        shutil.copyfile(self.filepath, filepath)

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
