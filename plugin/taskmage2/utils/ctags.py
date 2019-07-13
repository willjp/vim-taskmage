import os
import re

import six

from taskmage2.vendor.six.moves import UserList


class CtagsFile(UserList):
    def __init__(self, data=None):
        if data is None:
            data = []
        super(CtagsFile, self).__init__(data)
        self.data = data

    def load_file(self, filepath):
        """ Load ctag entries from the contents of a file (in tasklist format- restructuredtext).

        Args:
            filepath (str):
                path to a file
        """
        with open(filepath, 'r') as fd:
            contents = fd.read()
        self.load_text(contents, filepath)

    def load_text(self, text, filepath=None):
        """ Finds CtagEntries within text.

        Args:
            text (str):
                Taskmage Tasks in tasklist format. (ReStructuredText-inspired)
        """
        self.data = []
        self.data.extend(CtagsHeaderEntry.find_entries(text, filepath))
        # ... other entry types...

    def render(self):
        """ Renders the current entries within this CtagsFile instance.

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
        ctags_header = (
            '!_TAG_FILE_ENCODING	utf-8\n'
            '!_TAG_FILE_FORMAT	2\n'
            '!_TAG_FILE_SORTED	1\n'
        )
        entries_str = '\n'.join([e.render() for e in self.data])
        render = ctags_header + entries_str
        return render


class CtagsEntry(object):
    """ Interface for CtagsHeaderEntries
    """
    @property
    def entry_regex(self):
        raise NotImplementedError()

    @classmethod
    def find_entries(cls, text, filepath=None):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()


class CtagsHeaderEntry(CtagsEntry):
    def __init__(self, uuid_=None, name=None, ntype=None, filepath=None, start_pos=None, uline_char=None, lineno=None, parents=None):
        if parents is None:
            parents = []
        if filepath is None:
            filepath = 'none'

        self.uuid = uuid_
        self.name = name
        self.ntype = ntype
        self.filepath = filepath
        self.start_pos = start_pos
        self.uline_char = uline_char
        self.lineno = lineno
        self.parents = parents

    def render(self):
        """ Renders this instance as a ctags-entry line.

        Returns:
            str: ``'My Header\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:5'``
        """
        # NOTE: for now, we'll treat all nodetypes as sections.
        #       later, check 'self.ntype'
        type_char = 's'

        entry = '{}\t{}\t{}\t{}\tline:{}'.format(
            self.name, self.filepath, self.entry_regex, type_char, self.lineno
        )
        if not self.parents:
            return entry

        entry += '\tsection:{}'.format('|'.join(self.parents))
        return entry

    @property
    def entry_regex(self):
        r""" Ctags Entry regex for line (as written in the `tags` file)

        Returns:
            str: ``'/^\{\*[A-Z0-9]{32}\*\}name of section$/;'``
        """
        if not self.uuid:
            line_regex = '/^' + self.name + '$/;"'
            return line_regex

        line_regex = (
            '/^'
            + re.escape('{*')
            + self.uuid
            + re.escape('*}')
            + self.name
            + '$/;"'
        )
        return line_regex

    @staticmethod
    def match_regex():
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

    @classmethod
    def find_entries(cls, text, filepath=None):
        """ Extracts a list of :py:obj:`CtagsHeaderEntry` objects from text in the tasklist format
        (ReStructuredText inspired).

        Returns:
            CtagsFile:
                list of CtagsHeaderEntries.

                .. code-block:: python

                    [CtagsHeaderEntry(...), CtagsHeaderEntry(...), ...]

        """
        entries = cls._find_entries(text)
        cls._set_entries_lineno(text, entries)
        cls._set_entries_parents(entries)
        cls._set_entries_filepath(entries, filepath)

        return entries

    @classmethod
    def _find_entries(cls, text):
        r""" Finds headers in a taskmage tasklist (rst-inspired).

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

                    [CtagsHeaderEntry(...), CtagsHeaderEntry(...), ...]

        """
        # get sections
        ctags_entries = []
        regex = cls.match_regex()

        for match in re.finditer(regex, text, re.MULTILINE):
            if len(match.group('name')) <= len(match.group('underline')):
                entry = CtagsHeaderEntry(
                    uuid_=match.group('uuid'),
                    name=match.group('name'),
                    ntype=match.group('type'),
                    start_pos=match.start(),
                    uline_char=match.group('underline')[0]
                )
                ctags_entries.append(entry)
        return ctags_entries

    @classmethod
    def _set_entries_lineno(cls, text, ctag_entries):
        """ Adds line-numbers to :py:obj:`CtagsHeaderEntry` objects given a list of
        entries in the order they occurred, and the text they were obtained from.

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

            ctag_entries (list):
                List of :py:obj:`CtagsHeaderEntry` objects

        """
        fd = six.StringIO(text)
        fd.seek(0)

        # get line-numbers for sections
        lineno = 1  # ctags line nums  1-indexed
        for entry in ctag_entries:
            while fd.tell() < entry.start_pos:
                ch = fd.read(1)
                if ch == '\n':
                    lineno += 1
            entry.lineno = lineno

    @classmethod
    def _set_entries_parents(cls, ctag_entries):
        # keep track of parents
        ch_stack = {}  # {'=': {'name':'My Header', 'indent': 0}, '-': {'name': 'SubHeader', 'indent': 1}}
        for entry in ctag_entries:
            u_ch = entry.uline_char
            if u_ch in ch_stack:
                indent = ch_stack[u_ch]['indent']
                [ch_stack.pop(k) for k in list(ch_stack.keys()) if ch_stack[k]['indent'] >= indent]
            else:
                indent = len(ch_stack)

            # get list of parent names, in order of indent
            parent_info = [(ch_stack[k]['name'], ch_stack[k]['indent']) for k in ch_stack]
            parent_info.sort(key=lambda x: x[1])
            parents = [p[0] for p in parent_info]

            # assign parents
            entry.parents = parents

            # add this section as a parent
            ch_stack[u_ch] = {'name': entry.name, 'indent': indent}

    @classmethod
    def _set_entries_filepath(cls, ctag_entries, filepath):
        if filepath:
            filepath = os.path.abspath(filepath)
        else:
            filepath = 'none'

        filepath = os.path.abspath(filepath)
        for entry in ctag_entries:
            entry.filepath = filepath


