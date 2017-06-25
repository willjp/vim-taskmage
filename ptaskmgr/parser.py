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
from   collections   import OrderedDict, namedtuple
import uuid
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


_taskindent = namedtuple( 'task', ['indent','uuid'] )


#!TODO: extract task hierarchies!
#!TODO: to_ptaskdata:  save comments insead of just ignoring them
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
                        'uuid':   '2DC12F0A0884461CAB1A8582A88632C7',
                        'text':   'this is\n my todo',
                        'status': 'todo',
                        'isnew':  True/False,

                        ## and either of ##
                        'parent':      'AB9C073FD0074AAB97216F15407D3EF8',  # None, uuid or section-name
                        'parent_type': 'task',                              # root, task or section
                    },
                ]
        """

        tasks = [] # the output var

        task  = []
        task_indentation = 0   # number of spaces/tabs of the last task (still currently active task)
                               # used to identify multiline tasks


        # stores last occurrences of info
        last = {
            'line':   '',
            'uuid':    None,
            'status':  None,
            'section': None,

            'indents': [],   # in escalating order of indentation: 3, 6, 9, ...
                             # the last item in list indicates the last task's
                             # indentation.
                             #
                             # [
                             #  (3,e0bd92993c554991abe4572e3e4b918d),
                             #  (6,917affe2f19a49da914ec504866a01fe),
                             #  ...
                             # ]
        }


        for line in fd:

            if not line:
                last['line'] = ''
                continue

            uuid_regex      = '{\*[A-Z0-9]+\*}'
            exist_taskmatch = re.search( uuid_regex, line )
            new_taskmatch   = re.search( '^[ \t]*[*-xo][ \t]', line )



            # Section-Title
            # =============
            if last['line']:
                if re.match( '^(?P<char>[=\-`:.\'"~^_\*#])(?P=char)*[ \t]*$', line):

                    if len(line.rstrip()) >= len(last['line'].rstrip()):

                        if task:
                            task  = task[:-1]
                            tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval
                            task  = []

                        last['section'] = last['line'].strip()
                        last['line']    = line
                        continue

            # Comment
            # =======
            # if '#' was not used for a title underline,
            # and a line starts with '#', it is a comment and ignored.
            if line:
                if line[0] == '#':
                    last['line'] = line
                    continue


            # Multiline task-descriptions
            # (indentation >= task-definition indentation)
            # ============================================
            (task_continued, last, tasks, task) = self._parse_task_multiline( last, task_indentation, line, tasks, task )
            if task_continued:
                last['line'] = line
                continue



            # Existing task
            # =============
            if exist_taskmatch:
                tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval
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
                _uuid        = uuid_bracketed[2:-2]
                status       = self._status_from_statuschar( status_char )

                if not status:
                    raise RuntimeError(
                        'Invalid task. Missing or invalid status-char (+-x*): %s' % line
                    )
                task.append( linesplit[1].strip() )

                # remember details in case multiline
                task_indentation = len(linesplit[0])+1
                last['uuid']     = _uuid
                last['status']   = status


            # New task
            # ========
            elif new_taskmatch:
                tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval
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
                last['uuid']     = None
                last['status']   = status


            last['line'] = line



        # add final task
        if task:
            tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval

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


    def _parse_task_multiline(self, last, task_indentation, line, tasks, task ):
        """
        Checks if this line is a continuation of the previous
        task.

        Args:
            last (dict):
                .. code-block:: python

                    {
                        'line'    : ..,
                        'uuid'    : ..,
                        'status'  : ..,
                        'section' : ..,
                        'indents' : ..,
                    }

            task_indentation (int):
                The indentation of the last task.
                (we are checking if this line is a continuation
                of that task's description).

            line (str):
                the line we are reading

            tasks (dict):
                The output of :py:meth:`ptask_taskinfo`

            task (list):  ``(ex:  ['line A', 'line B', ...] )``
                Each item represents a line in
                a multiline task.


        Returns:

            .. code-block:: python

                (is_taskdefinition, tasks, task)
        """
        task_continued = False

        if task_indentation != None:

            # get whitespace
            whitespace  = re.match('^[ \t]*', line)
            indentation = len(whitespace.group())

            # if line is a task-definition
            # ============================
            if re.match('^[ \t]*[*+x\-]( |{\*)', line ):

                # TODO: Need to keep history of last-task indentation
                #       levels. so that when a task is LESS INDENTED
                #       than the last task, we know which task it is
                #       parented to...


                # new task
                #if indentation == task_indentation:
                #    tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                #    task  = []

                ## new task, but parented to another task
                #elif indentation > task_indentation:
                #    tasks = add_task2tasks( tasks, task, last_uuid, last_status, last_section )
                #    task  = []

                ## check indentation to get
                #else:
                tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval
                task  = []


            # if line is not task
            # ===================
            else:
                # if line is indented, (and not another task) add to
                # task-description
                if indentation >= task_indentation:
                    task.append( line.strip() )
                    last['line']   = line
                    task_continued = True

                # if line is completely empty, add newline to
                # task-description
                elif not line.strip():
                    task.append( line.strip() )
                    last['line']   = line
                    task_continued = True

                # if indentation is less than current indentation
                # then the last task is finished.
                #
                # ( might be comment, section-header, ... )
                else:
                    tasks = self._add_task2tasks( tasks, task, last, None ) # None is tempval
                    task  = []


        return (task_continued, last, tasks, task)

    def _add_task2tasks(self, tasks, task, last, parent_task ):
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


        # if new task, assign a UUID to it,
        # and mark it as new.
        isnew = True
        if last['uuid'] == None:
            last['uuid'] = uuid.uuid4().hex
            isnew = True

        # determine parent type
        # TODO

        if task:
            tasks.append({
                'uuid'       : last['uuid'],
                'text'       : '\n'.join(task),
                'status'     : last['status'],
                'parent'     : last['section'],
                'parent_type': 'section',
                'isnew'      : isnew,
            })
        return tasks




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




