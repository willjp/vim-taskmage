import os
import sys
import re
import collections


# TODO: this entire module is way to coupled.


def get_header_regex():
    """ Regex that will match ReStructuredText headers
    (regardless of whether they are section, file, or a different nodetype).

    Notes:
        identifies the following named groups

        ::

            {*B98D2124E2DA4DD19D6CEA0A787E3BB2*}file::My Awesome Title
            ================

            # matches
            uuid      = 'B98D2124E2DA4DD19D6CEA0A787E3BB2'   # may or may not be present
            type      = 'file'                               # not set for 'section' type, set for 'file' type
            name      = 'My Awesome Title'
            underline = '================'

    """
    underline_chars = ['=', '-', '`', ':', "'", '"', '~', '^', '_', '*', '+', '#', '<,' '>']
    uuid_regex = '[A-Z0-9]{32}'
    underline_regex = '[{}]'.format(''.join([re.escape(x) for x in underline_chars]))
    section_regex = (
        '^(' + re.escape('{*') + '(?P<uuid>' + uuid_regex + ')' + re.escape('*}') + ')?'   # {*FF128D3EF6044AE7B038BEFDF03555C0*}
        + '(?P<type>([a-z]+' + '(?=' + re.escape('::') + '))?)'                            # file::
        + '(?P<name>[^\n]+)[ \t]*$\n'                                                      # My Section Name\n
        + '(?P<underline>' + underline_regex + '+)[ \t]*$'                                 # ===============
    )
    return section_regex


def render_tagfile(filepath):
    """

    Args:
        filepath (str):
            filepath of a taskmage-tasklist file (restructuredtext-ish).

    Returns:
        str:
            the contents of a ctags `tags` file.

            ::

                !_TAG_FILE_ENCODING	utf-8
                !_TAG_FILE_FORMAT	2
                !_TAG_FILE_SORTED	1
                My Header\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:5
                My SubHeader\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:13\tsection:My Header|My SubHeader'

    """
    filepath = os.path.abspath(filepath)

    # get header
    ctags_header = (
        '!_TAG_FILE_ENCODING	utf-8\n'
        '!_TAG_FILE_FORMAT	2\n'
        '!_TAG_FILE_SORTED	1\n'
    )

    ctags_entries = []
    with open(filepath, 'r') as fd:
        file_contents = fd.read()
        header_matches = find_header_matches(file_contents)
        numbered_header_matches = get_header_match_line_numbers(fd, header_matches)

    for match in numbered_header_matches:
        ctags_entries.append(
            get_ctags_entry(match.name, filepath, match.regex, match.type, match.lineno)
        )

    rendered_tags = ctags_header + '\n'.join(ctags_entries)
    return rendered_tags


def find_header_matches(text):
    """ Finds headers in a taskmage tasklist (rst-inspired).

    Args:
        text (str):
            A TaskMage mtask file rendered as a tasklist file (restructuredtext-ish)

            .. code-block:: ReStructuredText

                All Todos
                =========

                {*679C2485E0E24B5687EEBB9D5AC3B7C1*}Saved Todos
                -----------

                * {*F05D37A337DF42448E7E229B35F3F021*} clean kitchen
                x wash dishes

    Returns:
        list:
            A list of named-tuples with matches

            .. code-block:: python

                [
                    section_match(name='All Todos', type='section', regex='/^...', match_start_pos=30),
                    ...
                ]

            ::

                name:             name of section
                type:             (section|file)
                regex:            '/^\{\*[A-Z0-9]{32}\*\}name of section$/;'   # ctagsfile regex entry
                match_start_pos:  30                                           # position of first character in match

    """
    # get sections
    matches = []
    section_match = collections.namedtuple('section_match', ['name', 'type', 'regex', 'match_start_pos'])
    regex = get_header_regex()

    for match in re.finditer(regex, text, re.MULTILINE):
        if len(match.group('name')) == len(match.group('underline')):
            uuid = match.group('uuid') or ''
            line_regex = (
                '/^'
                + uuid
                + match.group('name')
                + '$/;"'
            )
            matches.append(
                section_match(
                    name=match.group('name'),
                    type=match.group('type'),
                    regex=line_regex,
                    match_start_pos=match.start(),
                )
            )
    return matches


def get_header_match_line_numbers(fd, header_matches):
    """ Adds line-numbers to `header_matches`

    Notes:
        searches a file-descriptor for match-start-positions in `header_matches` ,
        keeping track of newlines .

    Args:
        fd (io.IOBase):
            file-descriptor that was used to obtain `header_matches`

        header_matches (list):
            Output of :py:func:`find_header_matches`

    Returns:
        list:
            Same output as :py:func:`find_header_matches` but with an additional `lineno` field.

            .. code-block:: python

                [
                    section_match(name='All Todos', type='section', regex='/^...', match_start_pos=30, lineno=5),
                    ...
                ]

    """
    numbered_header_matches = []
    numbered_section_match = collections.namedtuple('section_match_w_lineno', ['name', 'type', 'regex', 'match_start_pos', 'lineno'])

    # get line-numbers for sections
    fd.seek(0)
    lineno = 1  # ctags line nums  1-indexed
    for match in header_matches:
        while fd.tell() < match.match_start_pos:
            ch = fd.read(1)
            if ch == '\n':
                lineno += 1
        numbered_header_matches.append(
            numbered_section_match(
                name=match.name,
                type=match.type,
                regex=match.regex,
                match_start_pos=match.match_start_pos,
                lineno=lineno,
            )
        )
    return numbered_header_matches


def get_ctags_entry(name, filepath, line_regex, ntype, lineno, parents=None):
    """ Returns a ctags entry for the header.

    Returns:
        str: ``'My Header\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:5'``

    """
    # sections have no identifier (ex: 'file::My Header')
    if not ntype:
        type_char = 's'
    elif ntype == 'file':
        raise NotImplementedError('todo')

    if not parents:
        entry = '{}\t{}\t{}\t{}\tline:{}'.format(
            name, filepath, line_regex, type_char, lineno
        )
        return entry
    raise NotImplementedError('todo')


