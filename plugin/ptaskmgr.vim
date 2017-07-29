

"" Plugin Init
""
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



"" Commands
""

function! PtaskArchiveCompleted()
    py ptaskmgr.vim_plugin.archive_completed_tasks()
endfunc
command PtaskArchiveCompleted  call PtaskArchiveCompleted()


function! PtaskOpenCounterpart( open_command )
    execute 'py ptaskmgr.vim_plugin.open_counterpart( "'. a:open_command .'" )'
endfunc
command PtaskToggle call PtaskOpenCounterpart('edit')
command PtaskSplit  call PtaskOpenCounterpart('split')
command PtaskVSplit call PtaskOpenCounterpart('vsplit')


function! PtaskCreateProject()
    py ptaskmgr.vim_plugin.create_project()
endfunc
command PtaskCreateProject call PtaskCreateProject()



"" AutoCmds
""

    " on-read, replace buffer with RST
autocmd BufRead      *.ptask  py ptaskmgr.vim_plugin.jsonfile_to_rst()

    " on-write, replace buffer with JSON, then 
    " after save convert back into RST
autocmd BufWritePre  *.ptask  py ptaskmgr.vim_plugin.rst_to_json()
autocmd BufWritePost *.ptask  py ptaskmgr.vim_plugin.jsonfile_to_rst()



