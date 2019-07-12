#!/usr/bin/env python

import argparse
import sys

# proof-of-concept that I can make tags
#
# output is hard-coded
#
# generates fake tags file for 'examples/sample_tasks.mtask'


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

        file_contents = (
            '!_TAG_FILE_ENCODING	utf-8\n'
            '!_TAG_FILE_FORMAT	2\n'
            '!_TAG_FILE_SORTED	1\n'
            # section
            'home\texamples/sample_tasks.mtask\t/^{*F92370418E074C0B9665937C1DFE8AF6*}home$/;"\ts\tline:4\n'
            # nested section
            'kitchen\texamples/sample_tasks.mtask\t/^{*0982509FBE9B45E99BE8696A7880A8B0*}kitchen$/;"\ts\tline:8\tsection:home\n'
        )
        if args.file == '-':
            sys.stdout.write(file_contents)
        else:
            with open(args.file, 'w') as fd:
                fd.write(file_contents)


if __name__ == '__main__':
    cli = CommandlineInterface()
    cli.parse_args()
