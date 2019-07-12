#!/usr/bin/env python
import argparse
import os
import sys
_bindir = os.path.dirname(os.path.abspath(__file__))
_plugindir = os.path.abspath('{}/../plugin')
sys.path.insert(0, _plugindir)
from taskmage2.utils import ctags


# TODO: verify meaning of '--sro' flag. It appears to be necessary...


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

        rendered_tags = ctags.render_tagfile(args.target_file)
        if args.file == '-':
            sys.stdout.write(rendered_tags)
        else:
            with open(args.file, 'w') as fd:
                fd.write(rendered_tags)


if __name__ == '__main__':
    cli = CommandlineInterface()
    cli.parse_args()
