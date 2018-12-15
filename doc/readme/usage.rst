
Usage
=====

**1.** Create a taskmage project, then create/edit a ``*.mtask`` file within it.

    .. code-block:: vim
    
        " create a new taskmage project
        :TaskMageCreateProject
    
        " create a new taskfile (alternatively from shell: touch file.mtask)
        :edit file.mtask


**2.** Populate it with tasks, using a format similar to ReStructuredText.

    .. code-block:: ReStructuredText
    
        Trip Home
        =========
    
        * grocery shopping
          x apples
          x oranges
          * sick supplies for Alex
            for while she isn't feeling well
          - deodorant
            
        Home
        ====
    
        * finish ZNC server setup
            * write saltstack recipe for ZNC server setup
            * test saltstack recipe


**3.** After completing several tasks, you can cleanup your tasklist by archiving completed task-chains (archived if task/header and all children are complete).

    .. code-block:: vim
    
        :TaskMageArchiveCompleted


**4.** You can compare your current tasks against completed tasks side-by-side by looking at the archived-tasks.

    .. code-block:: vim
    
        :TaskMageVSplit


*I use git to synchronize tasks between my computers. On-disk, entries are recorded one-task-per-line
so that you can more easily resolve merge-conflicts. Occasionally, I find it useful keep a tasklist
alongside my source-tree.*
