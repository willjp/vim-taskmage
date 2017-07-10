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
from   enum          import Enum
import copy
import uuid
import sys
import os
import json
import re
if sys.version_info[0] <= 2:
    from UserString  import UserString
    from UserList    import UserList
else:
    from collections import UserString
    from collections import UserList
#package
#external
#internal


_taskinfo = namedtuple(
    # while parsing, detailed info
    # about a task.
    'taskinfo', [
        'uuid',
        'text',
        'section',
        'status',
        'parent',
        'parent_type',
        'isnew'
    ]
)
_taskdef = namedtuple(
    # while parsing, info about
    # a task-definition
    'taskdef', [
        'uuid',        # 8FE95847DF73449096393F90E4E61535
        'status',      # 'todo', 'done', ...
        'isnew',       # True/False
        'text',        # [ line, line, ... ]
        'indentation', # number of whitespace characters at start of line
        'section',     # section-header at the time the task was defined
    ]
)
_taskindent = namedtuple(
    # new or existing, a pairing of uuid/indentation
    # for each new level of indentation
    'taskindent', ['uuid','indentation'],
)

class _ParserHandled( Enum ):
    """
    First item in return-value from each PtaskFile
    parser method. Indicates that an item was handled
    by the method, and categorizes how it was handled.
    """

    NewItemDefinition   = 1 # a new item was defined, so the last task should end

    ContinuedDefinition = 2 # a continuation of the last item. do not continue to attempt
                            # to handle with other parser methods, but do not
                            # add the item to the list of tasks just yet.


#!TODO: Figure out how to determine project-root,
#!      so that tasks can be archived.
#!
#!      it might make most sense to use a directory
#!      just like git. In this way, we can keep track
#!      of completed tasks in addition to keeping track
#!      of the project-root.

#!TODO: This should be divided into functions,
#!        the classes don't make sense...

#!TODO: Save comments insead of just ignoring them

