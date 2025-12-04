from datetime import date
from unittest.mock import Mock

import pytest
from testfixtures import (
    OutputCapture,
    Replace,
    Replacer,
    ShouldRaise,
    TempDirectory,
    compare,
    mock_datetime,
)

from diary.ingest import check_vm_time, ingest
from diary.objects import Period, Stuff, Type


class TestCheckVmTime:
    def test_vm_time_in_sync(self):
        mock_client = Mock()
        response = Mock()
        response.text = '2023-01-15T10:30:00\n'
        mock_client.get = Mock(return_value=response)

        with Replace('diary.ingest.datetime', mock_datetime(2023, 1, 15, 10, 30, 2, delta=0)):
            check_vm_time(mock_client)

        mock_client.get.assert_called_once_with('/vm_now')

    def test_vm_time_out_of_sync(self):
        mock_client = Mock()
        response = Mock()
        response.text = '2023-01-15T10:30:00\n'
        mock_client.get = Mock(return_value=response)

        with Replace('diary.ingest.datetime', mock_datetime(2023, 1, 15, 10, 31, 0, delta=0)):
            with ShouldRaise(
                RuntimeError(
                    'VM time is 2023-01-15 10:30:00 but local time is 2023-01-15 10:31:00 (0:01:00, please fix!'
                )
            ):
                check_vm_time(mock_client)


class TestIngest:
    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.zope = Mock()
        config.zope.list = Mock(return_value=[])
        config.dump = '~/test-dump'
        return config

    def test_ingest_basic_flow(self, mock_config):
        period1 = Period(date(2023, 1, 15))
        period1.stuff.append(Stuff(Type.did, 'First entry'))
        period2 = Period(date(2023, 1, 16))
        period2.stuff.append(Stuff(Type.did, 'Second entry'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period1) + '\n' + str(period2))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                mock_dump = Mock()
                r.replace('diary.ingest.dump', mock_dump)
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                with OutputCapture():
                    ingest(mock_config, trim=False, target=date(2023, 1, 16))

                compare(mock_dump.call_count, expected=2)
                mock_config.zope.add.assert_any_call(period1)
                mock_config.zope.add.assert_any_call(period2)

    def test_ingest_generates_future_dates(self, mock_config):
        period = Period(date(2023, 1, 15))
        period.stuff.append(Stuff(Type.did, 'Entry'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                r.replace('diary.ingest.dump', Mock())
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                ingest(mock_config, trim=False, target=date(2023, 1, 20))

            diary_content = diary_path.read_text()
            compare('(2023-01-16) Monday' in diary_content, expected=True)
            compare('(2023-01-17) Tuesday' in diary_content, expected=True)
            compare('(2023-01-18) Wednesday' in diary_content, expected=True)
            compare('(2023-01-19) Thursday' in diary_content, expected=True)
            compare('(2023-01-20) Friday' in diary_content, expected=True)

    def test_ingest_skips_empty_entries(self, mock_config):
        period1 = Period(date(2023, 1, 15))
        period2 = Period(date(2023, 1, 16))
        period2.stuff.append(Stuff(Type.did, 'Has content'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period1) + '\n' + str(period2))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                r.replace('diary.ingest.dump', Mock())
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                with OutputCapture() as output:
                    ingest(mock_config, trim=False, target=date(2023, 1, 16))

                compare(mock_config.zope.add.call_count, expected=1)

    def test_ingest_updates_existing_entry(self, mock_config):
        period = Period(date(2023, 1, 15))
        period.stuff.append(Stuff(Type.did, 'Updated entry'))

        existing_period = Period(date(2023, 1, 15))
        existing_period.zope_id = 'existing-123'
        mock_config.zope.list = Mock(return_value=[existing_period])

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                r.replace('diary.ingest.dump', Mock())
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                with OutputCapture():
                    ingest(mock_config, trim=False, target=date(2023, 1, 15))

                mock_config.zope.update.assert_called_once()
                updated_period = mock_config.zope.update.call_args[0][0]
                compare(updated_period.zope_id, expected='existing-123')

    def test_ingest_with_trim_true(self, mock_config):
        from datetime import timedelta
        from diary.dates import previous_sunday

        cutoff = previous_sunday()
        future_date = cutoff + timedelta(days=10)

        period = Period(future_date)
        period.stuff.append(Stuff(Type.did, 'Entry'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                r.replace('diary.ingest.dump', Mock())

                ingest(mock_config, trim=True, target=future_date)

            compare(mock_config.zope.add.call_count, expected=1)

    def test_ingest_dumps_all_periods(self, mock_config):
        period1 = Period(date(2023, 1, 15))
        period1.stuff.append(Stuff(Type.did, 'Entry 1'))
        period2 = Period(date(2023, 1, 16))
        period2.stuff.append(Stuff(Type.did, 'Entry 2'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period1) + '\n' + str(period2))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                mock_dump = Mock()
                r.replace('diary.ingest.dump', mock_dump)
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                ingest(mock_config, trim=False, target=date(2023, 1, 16))

            compare(mock_dump.call_count, expected=2)
            calls = mock_dump.call_args_list
            compare(calls[0][0][1], expected=period1)
            compare(calls[1][0][1], expected=period2)

    def test_ingest_uses_target_date_when_provided(self, mock_config):
        period = Period(date(2023, 1, 15))
        period.stuff.append(Stuff(Type.did, 'Entry'))

        with TempDirectory() as td:
            diary_path = td / 'diary.txt'
            diary_path.write_text(str(period))
            mock_config.diary_path = diary_path

            with Replacer() as r:
                r.replace('diary.ingest.check_vm_time', Mock())
                r.replace('diary.ingest.dump', Mock())
                r.replace('diary.ingest.previous_sunday', Mock(return_value=date(2023, 1, 1)))

                ingest(mock_config, trim=False, target=date(2023, 1, 18))

            diary_content = diary_path.read_text()
            compare('(2023-01-18) Wednesday' in diary_content, expected=True)
