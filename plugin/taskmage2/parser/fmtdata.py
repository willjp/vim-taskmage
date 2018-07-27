

class TaskList(object):
    statuses = {
        'x': 'done',
        '-': 'skip',
        'o': 'wip',
        '*': 'todo',
    }
    indent_lvl_chars = [
        '=', '-', '`', ':', '.', "'", '"', '~', '^', '_', '+'
    ]

    def statuschar(self, status):
        """
        Returns a status-char from a status.

        Returns:

            .. code-block:: python

                '*'

        """
        for char in self.statuses:
            if self.statuses[char] == status:
                return char

        raise KeyError('status does not exist: "{}"'.format(status))

    def status(self, char):
        """
        Returns a status from a statuschar

        Returns:

            .. code-block:: python

                'done'

        """
        return self.statuses[char]
