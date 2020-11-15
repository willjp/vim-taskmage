import datetime
import time
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


def parse_local_isodate(datestr):
    if not re.match(r'^\d...-\d.-\d.$', datestr):
        raise TypeError('invalid date format (YYYY-MM-DD). Received "{}"'.format(datestr))
    date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return datetime.datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=LocalTimezone())


class LocalTimezone(datetime.tzinfo):
    """
    Notes:
        copied from the official python docs.
    """
    std_offset = datetime.timedelta(seconds=-time.timezone)

    if time.daylight:
        dst_offset = datetime.timedelta(seconds=-time.altzone)
    else:
        dst_offset = std_offset

    dst_diff = dst_offset - std_offset
    zero = datetime.timedelta(0)

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.dst_offset
        else:
            return self.std_offset

    def dst(self, dt):
        if self._isdst(dt):
            return self.dst_diff
        else:
            return self.zero

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


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
