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
import datetime
if sys.version_info[0] <= 2:
    from UserString  import UserString
    from UserList    import UserList
else:
    from collections import UserString
    from collections import UserList
#package
from .        import six
from .project import get_projectroot
#external
#internal

#!TODO: multiline task comments


_taskinfo = namedtuple(
    # explicit info about a task
    'taskinfo', [
        'uuid',
        'text',
        'section',
        'status',
        'created',
        'parent',
        'parent_type', # 'root', 'section', 'task'
        'isnew'
    ]
)
_taskdef = namedtuple(
    # info obtained from a ReStructuredText task
    # ( needs help from json file for full taskinfo )
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



class _TaskDataFmt( Enum ):
    """
    Enum listing the various accepted input/output formats
    of for :py:obj:`ptaskmgr.TaskData` .
    """
    data = 1
    rst  = 2
    json = 3



class TaskData( UserList ):
    """
    An object representing a single *.ptask file's list of tasks
    as a python list.


    Example:

        .. code-block:: python

            [
                {
                    '_id':        '52EB34660CBE40EFA481452909BCD408',
                    'status':     'todo',   # todo, done, skip, wip
                    'created':    '2017-07-26T20:26:13.675941-04:00',
                    'text':       'finish fixing ...',

                    # optional keys
                    'parenttask': 'E762BCA9CAA1477CB102E7DA3DE7E2B0',
                    'section':    'home todos',
                }
            ]


    Attributes:

        datafmt (Enum):
            Enum class that lists the accepted
            types of TaskData formats.

            * `data (list)`: The native-format of this TaskData object,
                             equivalent to the raw JSON file (*.ptask),
                             once parsed by this class.

                             .. code-block:: python

                                [
                                  {
                                    "status"   : "todo",
                                    "text"     : "a",
                                    "finished" : false,
                                    "_id"      : "C176274F1CD741D2AB3FB3F2FAA05D06"
                                  },
                                  ...
                                ]

            * `rst (str)`:  A string in the ReStructuredText inspired format.
                            This format is the view of the tasklist that is
                            edited by the user.

                            .. code-block:: ReStructuredText

                                *{*36F8F60D60DD46698BE972213697D531*} clean kitchen
                                    *{*329BB41F3A4446B3A171206BF63D2483*} clean stove
                                    * clean fridge
                                    * wash dishes

                                Homework
                                ========

                                * Calculus: Chapter 11


            * `json (str)`: A raw, unparsed string of JSON.

                .. code-block:: json

                    [
                      {
                        "status"   : "todo",
                        "text"     : "a",
                        "finished" : false,
                        "_id"      : "C176274F1CD741D2AB3FB3F2FAA05D06"
                      },
                      ...
                    ]



            See also:
                * :py:meth:`set_data`

    """
    datafmt = _TaskDataFmt # enum with various data formats
    def __init__(self, taskdata=None, datafmt=None, datapath=None ):
        """
        Args:
            taskdata (str, list, optional):
                The data that you would like to use (parse)
                to intialize this :py:obj:`TaskData` object's
                data.

            datafmt (ptaskmgr.TaskData.datafmt, optional):
                Indicates the type of data `taskdata` is.

            datapath (str, optional): ``(ex:  '/home/todo/file.ptask' )``
                Path to a .ptask file (json) that (if exists)
                contains additional information about tasks.

                *used only by 'rst' datafmt*
        """
        UserList.__init__(self)

        # Load
        if any([taskdata, datafmt, datapath]):
            if not all([x != None for x in (taskdata, datafmt)]):
                raise TypeError(
                    'If either `taskdata` or `datafmt` arguments are provided, '
                    'they are both required.'
                )

            self.set_data( taskdata, datafmt, datapath )


    def isinitialized(self):
        """
        Returns ``True`` if this object has had it's information
        set using :py:meth:`set_data` .
        """
        if self._isinitialized:
            return True
        return False

    def clear(self):
        """
        DisAssociates this object with it's info.
        """
        self._isinitialized = False
        self.data           = []


    def set_data(self, taskdata, datafmt, datapath=None ):
        """
        Reads from a source, and updates the tasklist this object represents.

        Args:
            taskdata (str, list):
                The data that you would like to use (parse)
                to intialize this :py:obj:`TaskData` object's
                data.

            datafmt (ptaskmgr.TaskData.datafmt):
                Indicates the type of data `taskdata` is.

            datapath (str, optional): ``(ex:  '/home/todo/file.ptask' )``
                Path to a .ptask file (json) that (if exists)
                contains additional information about tasks.

                *used only by 'rst' datafmt*


        Side Effect:

            This object's tasklist is set:

            .. code-block:: python

                [
                  {
                    "status"   : "todo",
                    "text"     : "a",
                    "finished" : false,
                    "_id"      : "C176274F1CD741D2AB3FB3F2FAA05D06"
                  },
                  {
                    "status"     : "todo",
                    "text"       : "b",
                    "finished"   : false,
                    "_id"        : "6D2C0034D18B475E8210909796FB151E",
                    "parenttask" : "C176274F1CD741D2AB3FB3F2FAA05D06"
                  },
                ]

        """

        self.clear()

        if datafmt == TaskData.datafmt.data:
            self._load_from_taskdata( taskdata )

        elif datafmt == TaskData.datafmt.rst:
            self._load_from_rst( taskdata, datapath )

        elif datafmt == TaskData.datafmt.json:
            self._load_from_json( taskdata )

        else:
            raise TypeError(
                ('`datafmt` expects a choice from the enum '
                '`TaskData.datafmt`. Received: %s') % datafmt
            )

        self._isinitialized = True

    def _load_from_taskdata(self, taskdata):
        """
        Validates and sets TaskData.
        """
        #TODO: validate taskdata!
        self.data = taskdata

    def _load_from_json(self, jsonstr ):
        """
        Loads TaskData from a non-decoded json object (string).
        """

        taskdata  = json.loads( jsonstr )

        #TODO: convert datatypes into native(?)

        self._load_from_taskdata( taskdata )

    def _load_from_rst(self, rst, datapath):
        """
        Args:
            rst (str):
                A string representing a full, multiline taskdata
                JSON object represented in ReStructuredText format.

            datapath (str, optional): ``(ex:  '/home/todo/file.ptask' )``
                Path to a .ptask file (json) that (if exists)
                contains additional information about tasks.

                *used only by 'rst' datafmt*
        """
        if not datapath:
            raise TypeError(
                'parsing Rst task format requires `datapath` argument'
            )


        taskdata = _RstTaskParser( rst.split('\n'), datapath )
        self._load_from_taskdata( taskdata )


    def add_taskinfo(self, taskinfo):
        """
        Adds a single task to this taskdata object
        from a :py:obj:`_taskinfo` namedtuple.

        Args:
            taskinfo (_taskinfo):
                A :py:obj:`_taskinfo` object representing a task
        """

        task = self.taskinfo_to_task( taskinfo )
        self.data.append( task )

    def render_datafmt(self, datafmt):
        """
        Renders the current :py:obj:`TaskData` list to
        another one of the supported formats, and returns
        it.

        Args:
            datafmt (ptaskmgr.TaskData.datafmt):
                Indicates the type of data `taskdata` is.

        Returns:

            * `data`: a copy of this object (python list)
            * `json`: a JSON string, ready to be written to a file
            * `rst`:  a string in the ReStructuredText inspired task list format.
        """

        if datafmt == TaskData.datafmt.data:
            return self._render_to_taskdata()

        elif datafmt == TaskData.datafmt.rst:
            return self._render_to_rst()

        elif datafmt == TaskData.datafmt.json:
            return self._render_to_json()

        else:
            raise TypeError(
                ('`datafmt` expects a choice from the enum '
                '`TaskData.datafmt`. Received: %s') % datafmt
            )

    def _render_to_taskdata(self):
        """

        Returns:

            .. code-block:: python

                [
                    {
                        "_id":      "40429D679A504ED99F97D0D16067B2B3",
                        "section":  "other",
                        "created":  "2017-06-11T22:40:52.460849-04:00",
                        "finished": null,
                        "text":     "A task under a different category",
                        "status":   "skip"
                    },
                    {
                        "_id":      "E061DCB183EF4C418E97DEE63332C1A0",
                        "section":  "misc",
                        "created":  "2017-06-11T22:40:52.460849-04:00",
                        "finished": null,
                        "text":     "A test comment within a category",
                        "status":   "todo"
                    },
                ]
        """
        return list(self)

    def _render_to_json(self):
        """
        Produces an encoded JSON object, ready
        to be written to a file

        Returns:

            .. code-block:: json

                [
                    {
                        "_id":      "40429D679A504ED99F97D0D16067B2B3",
                        "section":  "other",
                        "created":  "2017-06-11T22:40:52.460849-04:00",
                        "finished": null,
                        "text":     "A task under a different category",
                        "status":   "skip"
                    },
                    {
                        "_id":      "E061DCB183EF4C418E97DEE63332C1A0",
                        "section":  "misc",
                        "created":  "2017-06-11T22:40:52.460849-04:00",
                        "finished": null,
                        "text":     "A test comment within a category",
                        "status":   "todo"
                    },
                ]

        """
        return json.dumps( list(self), indent=2 )

    def _render_to_rst(self):
        """
        ReStructures the current data as a ReStructuredText inspired
        string. This is what users edit in vim.

        Returns:

            .. code-block:: ReStructuredText

                *{*36F8F60D60DD46698BE972213697D531*} clean kitchen
                    *{*329BB41F3A4446B3A171206BF63D2483*} clean stove
                    * clean fridge
                    * wash dishes

                Homework
                ========

                * Calculus: Chapter 11
        """

        tasks     = OrderedDict()
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
        for task in self.data:
            tasks[ task['_id'] ] = task
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
        # building `rst_str` progressively
        # ==============================================

        rst_str = '\n\n'

        for taskId in hierarchy['toplevel_tasks']:
            rst_str = self._get_taskhier_branch_rst(
                taskId    = taskId,
                ptask_str = rst_str,
                hierarchy = hierarchy,
            )

        for section in hierarchy['sections']:
            rst_str += '\n\n'
            rst_str += section +'\n'
            rst_str += '=' * len(section) +'\n\n'

            for taskId in hierarchy['sections'][section]:
                rst_str = self._get_taskhier_branch_rst(
                    taskId    = taskId,
                    ptask_str = rst_str,
                    hierarchy = hierarchy,
                )

        return rst_str

    def _get_taskhier_branch_rst(self, taskId, ptask_str, hierarchy, depth=0 ):
        """
        Renders a task and all of it's entire child-task hierarchy
        in the ReStructuredText inspired format
        (appending to the existing `ptask_str`, if provided).


        Args:
            taskId (str):
                the uuid assigned to a particular task

            ptask_str (str):
                the string destined to be the *.ptask file so far.
                (return value)

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

        """

        taskinfo = self.get_taskinfo( taskId )

        if not taskinfo:
            return

        if   taskinfo.status  == 'todo': status = '*'
        elif taskinfo.status  == 'done': status = 'x'
        elif taskinfo.status  == 'wip':  status = 'o'
        elif taskinfo.status  == 'skip': status = '-'

        # current task
        ptask_str += ('    '*depth) + '%s{*%s*} %s\n' % (status, taskinfo.uuid, taskinfo.text)


        # recurse for subtasks
        if taskinfo.uuid in hierarchy['tasks']:
            for _taskId in hierarchy['tasks'][ taskinfo.uuid ]:
                ptask_str = self._get_taskhier_branch_rst(
                    taskId    = _taskId,
                    ptask_str = ptask_str,
                    hierarchy = hierarchy,
                    depth     = depth+1,
                )

        return ptask_str


    def get_taskinfo(self, taskId):
        """
        Obtains a `taskinfo` :py:obj:`namedtuple` with task information.

        Returns:

            .. code-block:: python

                # If a task matching taskId is found
                taskinfo = _taskinfo(
                    uuid        = 'cb798ab368eb400fa4d0edd941c03536',
                    text        = 'Make sure to do blah',
                    section     = None,  # or the section name
                    status      = 'todo',
                    parent      = None
                    parent_type = 'root', # 'root', 'section', 'task'

                    created     = '2017-07-29T10:33:28.754000-00:00',

                    isnew       = False,  # all tasks obtained from this method
                                          # return False, because they exist in
                                          # this TaskData() object.
                )

                # If no task matches taskId
                False
        """

        if not self.isinitialized():
            raise RuntimeError(
                'Cannot retrive a taskId if this object is not initialized with any taskdata.'
                'Make sure to run `TaskData().set_data()` before using this method.'
            )

        # find task from taskId
        # =====================
        for task in self.data:
            if task['_id'] == taskId:

                if 'parenttask' in task:
                    parent      = task['parenttask']
                    parent_type = 'task'

                elif 'section' in task:
                    parent      = task['section']
                    parent_type = 'section'

                else:
                    parent      = None
                    parent_type = 'root'


                section = None
                if section in task:
                    section = task['section']

                taskinfo = _taskinfo(
                    uuid        = taskId,
                    text        = task['text'],
                    section     = section,
                    status      = task['status'],
                    parent      = parent,
                    parent_type = parent_type,
                    created     = task['created'],
                    isnew       = False,
                )

                return taskinfo

        logger.error('Corrupted Data: Unable to find task with ID: %s' % taskId)
        return False

    def remove_tasks(self, taskIds):
        """
        Removes tasks from this :py:obj:`TaskData` object.
        (this is used when archiving tasks)

        Args:
            taskIds (list(str), optional): ``(ex: None, ['E7E47D40A54244B997A61F074738CCF7', ...] )``
                A list of uuids of the tasks you'd like to archive.

        Returns:

            .. code-block:: python

                [
                    _taskinfo(
                        uuid        = 'cb798ab368eb400fa4d0edd941c03536',
                        text        = 'Make sure to do blah',
                        section     = None,  # or the section name
                        status      = 'todo',
                        parent      = None
                        parent_type = 'root', # 'root', 'section', 'task'

                        created     = '2017-07-29T10:34:04.642887-00:00',

                        isnew       = False,  # all tasks obtained from this method
                                              # return False, because they exist in
                                              # this TaskData() object.
                    ),
                    _taskinfo(...),
                    ...
                ]

        """


        # nothing to do
        if not taskIds:
            return

        # remove tasks from self.data
        archived_tasks = []
        rm_count       = 0
        taskdata       = list(self.data)
        if taskdata:
            for i in range(len(taskdata)):
                task = taskdata[i]

                if task['_id'] in taskIds:

                    # remove from self.data
                    archived_tasks.append( self.get_taskinfo(task['_id']) )
                    self.data.pop(i - rm_count)
                    rm_count += 1

        return archived_tasks

    def remove_completed(self):
        """
        Removes all completed tasks.
        (this is used when archiving tasks)

        Returns:

            .. code-block:: python

                ## if completed tasks
                [
                    _taskinfo(
                        uuid        = 'cb798ab368eb400fa4d0edd941c03536',
                        text        = 'Make sure to do blah',
                        section     = None,  # or the section name
                        status      = 'todo',
                        parent      = None
                        parent_type = 'root', # 'root', 'section', 'task'

                        isnew       = False,  # all tasks obtained from this method
                                              # return False, because they exist in
                                              # this TaskData() object.
                    ),
                    _taskinfo(...),
                    ...
                ]

                ## if no completed tasks
                []

        """
        # find all completed tasks, all of whose
        # child tasks are also completed.

        # get completed tasks
        completed_tasks = set()


        def task_branch_completed( taskid, tasks, children, _completed_tasks=None ):
            """
            returns ``True`` if task and all children
            are complete.

            Args:
                taskid (str): ``(ex: '296482ed430c4cbf9d39afefb52fa3e3' )``

                children (dict): ``(ex: {_id:set(childId,childId,...)} )``
                    pass
            """
            if tasks[ taskid ]['status'] not in ('skip','done'):
                return False

            if not _completed_tasks:
                _completed_tasks = set()

            _completed_tasks.add( taskid )

            if children[ taskid ]:
                for childId in children[ taskid ]:
                    if not task_branch_completed( childId, tasks, children, _completed_tasks ):
                        return False
                    _completed_tasks.add( childId )

            return _completed_tasks




        # build dict of tasks,
        # task-children,
        # and set of toplevel tasks (section or root)
        # ===========================================
        toplvl_taskids  = set() # set([ _id, _id, ... ])
        tasks           = {}    # ``{_id:{...}, _id:{...}}``   self.data made into a dict
        children        = {}    # ``{_id:set([ parent_id, parent_id ]), _id:set(), ...}``


        for task in self.data:
            taskid = task['_id']
            tasks[ taskid ] = task

            if 'parenttask' not in task:
                toplvl_taskids.add( taskid )

                if taskid not in children:
                    children[ taskid ] = set()
            else:
                if taskid not in children:
                    children[ taskid ] = set()
                if task['parenttask'] not in children:
                    children[ task['parenttask'] ] = set()

                children[ task['parenttask'] ].add( taskid )



        # only archive toplevel tasks,
        # and only if all of their children
        # are completed.
        for taskid in toplvl_taskids:
            completed = task_branch_completed( taskid, tasks, children )
            if completed:
                completed_tasks.update( completed )


        # return tasks
        # ============
        if completed_tasks:
            return self.remove_tasks( completed_tasks )
        else:
            return []


    def taskinfo_to_task(self, taskinfo ):
        """
        Converts a taskinfo (namedtuple) object to a task
        dictionary (as it appears in JSON file).

        Args:
            taskinfo (_taskinfo):
                A :py:obj:`_taskinfo` object representing a task
        """

        now     = datetime.datetime.utcnow()
        now_iso = now.isoformat()
        new_task = {
            'status': taskinfo.status,
            'text'  : taskinfo.text,
            '_id'   : taskinfo.uuid,
        }


        # finished
        if taskinfo.status in ('skip','done'):
            new_task['finished'] = now_iso
            new_task['created']  = taskinfo.created
        else:
            if taskinfo.created == None:
                new_task['created'] = now_iso
            else:
                new_task['created'] = taskinfo.created

            new_task['finished'] = False


        # created timestamp
        if taskinfo.isnew:
            new_task['created'] = now_iso


        # parent info
        if taskinfo.parent_type == 'root':
            pass

        elif taskinfo.parent_type == 'task':
            new_task['parenttask'] = taskinfo.parent

        elif taskinfo.parent_type == 'section':
            new_task['section'] = taskinfo.parent

        return new_task



class _RstTaskParser( UserList ):
    """
    Parses a ReStructuredText inspired todolist into
    a format that is compatible with :py:obj:`ptaskmgr.TaskData`
    """
    def __init__(self, fileconts, datapath ):
        """
        Args:
            fileconts (collections.Iterable):
                A list, file-descriptor, or other iterable
                collection where each item represents a single
                line of text from the ReStructuredText
                formatted taskfile.
        """
        UserList.__init__(self)


        if os.path.isfile( datapath ):
            with open( datapath, 'r' ) as fd:
                self._saved_taskdata = TaskData(
                    taskdata=fd.read(), datafmt=TaskData.datafmt.json,
                )
        else:
            self._saved_taskdata = TaskData(
                taskdata=[], datafmt=TaskData.datafmt.data
            )


        now = datetime.datetime.utcnow()

        taskdata = []
        for task in self._taskinfo_from_rst( fileconts ):
            new_task = {
                'status': task.status,
                'text'  : task.text,
                '_id'   : task.uuid,
            }

            # finished
            if task.status in ('skip','done'):
                new_task['finished'] = now.isoformat()
            else:
                new_task['finished'] = False


            # created timestamp
            if task.isnew:
                new_task['created'] = now.isoformat()
            else:
                taskinfo = self._saved_taskdata.get_taskinfo( task.uuid )
                new_task['created'] = taskinfo.created


            # parent info
            if task.parent_type == 'root':
                pass

            elif task.parent_type == 'task':
                new_task['parenttask'] = task.parent

            elif task.parent_type == 'section':
                new_task['section'] = task.parent


            taskdata.append( new_task )

        self.data = taskdata

    def _taskinfo_from_rst(self, fileconts):
        """
        Creates a list of :py:obj:`_taskinfo` objects for all.

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


        Args:
            tasks ( list(_taskinfo) ):
                A list of taskinfo objects. The new task
                will be appended to this.

            last_encountered (dict):
                A dictionary storing the last occurrences
                of various .ptask elements.

                .. code-block:: ReStructuredText

                    {
                        'line':     '   * last line from file',
                        'section':  'home',
                        'indents':  [ _taskindent(), _taskindent(), ... ],
                    }

        """


        # strip all newlines after the task
        # (but keep newlines in the middle of task)
        trailing_blanklines = 0
        for i in reversed(range(len(last_taskdef.text))):
            if not last_taskdef.text[i]:   trailing_blanklines +=1
            else:                          break

        if trailing_blanklines:
            last_taskdef._replace( text=last_taskdef.text[ : -1 * trailing_blanklines ] )


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

            if last_taskdef.isnew:
                created        = None
            else:
                saved_taskinfo = self._saved_taskdata.get_taskinfo( last_taskdef.uuid )
                created        = saved_taskinfo.created

            tasks.append(
                _taskinfo(
                    uuid        = last_taskdef.uuid,
                    text        = '\n'.join(last_taskdef.text),
                    section     = last_taskdef.section,
                    status      = last_taskdef.status,
                    parent      = parent,
                    parent_type = parent_type,
                    isnew       = last_taskdef.isnew,
                    created     = created,
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




if __name__ == '__main__':
    ## python -m ptaskmgr.parser

    import os
    projdir   = '/'.join( os.path.realpath(__file__).split('/')[:-2] )


    def test_remove_completed():
        taskdata = [
            {
                '_id':     '9f0520b8f31d4bd4ad7b86348ecb7ac4',
                'status':  'done',
                'text':    'a',
                'created': '2017-07-28T21:32:45.175813-04:00'
            },
            {
                '_id':         '56909776a3dc4c17961ba3ea2e4a2d20',
                'status':      'done',
                'text':        'b',
                'created':     '2017-07-28T21:35:05.125148-04:00',
                'parenttask':  '9f0520b8f31d4bd4ad7b86348ecb7ac4',
            },
            #{
            #    '_id':         '0a022be074fe4d69bda952dd8690c0b9',
            #    'status':      'todo',
            #    'text':        'b',
            #    'created':     '2017-07-28T21:35:05.125148-04:00',
            #    'parenttask':  '9f0520b8f31d4bd4ad7b86348ecb7ac4',
            #}
        ]
        data = TaskData(
            taskdata = taskdata,
            datafmt  = TaskData.datafmt.data,
        )

        print( data.remove_completed() )

    def runtests():
        test_remove_completed()

    runtests()



