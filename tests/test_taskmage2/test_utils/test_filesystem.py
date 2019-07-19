from taskmage2.utils import filesystem


class Test_format_path(object):
    def test_ntpath(self):
        path = filesystem.format_path('C:\\Users\\vagrant')
        assert path == 'C:/Users/vagrant'

    def test_unix_root(self):
        path = filesystem.format_path('/')
        assert path == '/'

    def test_trailing_slash(self):
        path = filesystem.format_path('/usr/lib/')
        assert path == '/usr/lib'


class Test_walk_parents(object):
    def test_walk_parents(self):
        parents = list(filesystem.walk_parents('/usr/local/lib/libsomething'))
        assert parents == [
            '/usr/local/lib/libsomething',
            '/usr/local/lib',
            '/usr/local',
            '/usr',
            '/',
        ]

    def test_walk_parents(self):
        parents = list(filesystem.walk_parents('C:/Users/vagrant'))
        assert parents == [
            'C:/Users/vagrant',
            'C:/Users',
            'C:'
        ]
