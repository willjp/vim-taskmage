
let s:bufname = 'taskmage-search'


" TODO: syntax (show relative-path from taskmageproject (if exists))
" TODO: syntax (hide uuid)
" TODO: syntax color file differently from match


function! taskmage#searchbuffer#name()
    """ Get name of searchbuffer
    " Returns:
    "     str: name of taskmage's searchbuffer
    """
    return s:bufname
endfunction


function! taskmage#searchbuffer#bufnr()
    return bufnr(s:bufname)
endfunction


function! taskmage#searchbuffer#exists()
    """ Check if SearchBuffer already exists.
    " Returns:
    "   int: 0(false), 1(true)
    """
    let l:buffer_exists = bufname(s:bufname) != ''
    return l:buffer_exists
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
    if taskmage#searchbuffer#exists()
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

endfunction


function! taskmage#searchbuffer#close()
    """ Closes SearchBuffer (ignores if already closed)
    """
    if taskmage#searchbuffer#win_exists()
        let l:winnr = bufwinnr(s:bufname)
        exec printf(%s close', l:winnr)
    endif
    if taskmage#searchbuffer#exists()
        bdel s:bufname
    endif
endfunction


function! taskmage#searchbuffer#focus_window()
    exec printf('%d wincmd w', bufwinnr(s:bufname))
endfunction


function! taskmage#searchbuffer#clear()
    """ Clears SearchBuffer's contents
    """

    " remember previous windownr
    let l:created_temp_buffer = 0
    let l:prev_winnr = bufwinnr(expand('%'))

    " exit if not exists
    if !taskmage#searchbuffer#exists()
        return
    endif

    " if buffer exists, but not in window, show in
    " window so we can clear the buffer.
    if !taskmage#searchbuffer#win_exists()
        exec printf('sp %s', s:bufname)
        let l:created_temp_buffer = 1
    endif

    " focus window, remove contents
    call taskmage#searchbuffer#focus_window()
    exec '0'
    exec printf('delete %d', line('$'))

    " close window, if we created a temp window
    if l:created_temp_buffer == 1
        close
    endif

    " restore previous windownr
    exec printf('%d wincmd w', l:prev_winnr)
endfunction


function! taskmage#searchbuffer#set_contents(lines)
    " remember prev window
    let l:prev_winnr = bufwinnr(expand('%'))

    " set new contents
    call taskmage#searchbuffer#open()
    call taskmage#searchbuffer#clear()
    call taskmage#searchbuffer#focus_window()
    call setline(1, a:lines)

    " restore prev window
    exec printf('%d wincmd w', l:prev_winnr)
endfunction


function! taskmage#searchbuffer#append_line(line)
    call taskmage#searchbuffer#focus_window()
    call setline(getline('.'), a:line)
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

    " return to previous window, and open searchresult
    :wincmd p
    let l:cmds = printf('edit +/{\\*%s\\*} %s', l:uuid, l:filepath)
    exec l:cmds
endfunction


