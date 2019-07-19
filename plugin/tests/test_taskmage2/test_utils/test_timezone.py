import datetime
from taskmage2.utils import timezone


class Test_parse_utc_iso8610:
    def test_utc_date_succeeds(self):
        datestr = '2019-07-19T07:56:13.111111+00:00'
        dt = timezone.parse_utc_iso8601(datestr)
        expected_dt = datetime.datetime(2019, 7, 19, 7, 56, 13, 111111, tzinfo=timezone.UTC())
        assert dt == expected_dt


class Test_timezones:
    def test_time_arithmetric_works(self):
        utcnow = datetime.datetime.now(timezone.UTC())
        localnow = utcnow.astimezone(timezone.LocalTimezone())
        difference = localnow - utcnow
        assert utcnow.utcoffset() != localnow.utcoffset()
        assert difference == datetime.timedelta(seconds=0)
