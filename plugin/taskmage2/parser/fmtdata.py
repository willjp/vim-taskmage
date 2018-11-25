

class TaskList(object):
    """ Stores methods for statuschar/status conversions.
    """
    # list of status-chars:status
    statuses = {
        'x': 'done',
        '-': 'skip',
        'o': 'wip',
        '*': 'todo',
    }

    # list of valid characters to underline sections/files
    indent_lvl_chars = [
        '=', '-', '`', ':', '.', "'", '"', '~', '^', '_', '+'
    ]

    @classmethod
    def statuschar(cls, status):
        """
        Returns a status-char from a status.

        Returns:

            .. code-block:: python

                '*'

        """
        for char in cls.statuses:
            if cls.statuses[char] == status:
                return char

        raise KeyError('status does not exist: "{}"'.format(status))

    @classmethod
    def status(cls, char):
        """
        Returns a status from a statuschar

        Returns:

            .. code-block:: python

                'done'

        """
        return cls.statuses[char]
