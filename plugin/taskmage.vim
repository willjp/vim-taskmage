
" ===========
" Plugin Init
" ===========
let s:scriptroot=expand('<sfile>:p:h')

if !has('python')
    finish
    echo "Your version of vim does not support python"
else
    execute 'pyfile ' .   s:scriptroot . '/taskmage_init_syspath.py'
    execute 'py import taskmage.vim_plugin'
    py import logging
    py logging.basicConfig( lv=20 )
endif



" ========
" Commands
" ========

function! TaskMageArchiveCompleted()
    """
    " Archives all completed tasks 
    " ( provided all of their parents are also completed )
    """
    py taskmage.vim_plugin.archive_completed_tasks()
endfunc
command TaskMageArchiveCompleted  call TaskMageArchiveCompleted()


function! TaskMageOpenCounterpart( open_command )
    """
    " Opens matching archived-file for task-files and vice-versa.
    "
    " Args:
    "
    "    open_command (str): ``(ex: 'edit', 'split', 'vsplit' )``
    "       the vim-command to use to open the new buffer
    " 
    """
    execute 'py taskmage.vim_plugin.open_counterpart( "'. a:open_command .'" )'
endfunc
command TaskMageToggle call TaskMageOpenCounterpart('edit')
command TaskMageSplit  call TaskMageOpenCounterpart('split')
command TaskMageVSplit call TaskMageOpenCounterpart('vsplit')


function! TaskMageCreateProject()
    """ 
    " prompts user to create a new vim project 
    """
    py taskmage.vim_plugin.create_project()
endfunc
command TaskMageCreateProject call TaskMageCreateProject()


function! TaskMageSaveStart()
    """ 
    " saves cursor-pos, converts Rst-to-Json 
    """
    let s:saved_view = winsaveview()
    py   taskmage.vim_plugin.rst_to_json()
endfunc

function! TaskMageSaveEnd()
    """ 
    " converts saved-json back to rst, restores cursor-pos 
    """
    py   taskmage.vim_plugin.jsonfile_to_rst()
    call winrestview( s:saved_view )
endfunc




" ========
" AutoCmds
" ========

" on-read, replace buffer with RST
autocmd BufRead      *.mtask  py taskmage.vim_plugin.jsonfile_to_rst()


autocmd BufWritePre  *.mtask  call TaskMageSaveStart()
autocmd BufWritePost *.mtask  call TaskMageSaveEnd()



