
" ===========
" Plugin Init
" ===========


let s:scriptroot=expand('<sfile>:p:h')

if !has('python')
    finish
    echo "Your version of vim does not support python"
else
    py import sys
    py import logging
    py logging.basicConfig(lv=20)
    execute 'py if "' . s:scriptroot . '" not in sys.path: sys.path.append("' . s:scriptroot . '")'
    py import taskmage2.vim_plugin
endif


" =========
" Functions
" =========

"function! TaskMageOpenCounterpart( open_command )
"    """
"    " Opens matching archived-file for task-files and vice-versa.
"    "
"    " Args:
"    "
"    "    open_command (str): ``(ex: 'edit', 'split', 'vsplit' )``
"    "       the vim-command to use to open the new buffer
"    " 
"    """
"    execute 'py taskmage2.vim_plugin.open_counterpart( "'. a:open_command .'" )'
"endfunc


function! TaskMageSaveStart()
    " saves cursor-pos, converts TaskList(rst)-to-Mtask(json)
    let s:saved_view = winsaveview()
    py taskmage2.vim_plugin.handle_presave_mtask()
endfunc

function! TaskMageSaveEnd()
    " converts saved-Mtask(json) back to TaskList(rst), restores cursor-pos 
    py taskmage2.vim_plugin.handle_postsave_mtask()
    call winrestview(s:saved_view)
endfunc


" ========
" Commands
" ========

command TaskMageCreateProject     py taskmage2.vim_plugin.create_project()
command TaskMageArchiveCompleted  py taskmage2.vim_plugin.archive_completed_tasks()

"command TaskMageToggle call TaskMageOpenCounterpart('edit')
"command TaskMageSplit  call TaskMageOpenCounterpart('split')
"command TaskMageVSplit call TaskMageOpenCounterpart('vsplit')
"command TaskMageCreateProject call TaskMageCreateProject()


" ========
" AutoCmds
" ========

autocmd BufRead             *.mtask  py taskmage2.vim_plugin.handle_open_mtask()
autocmd BufNewFile,BufRead  *.mtask  set filetype=taskmage2
autocmd BufWritePre         *.mtask  call TaskMageSaveStart()
autocmd BufWritePost        *.mtask  call TaskMageSaveEnd()

