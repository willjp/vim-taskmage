if exists('vim_taskmage_loaded') || &cp
    finish
endif
let vim_taskmage_loaded=1


" ===========
" Plugin Init
" ===========


let s:scriptroot=expand('<sfile>:p:h')

if !has('pythonx')
    echom "[taskmage error]: requires python 2 or 3"
    finish
else
    try
        pyx import sys
        pyx import logging
        execute 'pyx if "' . s:scriptroot . '" not in sys.path: sys.path.append("' . s:scriptroot . '")'
        pyx import taskmage2.vim_plugin
    catch 
        echom "[taskmage error]: " . v:errmsg
    endtry
endif


" =========
" Functions
" =========

function! TaskMageSaveStart()
    " saves cursor-pos
    let s:saved_view = winsaveview()

    " converts TaskList(rst)-to-Mtask(json)
    pyx taskmage2.vim_plugin.handle_presave_mtask()
endfunc

function! TaskMageSaveEnd()
    " converts saved-Mtask(json) back to TaskList(rst), restores cursor-pos 
    pyx taskmage2.vim_plugin.handle_postsave_mtask()

    " restore cursor postion
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

command TaskMageCreateProject     pyx taskmage2.vim_plugin.create_project()
command TaskMageArchiveCompleted  pyx taskmage2.vim_plugin.archive_completed_tasks()

command -nargs=* TaskMageOpenCounterpart   pyx taskmage2.vim_plugin.open_counterpart('<args>')
command          TaskMageToggle            pyx taskmage2.vim_plugin.open_counterpart('edit')
command          TaskMageSplit             pyx taskmage2.vim_plugin.open_counterpart('split')
command          TaskMageVSplit            pyx taskmage2.vim_plugin.open_counterpart('vsplit')
command -nargs=1 TaskMageSearch            pyx taskmage2.vim_plugin.search_keyword('<args>')
command -nargs=* TaskMageLatest            pyx taskmage2.vim_plugin.search_latest('<f-args>')


" ========
" AutoCmds
" ========

autocmd BufReadCmd          *.mtask  call pyxeval('taskmage2.vim_plugin.handle_open_mtask()')
autocmd BufNewFile,BufRead  *.mtask  set filetype=taskmage
autocmd BufWritePre         *.mtask  call TaskMageSaveStart()
autocmd BufWritePost        *.mtask  call TaskMageSaveEnd()

