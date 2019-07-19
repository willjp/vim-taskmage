
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


" =============
" Configuration
" =============

let g:tagbar_type_taskmage = {
        \ 'ctagstype': 'taskmage',
        \ 'ctagsbin': s:scriptroot . '/../bin/taskmage2ctags.py',
        \ 'ctagsargs': '-f - --sro » --lexer tasklist',
        \ 'kinds': [
            \ 's:sections'
        \ ],
        \ 'kind2scope': {
            \ 's': 'section'
        \ },
        \ 'sro' : '»',
        \ 'sort': 0,
    \ }


" ========
" Commands
" ========

command TaskMageCreateProject     py taskmage2.vim_plugin.create_project()
command TaskMageArchiveCompleted  py taskmage2.vim_plugin.archive_completed_tasks()

command -nargs=* TaskMageOpenCounterpart   py taskmage2.vim_plugin.open_counterpart('<args>')
command          TaskMageToggle            py taskmage2.vim_plugin.open_counterpart('edit')
command          TaskMageSplit             py taskmage2.vim_plugin.open_counterpart('split')
command          TaskMageVSplit            py taskmage2.vim_plugin.open_counterpart('vsplit')
command -nargs=1 TaskMageSearch            py taskmage2.vim_plugin.search_keyword('<args>')
command          TaskMageLatest            py taskmage2.vim_plugin.search_latest()


" ========
" AutoCmds
" ========

autocmd BufRead             *.mtask  py taskmage2.vim_plugin.handle_open_mtask()
autocmd BufNewFile,BufRead  *.mtask  set filetype=taskmage
autocmd BufWritePre         *.mtask  call TaskMageSaveStart()
autocmd BufWritePost        *.mtask  call TaskMageSaveEnd()

