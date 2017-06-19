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
import re
if sys.version_info[0] <= 2:
    from UserString  import UserString
    from UserDict    import IterableUserDict
else:
    from collections import UserString
    from collections import UserDict
#package
#external
#internal


#!TODO: to_ptaskdata:  save comments insead of just ignoring them
#!TODO: extract task hierarchies!
#!TODO: *.ptask to *.ptaskdata
class PtaskFile( UserString ):
    """
    Converts a :py:obj:`PtaskDataFile` JSON object into
    a file designed to be edited in vim.
    """
    def __init__(self, filepath=None):
        UserString.__init__(self,'')

        self.data  = ''
        self._dict = {}

        self._saved_data = OrderedDict()  # { UUID:{..task-contents..} }

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

        rawdata          = json.load( open(filepath,'r') )
        self.data        = ''
        self._saved_data = OrderedDict()

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
            self._saved_data[ task['_id'] ] = task
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


    def ptask_taskinfo(self, fd):
        """
        Reads a *.ptask file, and extracts structured information
        about the tasks it contains. This information can be used
        to update a *.ptaskdata file.


        Args:
            fd (a file-descriptor):
                A file-descriptor containing a *.ptask file

        Returns:

            A list of all tasks contained in the file.

            .. code-block:: python

                tasks = [
                    # existing tasks will have uuids
                    {
                        'uuid':   '2dc12f0a0884461cab1a8582a88632c7',
                        'text':   'this is\n my todo',
                        'status': 'todo',
                    },

                    # new tasks will *not* have a uuid
                    {
                        'uuid':    None,
                        'text':   'this is my other todo',
                        'status': 'done',
                    },

                ]
        """

        tasks = [] # the output var

        task  = []
        task_indentation = 0

        last_line    = ''
        last_uuid    = None
        last_status  = None
        last_section = None

        def add_task2tasks( tasks, task, uuid, status, section ):
            """
            adds current task to `tasks`
            """

            # strip all newlines after the task
            # (but keep newlines in the middle of task)
            trailing_blanklines = 0
            for i in reversed(range(len(task))):
                if not task[i]:   trailing_blanklines +=1
                else:             break

            if trailing_blanklines:
                task = task[ : -1 * trailing_blanklines ]

            if task:
                tasks.append({
                    'uuid'    : last_uuid,
                    'text'    : '\n'.join(task),
                    'status'  : last_status,
                    'section' : section,
                })
            return tasks


        for line in fd:

            if not line:
                last_line = ''
                continue

            uuid_regex      = '{\*[A-Z0-9]+\*}'
            exist_taskmatch = re.search( uuid_regex, line )
            new_taskmatch   = re.search( '^[ \t]*[*-xo][ \t]', line )



            # Section-Title
            # =============
            if last_line:
                if re.match( '^(?P<char>[=\-`:.\'"~^_\*#])(?P=char)*[ \t]*$', line):

                    if len(line.rstrip()) >= len(last_line.rstrip()):

                        if task:
                            task  = task[:-1]
                            tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                            task  = []

                        last_section = last_line.strip()
                        last_line    = line
                        continue

            # Comment
            # =======
            # if '#' was not used for a title underline,
            # and a line starts with '#', it is a comment and ignored.
            if line:
                if line[0] == '#':
                    last_line = line
                    continue


            # Multiline task-descriptions
            # (indentation >= task-definition indentation)
            # ============================================
            if task_indentation != None:

                # if not task
                if not re.match('^[ \t]*[*+x\-]( |{*)', line ):

                    # get whitespace
                    whitespace = re.match('^[ \t]*', line)
                    if whitespace:
                        indentation = len(whitespace.group())

                        # if line is indented, (and not another task) add to comment
                        if indentation >= task_indentation:
                            task.append( line.strip() )
                            last_line = line
                            continue

                        # if line is completely empty, add newline
                        elif not line.split():
                            task.append( line.strip() )
                            last_line = line
                            continue

                        # if indentation is different, then
                        # then the last task is finished.
                        else:
                            tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                            task  = []



            # Existing task
            # =============
            if exist_taskmatch:
                tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                task = []
                task_indentation = 0
                uuid_bracketed   = exist_taskmatch.group()
                linesplit        = line.split( uuid_bracketed )

                if len(linesplit) != 2:
                    raise RuntimeError(
                        'Incomplete or Invalid task: %s' % line
                    )
                elif not linesplit[0]:
                    raise RuntimeError(
                        'Incomplete or Invalid task: %s' % line
                    )

                status_char  = linesplit[0][-1]
                uuid         = uuid_bracketed[2:-2]
                status       = self._status_from_statuschar( status_char )

                if not status:
                    raise RuntimeError(
                        'Invalid task. Missing or invalid status-char (+-x*): %s' % line
                    )
                task.append( linesplit[1].strip() )

                # remember details in case multiline
                task_indentation = len(linesplit[0])+1
                last_uuid        = uuid
                last_status      = status


            # New task
            # ========
            elif new_taskmatch:
                tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                task  = []
                task_indentation = 0
                status_char = new_taskmatch.group()[-2]  # space then char
                status      = self._status_from_statuschar( status_char )
                if not status:
                    raise RuntimeError(
                        'Invalid task. Missing or invalid status-char (+-x*): %s' % line
                    )
                task.append(  line[ len(new_taskmatch.group()) : ].strip() )

                # remember details in case multiline
                task_indentation = len(line) - len(line.lstrip())
                last_uuid        = None
                last_status      = status


            last_line = line



        # add final task
        if task:
            tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )

        return tasks

    def _status_from_statuschar(self, status_char ):
        """

        """
        if status_char == 'o':
            return 'wip'

        elif status_char == 'x':
            return 'done'

        elif status_char == '*':
            return 'todo'

        elif status_char == '-':
            return 'skip'

        return False


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

    def test_ptaskdata_2_ptask( projdir ):
        ptaskdata_file = '{projdir}/examples/work.ptaskdata'.format(**locals())
        ptask = PtaskFile( ptaskdata_file )

        print(ptask)

    def test_ptask_taskinfo( projdir ):
        with open( '{projdir}/examples/work_valid.ptask'.format(**locals()), 'r' ) as fd:
            ptask = PtaskFile()
            taskinfo  = ptask.ptask_taskinfo( fd )

            print('----')
            for task in taskinfo:
                print( task )

    def runtests():
        #test_ptaskdata_2_ptask( projdir )
        test_ptask_taskinfo( projdir )

    runtests()




