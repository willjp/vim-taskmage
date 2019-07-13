import os
import re
import six
import taskmage2
from taskmage2.utils import ctags

_taskmagedir = os.path.dirname(os.path.abspath(taskmage2.__file__))
_test_resources = os.path.abspath('{}/../tests/test_resources'.format(_taskmagedir))


class Test_get_header_regex:
    @classmethod
    def setup_class(self):
        self.regex = ctags.get_header_regex()

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


class Test_render_tagfile:
    def test(self):
        filepath = '{}/mixed_headers.tasklist'.format(_test_resources)
        tags = ctags.render_tagfile(filepath)
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
        assert tags == expects


class Test_find_header_matches:
    def test_finds_match(self):
        text = (
            '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
            '========='
        )
        matches = ctags.find_header_matches(text)
        assert len(matches) == 1

    def test_no_matches_returns_empty_list(self):
        text = ''
        matches = ctags.find_header_matches(text)
        assert matches == []

    def test_rejects_headers_without_underline_matching_title_length(self):
        text = (
            'My Header\n'
            '====='
        )
        matches = ctags.find_header_matches(text)
        assert matches == []


class Test_get_header_line_numbers:
    def test_obtains_first_match_lineno(self):
        text = (
            '* task A\n'
            '* task B\n'
            '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
            '========='
        )
        header_matches = ctags.find_header_matches(text)
        matches = self.find_header_matches(text, header_matches)
        assert len(matches) == 1
        assert matches[0].lineno == 3

    def test_obtains_second_match_lineno(self):
        text = (
            '* task A\n'
            '* task B\n'
            '{*8ED87AC2D52F4734BAFCB7BDAA923DA4*}My Header\n'
            '=========\n'
            '\n'
            '* subtask A\n'
            '* subtask B\n'
            '\n'
            'Header 2\n'
            '--------\n'
        )
        header_matches = ctags.find_header_matches(text)
        matches = self.find_header_matches(text, header_matches)
        assert len(matches) == 2
        assert matches[1].lineno == 9

    def find_header_matches(self, text, header_matches):
        fd = six.StringIO(text)
        fd.seek(0)
        numbered_matches = ctags.get_header_match_line_numbers(fd, header_matches)
        return numbered_matches


class Test_get_ctags_entry:
    def test_section(self):
        entry = ctags.get_ctags_entry(
            name='My Header',
            filepath='/path/to/todo.mtask',
            line_regex='/^My Header$/;"',
            ntype='',  # sections do not have a prefix
            lineno=5,
        )
        expected = 'My Header\t/path/to/todo.mtask\t/^My Header$/;"\ts\tline:5'
        assert entry == expected


