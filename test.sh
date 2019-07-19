#!/usr/bin/bash

# get dependencies
test -d .test_deps || mkdir -p .test_deps
test -e .test_deps/vader.vim/.git || git clone https://github.com/junegunn/vader.vim .test_deps/vader.vim

# run tests
vim -Nu <(cat << EOF
filetype off
set rtp+=.test_deps/vader.vim
set rtp+=~/.vim/bundle/jellybeans.vim
set rtp+=.
filetype plugin indent on
syntax enable
colorscheme jellybeans
map <leader>q :q<CR>
EOF) +Vader tests/viml/*
