#!/usr/bin/env python
"""
Name :          ptaskmgr.parser
Created :       Jun 11, 2017
Author :        Will Pittman
Contact :       willjpittman@gmail.com
________________________________________________________________________________
Description :   parses a *.ptaskdata file (json) into a file to be edited
                by vim (and then back to json afterwards).
________________________________________________________________________________
"""
#builtin
from   __future__    import unicode_literals
from   __future__    import absolute_import
from   __future__    import division
from   __future__    import print_function
from   collections   import OrderedDict
import sys
import os
import json
if sys.version_info[0] <= 2:
    from UserString  import UserString
    from UserDict    import IterableUserDict
else:
    from collections import UserString
    from collections import UserDict
#package
#external
#internal


class PtaskFile( UserString ):
    """
    Converts a :py:obj:`PtaskDataFile` JSON object into
    a file designed to be edited in vim.
    """
    def __init__(self, filepath=None):
        UserString.__init__(self,'')

        self.data  = ''
        self._dict = {}

        if filepath:
            self.data = self.from_ptaskdata( filepath )

    def from_ptaskdata(self, filepath):
        """
        Reads a *.ptaskdata file (JSON), and parses
        it into a format that will be used within vim
        to edit tasks.

        Args:
            filepath (str):
                the path to a (valid) *.ptaskdata file, that
                you want represented as a *.ptask file.

        Returns:

            .. code-block:: python

                *{*901A94884FE94EA18DE1879623986DF5*} task
                    *{*11F9AAEF279A45C19E9B38B56A0F4076*} subtask
                    *{*334a1033493f44178e098b32bbf82e29*} subtask


                section
                =======

                *{*308BD44370D543C8AFD5FF81F6383B1B*} task
                *{*2F23AD7FEF854B6F921689F310192A1D*} task2
                    *{*9A70C15B39B149FFBBC69C6B5ACC7801*} subtask
        """
        rawdata    = json.load( open(filepath,'r') )
        self.data  = ''


        hierarchy = {
            'toplevel_tasks': [],
            'sections':       OrderedDict(),
            'tasks':          OrderedDict(),
        }

        # create a dict of parents and their children
        # {
        #    'toplevel_tasks': [ taskId, taskid, ... ],
        #    'sections':       { section : [ taskId, taskId, ... ] },
        #    'tasks':          { taskId  : [ taskId, taskId, ... ] },
        # }
        #
        # saved as OrderedDict() so that item-order is preserved.
        for task in rawdata:
            if 'section' in task:
                if task['section']:
                    if task['section'] not in hierarchy['sections']:
                        hierarchy['sections'][ task['section'] ] = [ task['_id'] ]
                    else:
                        hierarchy['sections'][ task['section'] ].append( task['_id'] )

            elif 'parenttask' in task:
                if task['parenttask']:
                    if task['parenttask'] not in hierarchy['tasks']:
                        hierarchy['tasks'][ task['parenttask'] ] = [ task['_id'] ]
                    else:
                        hierarchy['tasks'][ task['parenttask'] ].append( task['_id'] )

            else:
                hierarchy['toplevel_tasks'].append( task['_id'] )


        # recurse through toplevel tasks, then sections,
        # building `ptask_str` progressively
        # ==============================================

        ptask_str = '\n\n'

        for taskId in hierarchy['toplevel_tasks']:
            ptask_str = self._get_ptaskdata_tasks(
                taskId    = taskId,
                ptask_str = ptask_str,
                jsondata  = rawdata,
                hierarchy = hierarchy,
            )
        for section in hierarchy['sections']:
            ptask_str += '\n\n'
            ptask_str += section +'\n'
            ptask_str += '=' * len(section) +'\n\n'

            for taskId in hierarchy['sections'][section]:
                ptask_str = self._get_ptaskdata_tasks(
                    taskId    = taskId,
                    ptask_str = ptask_str,
                    jsondata  = rawdata,
                    hierarchy = hierarchy,
                )


        return ptask_str

    def _get_ptaskdata_tasks(self, taskId, ptask_str, jsondata, hierarchy, depth=0 ):
        """

        Args:
            taskId (str):
                the uuid assigned to a particular task

            ptask_str (str):
                the string destined to be the *.ptask file so far.
                (return value)

            jsondata (list(dict)):
                the raw parsed *.ptaskdata file (json)

            hierarchy (dict):
                A dict of taskIds (parent), and their children.
                Used to arrange tasks in their proper hierarchy.

                .. code-block:: python

                    {
                        'tasks':          [ 'eb75388ab53d441093a6165cb28cac4d', 'b815e7ff99c8492a91bd3543ac5cded2', ... ],
                        'toplevel_tasks': [ 'eb75388ab53d441093a6165cb28cac4d', 'b815e7ff99c8492a91bd3543ac5cded2', ... ],
                        'sections':       [ 'eb75388ab53d441093a6165cb28cac4d', 'b815e7ff99c8492a91bd3543ac5cded2', ... ],
                    }

            depth (int, optional):
                the recursion depth of the current task.
                (automatically incremented by 1 during every recurse)

        Returns:

            A string destined to be a ptask file
            (ready for editing in vim)

            .. code-block:: python

                *{*901A94884FE94EA18DE1879623986DF5*} task
                    *{*11F9AAEF279A45C19E9B38B56A0F4076*} subtask
                    *{*334a1033493f44178e098b32bbf82e29*} subtask


                section
                =======

                *{*308BD44370D543C8AFD5FF81F6383B1B*} task
                *{*2F23AD7FEF854B6F921689F310192A1D*} task2
                    *{*9A70C15B39B149FFBBC69C6B5ACC7801*} subtask
        """

        task = self._task_from_taskId( taskId, jsondata )

        if not task:
            return

        if task['status'] == 'todo':
            status = '*'
        elif task['status'] == 'done':
            status = 'x'
        elif task['status'] == 'wip':
            status = 'o'
        elif task['status'] == 'skip':
            status = '-'

        # current task
        ptask_str += ('    '*depth) + '%s{{*{_id}*}} {text}\n'.format(**task) % status

        # recurse for subtasks
        if task['_id'] in hierarchy['tasks']:
            for _taskId in hierarchy['tasks'][ task['_id'] ]:
                ptask_str = self._get_ptaskdata_tasks(
                    taskId    = _taskId,
                    ptask_str = ptask_str,
                    jsondata  = jsondata,
                    hierarchy = hierarchy,
                    depth     = depth+1,
                )

        return ptask_str

    def _task_from_taskId(self, taskId, jsondata):
        """
        Returns:

            .. code-block:: python

                # If a task matching taskId is found
                {
                    '_id': 'cb798ab368eb400fa4d0edd941c03536',
                    'section': 'misc',
                    'created': '2017-06-12T21:42:43.084966-04:00',
                    'finished': None,
                    'text':    'Make sure to do blah',
                }

                # If no task matches taskId
                False
        """
        # find task from taskId
        # =====================
        for task in jsondata:
            if task['_id'] == taskId:
                return task

        logger.error('Corrupted Data: Unable to find task with ID: %s' % taskId)
        return False

    def edit_task(self):
        """
        Edit a single task as a conf file
        """
        # will require it's own pair of data vs string
        # (unless we use something like a conf-file as intermediary)
        raise NotImplementedError('TODO')



class PtaskDataFile( IterableUserDict ):
    """
    Converts a :py:obj:`PtaskFile` string (vim buffer) into
    a JSON file.
    """
    def __init__(self, filepath=None, string=None):
        IterableUserDict.__init__(self)
        pass

    def save(self, filepath):
        pass



if __name__ == '__main__':
    import os
    projdir   = '/'.join( os.path.realpath(__file__).split('/')[:-2] )
    ptaskdata_file = '{projdir}/examples/work.ptaskdata'.format(**locals())
    ptask = PtaskFile( ptaskdata_file )

    print(ptask)


