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
#package
#external
#internal


class PtaskFile( six.UserString ):
    """
    Converts a :py:obj:`PtaskDataFile` JSON object into
    a file designed to be edited in vim.
    """
    def __init__(self, filepath=None):
        self.data  = ''
        self._dict = {}

    def from_ptaskdata(self, filepath):
        rawdata    = json.load( open(filepath,'r') )
        self.data  = ''


        hierarchy = OrderedDict()
        
        # create a dict of parents and their children
        # {
        #    'toplevel_tasks': [ taskId, taskid, ... ],
        #    'sections':       { section : [ taskId, taskId, ... ] },
        #    'tasks':          { taskId  : [ taskId, taskId, ... ] },
        # }
        #
        # saved as OrderedDict() so that item-order is preserved.
        for task in rawdata:
            if task['section']:
                if task['section'] not in hierarchy:
                    hierarchy['sections'][ task['section'] ] = [ task['_id'] ]
                else:
                    hierarchy['sections'][ task['section'] ].append( task['_id'] )
            
            elif task['parenttask']:
                if task['parenttask'] not in hierarchy:
                    hierarchy['tasks'][ task['parenttask'] ] = [ task['parenttask'] ]
                else:
                    hierarchy['tasks'][ task['parenttask'] ].append( task['parenttask'] )

            else:
                hierarchy['toplevel_tasks'].append( task['_id'] )



        # !!!!!!!!!!!!!!!!!!!!
        # TODO: LEFT OFF HERE
        # !!!!!!!!!!!!!!!!!!!!

        # tasks without sections (and their subtasks) are placed at the very top
        # followed by sections and their tasks/subtasks
                    

        # navigate down the hierarchy (starting from sections)
        # and write the actual file contents.
        for section in hierarchy['sections']:
            self.data += '\n\n'
            self.data += section.title()
            self.data += '='* len(section)

            self.data = self._get_ptaskdata_tasks( 
                    ptask     = self.data,
                    parent    = section,
                    hierarchy = hierarchy,
                    data      = data,
            )


    def _get_ptaskdata_tasks(self, ptask, parent, hierarchy, data, depth=0):
        """
        Recursively navigates down hierarchy, adding
        to the string, and incrementing at each level
        of nested parenting.
        """
        ptask += ('    ' * depth) + data[
        if parent in hierarchy:
        pass


    def edit_task(self):
        """
        Edit a single task as a conf file
        """
        # will require it's own pair of data vs string
        # (unless we use something like a conf-file as intermediary)
        raise NotImplementedError('TODO')


class PtaskDataFile( six.IterableUserDict ):
    """
    Converts a :py:obj:`PtaskFile` string (vim buffer) into 
    a JSON file.
    """
    def __init__(self, filepath=None, string=None):
        pass


    def save(self, filepath):
        pass



