" Vim syntax file
" Language:   taskmage folds/syntax highlighting
" Maintainer: Will Pittman <willjpittman@gmail.com>
" Website:
" Latest Revision: 2017-06-11
"
"
" syntax folding:
" ===============
"   {*09042C43304F4B87927E9243470AF250*}    " UUIDs should be in all-caps
"                                           " (they will be hidden)
"
" syntax colouring:
" =================
"   * task to be done
"   - discarded task
"   x finished task
"   o started task
"   # any text following this char is a comment
"


if exists("b:current_syntax")
  finish
endif


"" use existing rst definition
:so $VIMRUNTIME/syntax/rst.vim





" Enable hiding text
set conceallevel=2
set concealcursor=vinc

" Define marker colours
let s:todo_colour     = 'magenta'
let s:skip_colour     = 'red'
let s:done_colour     = 'green'
let s:wip_colour      = '045'
let s:comment_colour  = '244'

let s:gui_todo_colour     = '#F57900'
let s:gui_skip_colour     = '#FF9D9D'
let s:gui_done_colour     = '#5FBA50'
let s:gui_wip_colour      = '#5CCEF4'
let s:gui_comment_colour  = '#7D7D7D'

let s:uuid_regex          = '{\*[A-Z0-9]\+\*}'
let s:todo_regex          = '\(^\s*\)\@<=\*\([a-zA-Z]\)\@!'
let s:skip_regex          = '\(^\s*\)\@<=-\([a-zA-Z]\)\@!'
let s:done_regex          = '\(^\s*\)\@<=x\([a-zA-Z]\)\@!'
let s:wip_regex           = '\(^\s*\)\@<=o\([a-zA-Z]\)\@!'
let s:comment_regex       = '#.*$'

" uuid without task-status, OR without a header-underline
let s:uuid_nostatus_regex = '' .
            \ '\([\*\-ox]\w*\)\@<!' .
            \ '{\*[A-Z0-9]\+\*}' .
            \ '\(.*\n[=\-`:\.\"~\^_+]\+\)\@!'


" unsaved entries will not have a UUID, but will be coloured
" as if they were the same as the existing entries
"
" ex:
"
"       - first task
"       -*{061050F029594620906982414B632F5F*} first task
"
"       (will both be coloured the same, and appear the same in the vim file)
"

execute "syntax match taskmage_uuid    '". s:uuid_regex          ."' conceal "
execute "syntax match taskmage_uuid    '". s:uuid_nostatus_regex ."' conceal cchar=E"
execute "syntax match taskmage_todo    '". s:todo_regex          ."'"
execute "syntax match taskmage_skip    '". s:skip_regex          ."'"
execute "syntax match taskmage_done    '". s:done_regex          ."'"
execute "syntax match taskmage_wip     '". s:wip_regex           ."'"
execute "syntax match taskmage_comment '". s:comment_regex       ."'"


execute ' highlight taskmage_todo     ctermfg='. s:todo_colour     .' guifg='. s:gui_todo_colour    .' ctermbg=none cterm=bold gui=bold'
execute ' highlight taskmage_skip     ctermfg='. s:skip_colour     .' guifg='. s:gui_skip_colour    .' ctermbg=none cterm=bold gui=bold'
execute ' highlight taskmage_done     ctermfg='. s:done_colour     .' guifg='. s:gui_done_colour    .' ctermbg=none cterm=bold gui=bold'
execute ' highlight taskmage_wip      ctermfg='. s:wip_colour      .' guifg='. s:gui_wip_colour     .' ctermbg=none cterm=bold gui=bold'
execute ' highlight taskmage_comment  ctermfg='. s:comment_colour  .' guifg='. s:gui_comment_colour .' ctermbg=none '


highlight Conceal ctermfg=221 ctermbg=095 cterm=bold


let b:current_syntax = "taskmage"

