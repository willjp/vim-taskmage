
" ===========
" Plugin Init
" ===========
let s:scriptroot=expand('<sfile>:p:h')

if !has('python')
	finish
	echo "Your version of vim does not support python"
else
	execute 'pyfile ' .   s:scriptroot . '/ptaskmgr_init_syspath.py'
	execute 'py import ptaskmgr.vim_plugin'
	py import logging
	py logging.basicConfig( lv=20 )
endif



" ========
" Commands
" ========

function! PtaskArchiveCompleted()
    """
    " Archives all completed tasks 
    " ( provided all of their parents are also completed )
    """
    py ptaskmgr.vim_plugin.archive_completed_tasks()
endfunc
command PtaskArchiveCompleted  call PtaskArchiveCompleted()


function! PtaskOpenCounterpart( open_command )
    """
    " Opens matching archived-file for task-files and vice-versa.
    "
    " Args:
    "
    "    open_command (str): ``(ex: 'edit', 'split', 'vsplit' )``
    "       the vim-command to use to open the new buffer
    " 
    """
    execute 'py ptaskmgr.vim_plugin.open_counterpart( "'. a:open_command .'" )'
endfunc
command PtaskToggle call PtaskOpenCounterpart('edit')
command PtaskSplit  call PtaskOpenCounterpart('split')
command PtaskVSplit call PtaskOpenCounterpart('vsplit')


function! PtaskCreateProject()
    """ 
    " prompts user to create a new vim project 
    """
    py ptaskmgr.vim_plugin.create_project()
endfunc
command PtaskCreateProject call PtaskCreateProject()


function! PtaskSaveStart()
    """ 
    " saves cursor-pos, converts Rst-to-Json 
    """
    let s:saved_view = winsaveview()
    py   ptaskmgr.vim_plugin.rst_to_json()
endfunc

function! PtaskSaveEnd()
    """ 
    " converts saved-json back to rst, restores cursor-pos 
    """
    py   ptaskmgr.vim_plugin.jsonfile_to_rst()
    call winrestview( s:saved_view )
endfunc




" ========
" AutoCmds
" ========

" on-read, replace buffer with RST
autocmd BufRead      *.ptask  py ptaskmgr.vim_plugin.jsonfile_to_rst()


autocmd BufWritePre  *.ptask  call PtaskSaveStart()
autocmd BufWritePost *.ptask  call PtaskSaveEnd()



