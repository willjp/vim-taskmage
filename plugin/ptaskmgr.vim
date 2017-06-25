

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


" with bufreadpre, the current bufferpath is still correct
autocmd BufReadPre  *.ptaskdata  execute 'call ptaskmgr.vim_plugin.PtaskFile(' . expand('%:p') . ')'