#!TODO: Archive tasks


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
            self.data = self.from_ptaskfile( filepath )


    def from_ptaskfile(self, filepath):
        """
        Reads a *.ptask file (JSON), and parses it into
        the ReStructuredText format.

        Args:
            filepath (str):
                the path to a (valid) *.ptask file, that
                you want represented as a ReStructuredText file.

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


    def ptask_taskinfo(self, fileconts):
        """
        Args:
            fileconts (collections.Iterable):
                A list, file-descriptor, or other iterable
                collection where each item represents a single
                line of text from the ReStructuredText
                formatted taskfile.

        Returns:

            .. code-block:: python

                [
                    _taskinfo(
                        uuid        = '3B958E62E79D4A08BF3F70D1601E7305',
                        text        = 'linea\nlineb\nlinec',
                        section     = 'Home Todos',
                        status      = 'todo',
                        parent      = 'root',
                        parent_type = None,
                        isnew       = True,
                    ),
                    _taskinfo(...),
                    _taskinfo(...),
                    ...
                ]

        """

        last_encountered  = {
            'line':    None,
            'section': None,
            'indents': [],  # [ _taskindent(), _taskindent(), ... ]
        }
        last_taskdef = None # _taskdef(): the last defined task
        tasks        = []   # [ _taskinfo(), _taskinfo(), ... ]

        for line in fileconts:

            if not line:
                line = ''

            count = 0
            for method in (
                self._handle_sectionheader,
                self._handle_comment,
                self._handle_continued_taskdef,
                self._handle_existing_taskdef,
                self._handle_new_taskdef,
            ):
                (   handled          ,
                    last_encountered ,
                    new_taskdef      ,
                ) = method( line, last_encountered, copy.deepcopy(last_taskdef) )


                # if the line defined a new `thing` (comment, header, task, ...)
                # this marks the end of the last `thing`. If a task
                # is being built, add it to `tasks`
                if handled:
                    if handled == _ParserHandled.NewItemDefinition:
                        if last_taskdef:
                            tasks = self._add_taskdef_to_tasks(
                                tasks, last_encountered, last_taskdef
                            )

                            # clear indentation history if new section
                            if tasks:
                                if tasks[-1].section != last_taskdef.section:
                                    last_encountered['indents'] = []

                            # set indents
                            last_encountered = self._set_last_encountered_indentation(
                                last_taskdef.uuid, last_taskdef.indentation, last_encountered
                            )
                            last_taskdef = None


                # prepare for next cycle
                last_taskdef = new_taskdef
                last_encountered['line'] = line

                # if the last method handled the line,
                # we do not need to run any more handlers
                if handled:
                    break

                count +=1

        if last_taskdef:
            tasks = self._add_taskdef_to_tasks(
                tasks, last_encountered, last_taskdef,
            )


        return tasks

    def _status_from_statuschar(self, status_char ):
        """
        Returns the text-status from the status-character
        used in a ReStructuredText format ptask file.
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

    def _handle_sectionheader(self, line, last_encountered, last_taskdef):
        """
        section-headers take 2x lines,

        Example:

            .. code-block:: ReStructuredText

                section-header
                ==============


         * the section-header text

         * a stream of repeated characters at least as long
           as the text


        """

        handled = False

        if not last_encountered['line']:
            return (handled, last_encountered, last_taskdef)


        if re.match( '^(?P<char>[=\-`:.\'"~^_\*#])(?P=char)*[ \t]*$', line):

            if len(line.rstrip()) >= len(last_encountered['line'].rstrip()):

                section = last_encountered['line'].strip()
                if section:

                    handled = _ParserHandled.NewItemDefinition
                    last_encountered['section'] = section
                    last_taskdef                = None

        return (handled, last_encountered, last_taskdef)

    def _handle_comment(self, line, last_encountered, last_taskdef):
        """
        Non-Inline Comments are entirely ignored (not saved to the ptaskfile).
        A comment is any line where the first character is a '#'

        (as long as it is not a part of a section-header).

        Example:

            .. code-block:: ReStructuredText

                # a comment (will not be saved)

                * do the laundry  # inline comments are preserved
                * do the dishes
        """
        handled = False

        # presently, comments are entirely ignored,
        # and not saved
        if line:
            if line[0] == '#':
                handled      = _ParserHandled.NewItemDefinition
                last_taskdef = None

        return (handled, last_encountered, last_taskdef)

    def _handle_continued_taskdef(self, line, last_encountered, last_taskdef ):
        """

        If a task is already started,
        this line is not a task,
        and this line is indented more than the last task definition:

        This line is part of a multiline task.

        Example:

            .. code-block:: ReStructuredText

                * This is my
                  very long task  # <-- continued taskdef

                  it occupies
                  multiple
                  lines


        """
        handled = False

        whitespace  = re.match('^[ \t]*', line)
        indentation = len(whitespace.group())

        if any([
            not whitespace,                           # no leading whitespace, cannot be continuation of task
            not last_taskdef,                         # no task currently being read, cannot continue extending task
            re.match('^[ \t]*[*+x\-]( |{\*)', line ), # this line is a task-definition, so not a continuation
            not len(last_encountered['indents']),     # no previous task indent, nothing to extend
        ]):
            return (handled, last_encountered, last_taskdef)

        if indentation > last_encountered['indents'][-1].indentation:
            handled = _ParserHandled.ContinuedDefinition
            last_taskdef.text.append( line.strip() )


        return (handled, last_encountered, last_taskdef)

    def _handle_existing_taskdef(self, line, last_encountered, last_taskdef ):
        """
        Handles a task-definition that has already been assigned
        a UUID.

        Example:

            .. code-block:: ReStructuredText

                *{*8DFD23B7636E4A0F91B7E13515762609*} My first task is to take over the world

        """
        handled = False

        uuid_regex      = '{\*[A-Z0-9]+\*}'
        exist_taskmatch = re.search( uuid_regex, line )


        if not exist_taskmatch:
            return (handled, last_encountered, last_taskdef)


        # build taskdef() for `tasks`
        # ===========================
        handled          = _ParserHandled.NewItemDefinition

        uuid_bracketed   = exist_taskmatch.group()
        linesplit        = line.split( uuid_bracketed )
        indentation      = len(line) - len(line.lstrip())
        _uuid            = uuid_bracketed[2:-2]


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

        last_taskdef = _taskdef(
            uuid        = _uuid,
            status      = status,
            isnew       = False,
            text        = [ linesplit[1].strip() ],
            indentation = indentation,
            section     = last_encountered['section'],
        )

        return (handled, last_encountered, last_taskdef)

    def _handle_new_taskdef(self, line, last_encountered, last_taskdef ):
        """
        Handles a task-definition that is not yet tracked in the ptaskfile.
        (has no uuid).

        Example:

            .. code-block:: ReStructuredText

                * My first task is to take over the world

        """
        handled       = False
        new_taskmatch = re.search( '^[ \t]*[*\-xo][ \t]', line )

        if not new_taskmatch:
            return (handled, last_encountered, last_taskdef)

        # build taskdef() for `tasks`
        # ===========================
        handled          = _ParserHandled.NewItemDefinition

        indentation = len(line) - len(line.lstrip())
        status_char = new_taskmatch.group()[-2]  # space then char
        status      = self._status_from_statuschar( status_char )
        _uuid       = uuid.uuid4().hex.upper()

        if not status:
            raise RuntimeError(
                'Invalid task. Missing or invalid status-char (+-x*): %s' % line
            )

        last_taskdef = _taskdef(
            uuid        = _uuid,
            status      = status,
            isnew       = True,
            text        = [ line[ len(new_taskmatch.group()) : ].strip() ],
            indentation = indentation,
            section     = last_encountered['section'],
        )

        return (handled, last_encountered, last_taskdef)

    def _add_taskdef_to_tasks(self, tasks, last_encountered, last_taskdef ):
        """
        Creates a :py:obj:`_taskinfo` object for the task,
        and appends it to the list `tasks`.
        """


        # strip all newlines after the task
        # (but keep newlines in the middle of task)
        trailing_blanklines = 0
        for i in reversed(range(len(last_taskdef.text))):
            if not last_taskdef.text[i]:   trailing_blanklines +=1
            else:                          break

        if trailing_blanklines:
            last_taskdef.text._replace( text=last_taskdef.text[ : -1 * trailing_blanklines ] )


        # determine parent/parent_type (by indentation)
        if len(last_encountered['indents']) == 0:
            if not last_taskdef.section:
                parent      = None
                parent_type = 'root'
            else:
                parent      = last_taskdef.section
                parent_type = 'section'

        else:
            handled = False

            # if section-changed, then this task (regardless of indentation)
            # is rooted to the section
            if tasks:
                if tasks[-1].section != last_taskdef.section:
                    parent      = last_taskdef.section
                    parent_type = 'section'
                    handled     = True

            # otherwise, check indentation to determine
            # the task's parent
            if not handled:
                for indent in reversed(last_encountered['indents']):
                    if indent.indentation < last_taskdef.indentation:
                        parent      = indent.uuid
                        parent_type = 'task'
                        handled     = True
                        break

                if not handled:
                    if last_taskdef.section:
                        parent      = last_taskdef.section
                        parent_type = 'section'
                    else:
                        parent      = None
                        parent_type = 'root'



        # add to `tasks`
        if last_taskdef.text:
            tasks.append(
                _taskinfo(
                    uuid        = last_taskdef.uuid,
                    text        = '\n'.join(last_taskdef.text),
                    section     = last_taskdef.section,
                    status      = last_taskdef.status,
                    parent      = parent,
                    parent_type = parent_type,
                    isnew       = last_taskdef.isnew,
                )
            )
        return tasks

    def _set_last_encountered_indentation(self, _uuid, indentation, last_encountered):
        indent = _taskindent( uuid=_uuid, indentation=indentation )

        while last_encountered['indents']:
            if   indentation == last_encountered['indents'][-1].indentation:
                last_encountered['indents'] = last_encountered['indents'][:-1]
                break

            elif indentation  < last_encountered['indents'][-1].indentation:
                last_encountered['indents'] = last_encountered['indents'][:-1]

            else:
                break

        last_encountered['indents'].append( indent )

        return last_encountered


    def archive_task(self):
        pass



class PtaskDataFile( UserList ):
    """
    Converts a :py:obj:`PtaskFile` string (vim buffer) into
    a JSON file.
    """
    def __init__(self, filepath=None ):
        UserList.__init__(self)

        if filepath:
            self._read_from_file( filepath )

    def _read_from_file(self, filepath):

        if not filepath:
            self.data = {}
            return

        self.data = json.load( open(filepath, 'r') )




if __name__ == '__main__':
    import os
    projdir   = '/'.join( os.path.realpath(__file__).split('/')[:-2] )

    def test_ptaskdata_2_ptask( projdir ):
        ptaskdata_file = '{projdir}/examples/raw/work.ptaskdata'.format(**locals())
        ptask = PtaskFile( ptaskdata_file )

        print(ptask)

    def test_ptask_taskinfo( projdir ):
        with open( '{projdir}/examples/raw/work_valid.ptask'.format(**locals()), 'r' ) as fd:
            ptask = PtaskFile()
            taskinfo  = ptask.ptask_taskinfo( fd )

            print('----')
            for task in taskinfo:
                print( task )

    def runtests():
        #test_ptaskdata_2_ptask( projdir )
        test_ptask_taskinfo( projdir )

    runtests()




