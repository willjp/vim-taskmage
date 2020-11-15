import datetime
import mock
from taskmage2.utils import timezone


class Test_parse_utc_iso8610:
    def test_utc_date_succeeds(self):
        datestr = '2019-07-19T07:56:13.111111+00:00'
        dt = timezone.parse_utc_iso8601(datestr)
        expected_dt = datetime.datetime(2019, 7, 19, 7, 56, 13, 111111, tzinfo=timezone.UTC())
        assert dt == expected_dt


class Test_parse_local_isodate:
    def test_succeeds(self):
        dt = timezone.parse_local_isodate('2019-07-19')
        expected_dt = datetime.datetime(2019, 7, 19, 0, 0, 0, tzinfo=timezone.LocalTimezone())
        assert dt == expected_dt


class Test_timezones:
    def test_utc_offsets_differ(self):
        # NOTE: mocking non-dst UTC-offset in case someone (or a CI server)
        #       is using UTC as their timezone.
        mock_std_offset = mock.PropertyMock(return_value=datetime.timedelta(hours=-4))
        with mock.patch(
            'taskmage2.utils.timezone.LocalTimezone.std_offset',
            new_callable=mock_std_offset,
        ):
            utcnow = datetime.datetime.now(timezone.UTC())
            localnow = utcnow.astimezone(timezone.LocalTimezone())

            utc_offset = utcnow.utcoffset()
            local_offset = localnow.utcoffset()
            assert utc_offset != local_offset

    def test_time_arithmetric_works(self):
        utcnow = datetime.datetime.now(timezone.UTC())
        localnow = utcnow.astimezone(timezone.LocalTimezone())
        difference = localnow - utcnow
        assert difference == datetime.timedelta(seconds=0)
