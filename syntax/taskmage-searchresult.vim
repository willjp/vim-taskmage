" Vim syntax file
" Language:   taskmage folds/syntax highlighting
" Maintainer: Will Pittman <willjpittman@gmail.com>
" Website: 
" Latest Revision: 2019-07-19
"
"
" SearchResults may look like any of the following:
" =================================================
"    ||/path/to/file.mtask|9B3983A601264622975EFD14181A6539|(2019-01-01)| my task
"    ||/path/to/file.mtask|9B3983A601264622975EFD14181A6539|| my header
"
"
" syntax folding:
" ===============
"    UUIDs are hidden
"
" syntax colouring:
" =================
"    None
"


if exists("b:current_syntax")
  finish
endif


" Enable hiding text
set conceallevel=2
set concealcursor=vinc


" Matches
let s:file_regex = '||[^|]\+'
let s:uuid_regex = '\(||[^|]\+\)\@<=|[A-Z0-9]\{32\}'
let s:modified_regex = '\(||[^|]\+|[^|]\+\)\@<=|[^|]\+'

execute "syntax match taskmage_search_pipe '|' "
execute "syntax match taskmage_search_file  '" .    s:file_regex     ."'"
execute "syntax match taskmage_search_uuid  '" .    s:uuid_regex     ."' conceal"
execute "syntax match taskmage_search_modified '".  s:modified_regex ."'"


" Colours
let s:file_colour = 'green'
let s:modified_colour = 'blue'
let s:pipe_colour = 'magenta'

execute ' highlight taskmage_search_file      ctermfg='. s:file_colour     .' ctermbg=none cterm=bold'
execute ' highlight taskmage_search_pipe      ctermfg='. s:pipe_colour     .' ctermbg=none cterm=bold'
execute ' highlight taskmage_search_modified  ctermfg='. s:modified_colour .' ctermbg=none cterm=bold'


" Finish
let b:current_syntax = 'taskmage-searchresult'
