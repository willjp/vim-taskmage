

let s:bufname = 'taskmage-search'
"       Name of the searchbuffer
" ex:   'taskmage-search'


let s:taskmage_postpopenfile_cmds_stack = {}
"       when user presses <Enter> on a line in the searchbuffer, 
"       a command is queued to run after that file has opened *AND* rendered
"       from .mtask to the .tasklist format. 
"
"       This prevents race-conditions between the rendering, and the queued
"       command.
"
" ex:   {abspath: [cmds, cmds, ...], ...}



function! taskmage#searchbuffer#name()
    """ Get name of searchbuffer
    " Returns:
    "     str: name of taskmage's searchbuffer
    """
    return s:bufname
endfunction


function! taskmage#searchbuffer#bufnr()
    """ Returns the buffer-number
    """
    return bufnr(s:bufname)
endfunction


function! taskmage#searchbuffer#win_exists()
    """ Check if SearchBuffer already exists.
    " Returns:
    "   int: 0(false), 1(true)
    """
    let l:win_exists = bufwinnr(s:bufname) >= 0
    return l:win_exists
endfunction


function! taskmage#searchbuffer#open()
    """ Create SearchBuffer (if not exists)
    """
    " exit early if buffer already exists
    if taskmage#searchbuffer#win_exists()
        return
    endif

    " create buffer/window
    exec printf('badd %s', s:bufname)
    exec printf('split %s', s:bufname)

    " buffer attributes
    setlocal buftype=nofile
    setlocal bufhidden=delete
    setlocal noswapfile

    " buffer key-mappings
    map <buffer> <Enter> :call taskmage#searchbuffer#open_searchresult()<CR>

    setlocal ft=taskmage-searchresult
endfunction


function! taskmage#searchbuffer#close()
    """ Closes SearchBuffer (ignores if already closed)
    """
    if taskmage#searchbuffer#win_exists()
        let l:winnr = bufwinnr(s:bufname)
        exec printf('%s close', l:winnr)
    endif
endfunction


function! taskmage#searchbuffer#focus_window()
    """ Focuses SearchBuffer Window.
    """
    exec printf('%d wincmd w', bufwinnr(s:bufname))
endfunction


function! taskmage#searchbuffer#clear()
    """ Clears SearchBuffer's contents
    """

    " if window does not exist, ignore.
    if !taskmage#searchbuffer#win_exists()
        return
    endif

    " remember previous windownr
    let l:prev_winnr = bufwinnr(expand('%'))

    " focus window, remove contents
    call taskmage#searchbuffer#focus_window()
    exec '0'
    exec printf('delete %d', line('$'))

    " restore previous window selection
    exec printf('%d wincmd w', l:prev_winnr)

endfunction


function! taskmage#searchbuffer#set_contents(lines)
    """ Opens SearchBuffer, sets contents, restores window-focus.
    """

    " remember prev window bufname
    " (bufwinnr is unreliable, changes)
    let l:prev_bufname = bufname('%')

    " set new contents
    call taskmage#searchbuffer#open()
    call taskmage#searchbuffer#clear()
    call taskmage#searchbuffer#focus_window()
    call setline(1, a:lines)

    " restore prev window
    exec printf('%d wincmd w', bufwinnr(l:prev_bufname))
endfunction


function! taskmage#searchbuffer#open_searchresult()
    """ Opens file referred to by current line.
    "
    " Notes:
    "     lineformatting:  ||{abspath-to-file}|{uuid}|{description}
    """

    " ignore if no window
    if !taskmage#searchbuffer#win_exists()
        return
    endif

    " ignore if search-buffer not focused
    if bufwinnr(s:bufname) != bufwinnr(expand('%'))
        return
    endif

    " NOTE: vim excludes empty strings in split!
    let l:line_parts = split(getline('.'), '|')

    " ignore if line does not match format
    if len(l:line_parts) < 3
        return
    endif

    " open file at UUID
    let l:filepath = l:line_parts[0]
    let l:uuid = l:line_parts[1]

    " return to previous window 
    :wincmd p

    " NOTE: cannot simply use ``:e +/match  file``, not even using `BufReadCmd`.
    "       Commands following ``call taskmage#searchbuffer#open_searchresult()``
    "       execute before the file-open finishes being handled.
    "
    "       prev command:
    "           exec printf('edit +/{\\*%s\\*} %s', l:uuid, l:filepath)

    exec printf('edit +/{\\*%s\\*} %s', l:uuid, l:filepath)

    " queue an open-regex line job, runs after file is opened/rendered to .tasklist
    "let l:cmds = printf('+/{\*%s\*}', l:uuid)
    "call taskmage#searchbuffer#put_postcmds(l:filepath, l:cmds)
    "exec 'edit ' . l:filepath

endfunction


function! taskmage#searchbuffer#put_postcmds(filepath, cmds)
    """ Queues a job to run after the file has opened
    """
    if !has_key(s:taskmage_postpopenfile_cmds_stack, a:filepath)
        let s:taskmage_postpopenfile_cmds_stack[a:filepath] = []
    endif
    call add(s:taskmage_postpopenfile_cmds_stack[a:filepath], a:cmds)
endfunction


function! taskmage#searchbuffer#pop_and_run_postcmds()
    """ If current file has a job queued, pops/runs the job at index 0.
    """
    let l:abspath = expand('%:p')
    if !has_key(s:taskmage_postpopenfile_cmds_stack, l:abspath)
        return
    endif

    let l:post_cmds = remove(s:taskmage_postpopenfile_cmds_stack[l:abspath], 0)
    exec l:post_cmds
endfunction


function! taskmage#searchbuffer#get_postcmds(filepath)
    let l:abspath = fnamemodify(a:filepath, ':p')
    if !has_key(s:taskmage_postpopenfile_cmds_stack, l:abspath)
        return []
    endif
    return deepcopy(s:taskmage_postpopenfile_cmds_stack[l:abspath])
endfunction


function! taskmage#searchbuffer#clear_postcmds()
    let s:taskmage_postpopenfile_cmds_stack = {}
endfunction


function! taskmage#searchbuffer#postcmds()
    return deepcopy(s:taskmage_postpopenfile_cmds_stack)
endfunction
