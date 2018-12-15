
# TaskMage

A simple plaintext task manager, allowing you to edit tasks in
plaintext lists (quick to edit, no metadata clutter), and store metadata in 
json files (for genrating reports, searching by date, etc). Inspired by git 
and taskwarrior.

[screenshot](./media/screenshot.png)


<br><br>
{:toc}
<br><br>


# Install
<blockquote>
After setting up a vim plugin-manager like [vundle][1], [pathogen][2], etc. Add this plugin
to your `~/.vimrc`.

``` vim
Plugin 'https://github.com/willjp/vim-taskmage'
```

[1]: https://github.com/vim-scripts/vundle
[2]: https://github.com/tpope/vim-pathogen
</blockquote>


# Usage
<blockquote>
Create a taskmage project, then create/edit a `*.mtask` file within it.

``` vim

" create a new taskmage project
:TaskMageCreateProject

" create a new taskfile (alternatively from shell: touch file.mtask)
:edit file.mtask
```

Populate it with tasks, using a format similar to ReStructuredText. 

``` ReStructuredText
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
```

After completing several tasks, you can cleanup your tasklist
by archiving completed task-chains (archived if task/header and all children are complete).

``` vim
:TaskMageArchiveCompleted
```

You can compare your current tasks against completed tasks
side-by-side by looking at the archived-tasks.

``` vim
:TaskMageVSplit
```

I use git to synchronize tasks between my computers. On-disk, entries are recorded one-task-per-line
so that you can more easily resolve merge-conflicts. Occasionally, I find it useful keep a tasklist
alongside my source-tree.
</blockquote>


# Syntax
<blockquote>

## Tasks
Tasks are treated similarly to ReStructuredText list-items, except that
additional characters are used to indicate task-status.

``` ReStructuredText
*   # todo
x   # finished
-   # skipped
o   # currently in-progress
```

Tasks can be divided into subtasks by indenting them under their parent.

``` ReStructuredText
* clean kitchen
    * dishes
        * cutlery
            * spoons
            * forks
            * knives
```

## Sections
Tasks can be categorized into sections (which take the format of a
ReStructuredText header). Headers can be nested.


``` ReStructuredText
* fix mouse scrollwheel
* water plants

Tommorrow
=========

work
----

* UI for software-updater
* installer for software-updater 


home 
----

* christmas shopping
* taskmage documentation


After Tomorrow
==============

* package ep110
```

## Comments
Inline comments (within tasks) are also supported. 
They are technically a part of the message of a task, but they are 
syntax-highlighted differently so that they stand out.

``` ReStructuredText
* do dishes  # start with forks!
             # then continue with spoons!

* another task
```
</blockquote>


#Projects
<blockquote>

Like git, taskmage uses a directory to indicate a project-root,
and store completed task-data. 


active
``` python
/todos/
    home/
        family.mtask
        sideprojects.mtask
    today.mtask
```

archive
``` python
/todos/.taskmage/
    home/
        family.mtask
        sideprojects.mtask
    today.mtask
```

</blockquote>
