" Vim syntax file
" Language: ptaskmgr folds/syntax highlighting
" Maintainer: Will Pittman <willjpittman@gmail.com>
" Website: 
" Latest Revision: 2017-06-11
"
"
" syntax folding:
"   {* 09042c43304f4b87927e9243470af250 *}
"
" syntax colouring:
"   * task to be done
"   - discarded task
"   x finished task
"   o started task
"

if exists("b:current_syntax")
  finish
endif


"" use existing rst definition
:so $VIMRUNTIME/syntax/rst.vim




" Enable hiding text
set conceallevel=1
set concealcursor=inc

" Define marker colours
let s:nostatus_colour = 'red'
let s:todo_colour = 'magenta'
let s:skip_colour = 'red'
let s:done_colour = 'green'
let s:wip_colour  = '045'

let s:nostatus_regex     = '\([^\*-xo].\)\@={\* [a-zA-Z0-9\-]\+ \*}'
let s:todo_regex         = '\(\(^\s*\)\@<=\*\([{}a-zA-Z]\)\@!\|\*{\* [a-zA-Z0-9\-]\+ \*}\)'
let s:skip_regex         = '\(\(^\s*\)\@<=-\([{a-zA-Z]\)\@!\|-{\* [a-zA-Z0-9\-]\+ \*}\)'
let s:done_regex         = '\(\(^\s*\)\@<=x\([{a-zA-Z]\)\@!\|x{\* [a-zA-Z0-9\-]\+ \*}\)'
let s:wip_regex          = '\(\(^\s*\)\@<=o\([{a-zA-Z]\)\@!\|o{\* [a-zA-Z0-9\-]\+ \*}\)'

let s:nostatus_regex_esc = '\\([^\\*-xo].\\)\\@={\\* [a-zA-Z0-9\\-]\\+ \\*}'
let s:todo_regex_esc     = '\\(\\(^\\s*\\)\\@<=\\*\\([{}a-zA-Z]\\)\\@!\\|\\*{\\* [a-zA-Z0-9\\-]\\+ \\*}\\)'
let s:skip_regex_esc     = '\\(\\(^\\s*\\)\\@<=-\\([{a-zA-Z]\\)\\@!\\|-{\\* [a-zA-Z0-9\\-]\\+ \\*}\\)'
let s:done_regex_esc     = '\\(\\(^\\s*\\)\\@<=x\\([{a-zA-Z]\\)\\@!\\|x{\\* [a-zA-Z0-9\\-]\\+ \\*}\\)'
let s:wip_regex_esc      = '\\(\\(^\\s*\\)\\@<=o\\([{a-zA-Z]\\)\\@!\\|o{\\* [a-zA-Z0-9\\-]\\+ \\*}\\)'





" unsaved entries will not have a UUID, but will be coloured
" as if they were the same as the existing entries
"
" ex:
"
"       - first task
"       -*{ 061050f029594620906982414b632f5f *} first task
"
"       (will both be coloured the same, and appear the same in the vim file)
"

execute  "syntax match ptaskmgr_nostatus '".    s:nostatus_regex ."'  conceal cchar=|"
execute  "syntax match ptaskmgr_todo     '".    s:todo_regex     ."'  conceal cchar=*"
execute  "syntax match ptaskmgr_skip     '".    s:skip_regex     ."'  conceal cchar=-"
execute  "syntax match ptaskmgr_done     '".    s:done_regex     ."'  conceal cchar=x"
execute  "syntax match ptaskmgr_wip      '".    s:wip_regex      ."'  conceal cchar=o"


execute ' highlight ptaskmgr_nostatus ctermfg=none ctermbg='. s:nostatus_colour .' cterm=bold'
execute ' highlight ptaskmgr_todo     ctermfg='. s:todo_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_skip     ctermfg='. s:skip_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_done     ctermfg='. s:done_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_wip      ctermfg='. s:wip_colour  .' ctermbg=none cterm=bold'



" setting Conceal cchar colour
" is done globally (not per match...)
"hi Conceal ctermfg='red' ctermbg=none cterm=bold



function! PTaskMgr_SetConcealColour()
    let line = getline('.')
    "if search(  s:todo_colour, line ) > 0
    if line=~s:todo_regex
        execute 'highlight Conceal  ctermfg=blue ctermbg=none cterm=bold'
    else
        execute 'highlight Conceal  ctermfg=magenta ctermbg=none cterm=bold'
    endif
endfunction


autocmd CursorMoved *.ptask  call PTaskMgr_SetConcealColour()


let b:current_syntax = "ptaskmgr"

