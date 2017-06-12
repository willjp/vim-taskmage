" Vim syntax file
" Language:   ptaskmgr folds/syntax highlighting
" Maintainer: Will Pittman <willjpittman@gmail.com>
" Website: 
" Latest Revision: 2017-06-11
"
"
" syntax folding:
"   {*09042C43304F4B87927E9243470AF250*}    " UUIDs should be in all-caps
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
set conceallevel=2
set concealcursor=vinc

" Define marker colours
let s:nostatus_colour = 'red'
let s:todo_colour = 'magenta'
let s:skip_colour = 'red'
let s:done_colour = 'green'
let s:wip_colour  = '045'


let s:uuid_regex          = '{\*[A-Z0-9]\+\*}'
let s:uuid_nostatus_regex = '\([\*-ox]\w*\)\@<!{\*[A-Z0-9]\+\*}'
let s:todo_regex          = '\(^\s*\)\@<=\*\([a-zA-Z]\)\@!'
let s:skip_regex          = '\(^\s*\)\@<=-\([a-zA-Z]\)\@!'
let s:done_regex          = '\(^\s*\)\@<=x\([a-zA-Z]\)\@!'
let s:wip_regex           = '\(^\s*\)\@<=o\([a-zA-Z]\)\@!'


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

execute "syntax match ptaskmgr_uuid '". s:uuid_regex          ."' conceal "
execute "syntax match ptaskmgr_uuid '". s:uuid_nostatus_regex ."' conceal cchar=E"
execute "syntax match ptaskmgr_todo '". s:todo_regex          ."'"
execute "syntax match ptaskmgr_skip '". s:skip_regex          ."'"
execute "syntax match ptaskmgr_done '". s:done_regex          ."'"
execute "syntax match ptaskmgr_wip  '". s:wip_regex           ."'"


execute ' highlight ptaskmgr_todo     ctermfg='. s:todo_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_skip     ctermfg='. s:skip_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_done     ctermfg='. s:done_colour .' ctermbg=none cterm=bold'
execute ' highlight ptaskmgr_wip      ctermfg='. s:wip_colour  .' ctermbg=none cterm=bold'


highlight Conceal ctermfg=221 ctermbg=095 cterm=bold


let b:current_syntax = "ptaskmgr"

