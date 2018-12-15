import datetime
import re


def parse_utc_iso8601(datestr):
    if not datestr.endswith('+00:00'):
        raise RuntimeError('datestr is not localized to UTC')

    microseconds = re.search('(?<=\\.)[0-9]+(?=\\+00:00$)', datestr)
    if microseconds:
        dt = datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f+00:00')
    else:
        dt = datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S+00:00')

    # localize as UTC
    dt = datetime.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        tzinfo=UTC(),
    )
    return dt


class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def fromutc(self, dt):
        return dt

    def __eq__(self, tzinfo):
        if tzinfo.__class__ == self.__class__:
            return True
        return False
