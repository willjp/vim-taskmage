import datetime
import collections

from dateutil import tz


class _NodeData(tuple):
    """ A class prototype for custom namdetuples.

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
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())

    def touch(self):
        return FileData()

    def update(self, data):
        return FileData()


class SectionData(_NodeData):
    _attrs = tuple()

    def __new__(cls):
        return _NodeData.__new__(cls, tuple())

    def touch(self):
        return SectionData()

    def update(self, data):
        return SectionData()


class TaskData(_NodeData):
    _attrs = ('status', 'created', 'finished', 'modified')

    def __new__(cls, status, created=None, finished=False, modified=None):
        if finished is None:
            finished = False

        if status not in ('todo', 'skip', 'done', 'wip'):
            raise TypeError('status')

        if created is not None:
            if not isinstance(created, datetime.datetime):
                raise TypeError('created')
            elif not created.tzinfo:
                raise TypeError('created')

        if finished is not False:
            if not isinstance(finished, datetime.datetime):
                raise TypeError('finished')
            elif not finished.tzinfo:
                raise TypeError('finished')

        if modified is not None:
            if not isinstance(modified, datetime.datetime):
                raise TypeError('modified')
            elif not modified.tzinfo:
                raise TypeError('modified')

        return _NodeData.__new__(cls, (status, created, finished, modified))

    def touch(self):
        utcnow = datetime.datetime.now(tz.UTC)
        new_data = self.as_dict()

        new_data['modified'] = utcnow

        # assign defaults
        if self.status is None:
            new_data['status'] = 'todo'

        if self.created is None:
            new_data['created'] = utcnow

        # update finished-time
        if all([
            self.status in ('done', 'skip'),
            self.finished is False,
        ]):
            new_data['finished'] = utcnow
        else:
            new_data['finished'] = False

        return TaskData(**new_data)

    def update(self, data):
        """ Return a new taskdata object with changes from another
        taskdata object merged on top of this one.
        """
        utcnow = datetime.datetime.now(tz.UTC)
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

