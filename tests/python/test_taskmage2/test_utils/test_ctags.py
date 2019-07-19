import os
import re
import six
import taskmage2
from taskmage2.utils import ctags

_taskmagedir = os.path.dirname(os.path.abspath(taskmage2.__file__))
_test_resources = os.path.abspath('{}/../tests/test_resources'.format(_taskmagedir))


class Test_CtagsFile:
    def test_read_from_file(self):
        filepath = '{}/mixed_headers.tasklist'.format(_test_resources)
        ctagsfile = ctags.CtagsFile()
        ctagsfile.load_file(filepath)
        render = ctagsfile.render()
        expects = (
            '!_TAG_FILE_ENCODING	utf-8\n'
            + '!_TAG_FILE_FORMAT	2\n'
            + '!_TAG_FILE_SORTED	1\n'
            + 'section 1\t{}\t/^section 1$/;"\ts\tline:5\n'.format(filepath)
            + 'section 1.a\t{}\t/^section 1.a$/;"\ts\tline:10\tsection:section 1\n'.format(filepath)
            + 'section 1.b\t{}\t/^section 1.b$/;"\ts\tline:15\tsection:section 1\n'.format(filepath)
            + 'section 2\t{}\t/^section 2$/;"\ts\tline:20\n'.format(filepath)
            + 'section 2.a\t{}\t/^section 2.a$/;"\ts\tline:23\tsection:section 2'.format(filepath)
        )
        assert render == expects


class Test_CtagsHeaderEntry:
    class Test_match_regex:
        @classmethod
        def setup_class(self):
            self.regex = ctags.CtagsHeaderEntry.match_regex()

        def test_no_headers_no_match(self):
            text = (
                '* task\n'
                '* {*5820C61E8A1B4293B0FBBEFC176917CF*}another task\n'
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match is None

        def test_matches_header_with_id(self):
            text = (
                '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group() == text

        def test_matches_header_without_id(self):
            text = (
                'My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group() == text

        def test_matches_header_with_type_and_id(self):
            text = (
                '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}file::My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group() == text

        def test_matches_header_with_type_without_id(self):
            text = (
                'file::My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group() == text

        def test_matches_multiple_headers(self):
            text = (
                'My Header\n'
                '========='
                '\n'
                'My Other Header\n'
                '---------------'
            )
            assert len(list(re.finditer(self.regex, text, re.MULTILINE))) == 2

        def test_extracts_name(self):
            text = (
                'My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('name') == 'My Header'

        def test_extracts_underline(self):
            text = (
                'My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('underline') == '========='

        def test_extracts_id_when_present(self):
            text = (
                '{*F89595A0D463456D9489A19736C5ABC0*}My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('uuid') == 'F89595A0D463456D9489A19736C5ABC0'

        def test_extracts_id_when_not_present(self):
            text = (
                'My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('uuid') is None

        def test_extracts_type_when_present(self):
            text = (
                'file::My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('type') == 'file'

        def test_extracts_type_when_not_present(self):
            text = (
                'My Header\n'
                '========='
            )
            match = re.search(self.regex, text, re.MULTILINE)
            assert match.group('type') == ''

    class Test__find_entries:
        def test_finds_match(self):
            text = (
                '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
                '========='
            )
            matches = ctags.CtagsHeaderEntry._find_entries(text)
            assert len(matches) == 1

        def test_no_matches_returns_empty_list(self):
            text = ''
            matches = ctags.CtagsHeaderEntry._find_entries(text)
            assert matches == []

        def test_rejects_headers_without_underline_matching_title_length(self):
            text = (
                'My Header\n'
                '====='
            )
            matches = ctags.CtagsHeaderEntry._find_entries(text)
            assert matches == []

    class Test__set_entries_lineno:
        def test_obtains_first_match_lineno(self):
            text = (
                '* task A\n'
                '* task B\n'
                '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
                '========='
            )
            entries = [
                ctags.CtagsHeaderEntry(
                    uuid_='8ED87AC2D52F4734BAFCB7BDAA923DA4',
                    name='My Header',
                    ntype='',  # section has no ntype
                    filepath='/path/file.tasklist',
                    start_pos=18,
                    uline_char='=',
                )
            ]
            ctags.CtagsHeaderEntry._set_entries_lineno(text, entries)
            assert len(entries) == 1
            assert entries[0].lineno == 3

        def test_obtains_second_match_lineno(self):
            text = (
                '* task A\n'
                '* task B\n'
                '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
                '=========\n'
                '\n'
                '* subtask A\n' # 86
                '* subtask B\n' # 98
                '\n'
                'Header 2\n'
                '--------\n'
            )
            entries = [
                ctags.CtagsHeaderEntry(
                    uuid_='8ED87AC2D52F4734BAFCB7BDAA923DA4',
                    name='My Header',
                    ntype='',  # section has no ntype
                    filepath='/path/file.tasklist',
                    start_pos=18,
                    uline_char='=',
                ),
                ctags.CtagsHeaderEntry(
                    name='Header 2',
                    ntype='',  # section has no ntype
                    filepath='/path/file.tasklist',
                    start_pos=100,
                    uline_char='-',
                )
            ]
            ctags.CtagsHeaderEntry._set_entries_lineno(text, entries)
            assert len(entries) == 2
            assert entries[1].lineno == 9

    class Test_render:
        def test_section(self):
            entry = ctags.CtagsHeaderEntry(
                name='My Header',
                filepath='/path/to/todo.mtask',
                ntype='',  # sections do not have a prefix
                lineno=5,
            )
            render = entry.render()
            expected = 'My Header\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:5'
            assert render == expected


