import re
import six
from taskmage2.utils import ctags


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
    pass


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
    def test(self):
        assert False
