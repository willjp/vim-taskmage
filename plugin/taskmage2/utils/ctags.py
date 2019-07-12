import os
import sys
import re
import collections


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
    filepath = os.path.abspath(filepath)

    # get header
    ctags_header = (
        '!_TAG_FILE_ENCODING	utf-8\n'
        '!_TAG_FILE_FORMAT	2\n'
        '!_TAG_FILE_SORTED	1\n'
    )

    with open(filepath, 'r') as fd:
        file_contents = fd.read()
        header_matches = find_header_matches(file_contents)
        ctags_entries = get_header_ctags_entries(fd, filepath, header_matches)

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


def get_header_ctags_entries(fd, filepath, header_matches):
    ctags_entries = []
    # get line-numbers for sections
    fd.seek(0)
    lineno = 1  # ctags line nums  1-indexed
    for match in header_matches:
        while fd.tell() < match.match_start_pos:
            ch = fd.read(1)
            if ch == '\n':
                lineno += 1
        if not match.type:
            type_char = 's'
        elif match.type == 'file':
            raise NotImplementedError('todo')
        ctags_entry = get_ctags_entry(match.name, filepath, match.regex, type_char, lineno)
        ctags_entries.append(ctags_entry)
    return ctags_entries


def get_ctags_entry(name, filepath, line_regex, type_char, lineno, parents=None):
    if not parents:
        entry = '{}\t{}\t{}\t{}\tline:{}'.format(
            name, filepath, line_regex, type_char, lineno
        )
        return entry
    raise NotImplementedError('todo')


