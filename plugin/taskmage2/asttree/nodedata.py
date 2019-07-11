""" Immutable Objects representing contents of "data" key of the various node types.

.. code-block:: javascript

    // A sample node of type task
    // (status, finished, modified, created all represented in TaskData() object)

    {
        "indent": 1,
        "name":  "Clean Kitchen",
        "parent": null,
        "type": "task"
        "data": {
            "status": "todo",
            "finished": false,
            "modified": "2019-07-11T13:59:14.690601-00:00",
            "created": "2019-07-11T13:59:14.690601-00:00"
        }
    }

"""
import datetime
import collections

from taskmage2.utils import timezone


class _NodeData(tuple):
    """ BaseClass for type-validated namdetuples.

    The attribute :py:attr:`_attrs` determines the
    namdetuple properties.

    Example:

        .. code-block:: python

            class TaskData(_NodeData):
                _attrs = ('status', 'created')

            status = TaskData(status='done', created=datetime.datetime(..))
            print(status.status)
            >>> 'done'

            print(status.created)
            >>> datetime.datetime(...)

    """
    def __new__(cls, data):
        if not isinstance(cls._attrs, tuple):
            raise RuntimeError(
                'Each `_NodeData` must have a `cls._attrs` attribute '
                'with a list of arguments in order'
            )
        if len(cls._attrs) != len(data):
            raise RuntimeError(
                'incorrect number of entries in `_NodeData`'
            )
        return tuple.__new__(cls, data)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(
                ['{}={}'.format(self._attrs[i], self[i]) for i in range(len(self._attrs))]
            )
        )

    def __getattr__(self, attr):
        if attr not in self._attrs:
            raise AttributeError('Attribute "{}" does not exist on object {}'.format(attr, self.__class__.__name__))
        return self[self._attrs.index(attr)]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('type of `other` does not match')
        for attr in self._attrs:
            if not getattr(self, attr) == getattr(other, attr):
                return False

        return True

    def as_dict(self):
        d = collections.OrderedDict()
        for i in range(len(self._attrs)):
            d[self._attrs[i]] = self[i]
        return d

    def copy(self, *args, **kwds):
        """
        Create a duplicate object of this type,
        optionally modifying it's arguments in the new
        object's constructor.

        Example:

            .. code-block:: python

                >>> class task(_NodeData):
                >>>     _attrs = ('status','finished')
                >>>     def __new__(cls, status, finished=False):
                >>>         return _NodeData.__new__(cls, (status,finished))

                >>> t = task('wip')
                task(status='wip', finished=False)

                >>> t.copy(finished=True)
                task(status='wip', finished=True)

        """
        new_kwds = list(self.as_dict().items())

        if args:
            new_kwds = new_kwds[len(args):]

        new_kwds = collections.OrderedDict(new_kwds)
        if kwds:
            new_kwds.update(kwds)

        return type(self)(*args, **new_kwds)

    def touch(self):
        """ Assigns default metadata to unassigned, updates modified-time.
        """
        raise NotImplementedError()

    def update(self, data):
        """ Creates a new nodedata object, with the merged contents of self, and the provided node-data.
        """
        raise NotImplementedError()


class FileData(_NodeData):
    """ Immutable Object "data" dict of a file node.
    """
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())

    def touch(self):
        return FileData()

    def update(self, data):
        return FileData()


class SectionData(_NodeData):
    """ Immutable Object "data" dict of a section node.
    """
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())

    def touch(self):
        return SectionData()

    def update(self, data):
        return SectionData()


