#!/usr/bin/env python
import argparse
import os
import sys
import uuid
_bindir = os.path.dirname(os.path.abspath(__file__))
_plugindir = os.path.abspath('{}/../plugin'.format(_bindir))
sys.path.insert(0, _plugindir)
from taskmage2.parser import iostream, parsers
from taskmage2.asttree import asttree, astnode, renderers


# TODO: incomplete we don't have a renderer for ctags yet
# TODO: verify meaning of '--sro' flag.


# reads the json file on disk


def render_tags(filepath, lexer_name):
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

        rendered_tags = render_tags(args.target_file, args.lexer)
        if args.file == '-':
            sys.stdout.write('\n'.join(rendered_tags))
        else:
            with open(args.file, 'w') as fd:
                fd.write('\n'.join(rendered_tags))


if __name__ == '__main__':
    cli = CommandlineInterface()
    cli.parse_args()
