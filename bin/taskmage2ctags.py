#!/usr/bin/env python
import argparse
import os
import sys
import uuid
import re
import collections
_bindir = os.path.dirname(os.path.abspath(__file__))
_plugindir = os.path.abspath('{}/../plugin'.format(_bindir))
sys.path.insert(0, _plugindir)
from taskmage2.parser import iostream, parsers
from taskmage2.asttree import asttree, astnode, renderers


# TODO: incomplete we don't have a renderer for ctags yet
# TODO: verify meaning of '--sro' flag.


# reads the json file on disk


def render_tags_using_renderer(filepath, lexer_name):
    """ renders tags from the json-serialized format

    Args:
        lexer_name (str): ``(ex: 'mtask', 'tasklist', 'taskdetails')``
            name of the lexer to use to deserialized the file contents
    """
    # build AST that starts with the filepath we are reading from
    ast = asttree.AbstractSyntaxTree([
        astnode.Node(
            _id=uuid.uuid4().hex.upper(),
            ntype='file',
            name=filepath,
        )
    ])

    # if the file exists on disk, add the file's AST
    # as children of our 'file' Node
    if os.path.isfile(filepath):
        with open(filepath, 'r') as fd_py:
            fd = iostream.FileDescriptor(fd_py)
            file_ast = parsers.parse(fd, lexer_name)
            ast[0].children = file_ast

    # now render the tagfile contents
    tags = ast.render(renderers.Ctags)
    return tags


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
        #'^' + re.escape('{*') + '(?P<uuid>' + uuid_regex + ')' + re.escape('*}')   # {*FF128D3EF6044AE7B038BEFDF03555C0*}
        '^(' + re.escape('{*') + '(?P<uuid>' + uuid_regex + ')' + re.escape('*}') + ')?'   # {*FF128D3EF6044AE7B038BEFDF03555C0*}
        + '(?P<type>([a-z]+' + '(?=' + re.escape('::') + '))?)'                    # file::
        + '(?P<name>[^\n]+)[ \t]*$\n'                                              # My Section Name\n
        + '(?P<underline>' + underline_regex + '+)[ \t]*$'                         # ===============
    )
    return section_regex


def render_tags_using_regex(filepath):
    filepath = os.path.abspath(filepath)

    # get header
    ctags_header = (
        '!_TAG_FILE_ENCODING	utf-8\n'
        '!_TAG_FILE_FORMAT	2\n'
        '!_TAG_FILE_SORTED	1\n'
    )

    ctags_entries = []
    with open(filepath, 'r') as fd:

        # get sections
        matches = []
        section_match = collections.namedtuple('section_match', ['name', 'type', 'regex', 'match_start_pos'])
        regex = get_header_regex()

        fileconts = fd.read()

        for match in re.finditer(regex, fileconts, re.MULTILINE):
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

        # get line-numbers for sections
        fd.seek(0)
        lineno = 1  # ctags line nums  1-indexed
        for match in matches:
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

    rendered_tags = ctags_header + '\n'.join(ctags_entries)
    return rendered_tags


def get_ctags_entry(name, filepath, line_regex, type_char, lineno, parents=None):
    if not parents:
        entry = '{}\t{}\t{}\t{}\tline:{}'.format(
            name, filepath, line_regex, type_char, lineno
        )
        return entry
    raise NotImplementedError('todo')


class CommandlineInterface(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            'target_file',
        )
        self.parser.add_argument(
            '-f', '--file',
            default='tags'
        )
        self.parser.add_argument(
            '-l', '--lexer',
            default='mtask',
        )
        # ignored for now
        self.parser.add_argument(
            '--sro',
        )

    def parse_args(self):
        args = self.parser.parse_args()

        rendered_tags = render_tags_using_regex(args.target_file)
        if args.file == '-':
            sys.stdout.write(rendered_tags)
        else:
            with open(args.file, 'w') as fd:
                fd.write(rendered_tags)


if __name__ == '__main__':
    cli = CommandlineInterface()
    cli.parse_args()