class TaskData(_NodeData):
    """ Immutable Object "data" dict of a task node.
    Behaves like a namedtuple with type-validation.

    Examples:

        .. code-block:: python

            >>> TaskData(status='todo')
            Taskdata(status=todo, created=None, finished=False, modified=None)

            >>> from taskmage2.utils import timezone
            >>> created = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.UTC())
            >>> TaskData(status='todo', created=created)
            TaskData(status=todo, created=2018-01-01 00:00:00+00:00, finished=False, modified=None)

            >>> taskdata = TaskData(status='todo')
            >>> taskdata.status
            'todo'

    """
    _attrs = ('status', 'created', 'finished', 'modified')

    def __new__(cls, status, created=None, finished=False, modified=None):
        """ Constructor.

        Args:
            status (str): ``(ex: 'todo', 'skip', 'done', 'wip')``
                The current status of a task. Must be one of todo, skip, done, or wip.

            created (datetime, optional): ``(ex: datetime.datetime(2018, 1, 1, 0, 0, 0, taskmage2.utils.timezone.UTC())``
                A timezone-localized datetime object.

            finished (False, datetime, optional): ``(ex: False, datetime.datetime(2018, 1, 1, 0, 0, 0, taskmage2.utils.timezone.UTC())``
                False, or the a timezone-localized datetime object indicatin gwhen
                the task was completed.

            modified (None, datetime, optional): ``(ex: None, datetime.datetime(2018, 1, 1, 0, 0, 0, taskmage2.utils.timezone.UTC())``
                None, or the most recent time a task was modified.

        """
        # defaults
        if finished is None:
            finished = False

        # validation
        cls._validate_status_param(status)
        cls._validate_created_param(created)
        cls._validate_finished_param(finished)
        cls._validate_modified_param(modified)

        return _NodeData.__new__(cls, (status, created, finished, modified))

    @staticmethod
    def _validate_status_param(status):
        """ Status only accepts string with valid status
        """
        if status not in ('todo', 'skip', 'done', 'wip'):
            raise TypeError('`status` must be one of (todo, skip, done, or wip)')

    @staticmethod
    def _validate_created_param(created):
        """ Created can be None, or a timezone-localized datetime
        """
        if created is None:
            return

        if not isinstance(created, datetime.datetime):
            message = ('`created` expects a datetime object. '
                       'received {}').format(str(type(created)))
            raise TypeError(message)
        elif not created.tzinfo:
            message = ('`created` expects a timezone-localized datetime '
                       'object. received {}').format(str(type(created)))
            raise TypeError(message)

    @staticmethod
    def _validate_finished_param(finished):
        """ Finished can be False, or a timezone-localized datetime object.
        """
        if finished is False:
            return

        if not isinstance(finished, datetime.datetime):
            message = ('`finished` expects a datetime object. '
                       'received {}').format(str(type(finished)))
            raise TypeError(message)
        elif not finished.tzinfo:
            message = ('`finished` expects a timezone-localized datetime '
                       'object. received {}').format(str(type(finished)))
            raise TypeError(message)

    @staticmethod
    def _validate_modified_param(modified):
        """ Modified can be None, or a timezone-localized datetime object.
        """
        if modified is None:
            return

        if not isinstance(modified, datetime.datetime):
            raise TypeError('modified')
        elif not modified.tzinfo:
            raise TypeError('modified')

    def touch(self):
        """ Updates fields, updates modified date (even if no changes).
        """
        utcnow = datetime.datetime.now(timezone.UTC())
        new_data = self.as_dict()
        new_data['modified'] = utcnow
        new_data['created'] = self._get_updated_created_status(utcnow)
        new_data['finished'] = self._get_updated_finished_status(utcnow)

        return TaskData(**new_data)

    def _get_updated_created_status(self, utcnow):
        if self.created is None:
            return utcnow
        return self.created

    def _get_updated_finished_status(self, utcnow):
        # if the task is 'done' or 'skip' it is considered completed.
        # if the task is not marked as completed, set it's completion
        # time to the current time/date, otherwise return the existing
        # finished timestamp
        task_is_completed = self.status in ('done', 'skip')
        if task_is_completed:
            if self.finished is False:
                return utcnow
            else:
                return self.finished

        # the task is not finished. It either was never finished,
        # or it's status has been reverted. Clear the finished date.
        return False

    def update(self, data):
        """ Return a new taskdata object with changes from another
        taskdata object merged on top of this one.
        """
        utcnow = datetime.datetime.now(timezone.UTC())
        new_data = self.as_dict()

        # if no changes, nothing to do
        if all([
            self.status == data.status,
            (self.created == data.created or data.created is None),
            (self.finished == data.finished or data.finished is None),
            (self.modified == data.modified or data.modified is None),
        ]):
            return TaskData(**new_data)

        # modified is always now,
        new_data['modified'] = utcnow

        # status always correct on new obj
        new_data['status'] = data.status

        # created, if present, will always be correct on new data
        if data.created:
            new_data['created'] = data.created

        # if new data has a finished-status
        if data.status not in ('done', 'skip'):
            new_data['finished'] = False
        elif self.status in ('done', 'skip') and self.finished:
            new_data['finished'] = self.finished
        elif data.finished:
            new_data['finished'] = data.finished
        elif self.finished:
            new_data['finished'] = self.finished
        else:
            new_data['finished'] = utcnow

        return TaskData(**new_data)

