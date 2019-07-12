#!/usr/bin/env python
import argparse
import os
import sys
_bindir = os.path.dirname(os.path.abspath(__file__))
_plugindir = os.path.abspath('{}/../plugin'.format(_bindir))
sys.path.insert(0, _plugindir)
from taskmage2.parser import iostream, parsers
from taskmage2.asttree import asttree


# TODO: incomplete we don't have a renderer for ctags yet
# TODO: verify meaning of '--sro' flag.


# reads the json file on disk

def render_tags(filepath):
    # read file on disk
    if os.path.isfile(filepath):
        with open(filepath, 'r') as fd_py:
            fd = iostream.FileDescriptor(fd_py)
            ast = parsers.parse(fd, 'mtask')
    else:
        ast = asttree.AbstractSyntaxTree()

    tags = file_ast.render(renderers.Ctags)


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
        # ignored for now
        self.parser.add_argument(
            '--sro',
        )

    def parse_args(self):
        args = self.parser.parse_args()

        rendered_tags = render_tags(args.target_file)
        if args.file == '-':
            sys.stdout.write('\n'.join(rendered_tags))
        else:
            with open(args.file, 'w') as fd:
                fd.write('\n'.join(rendered_tags))


if __name__ == '__main__':
    cli = CommandlineInterface()
    cli.parse_args()
