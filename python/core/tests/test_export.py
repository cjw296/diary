from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup
from testfixtures import OutputCapture, TempDirectory, compare

from diary.export import export, handle_error
from diary.objects import Period
from diary.zope import LookBackFailed


class TestHandleError:
    def test_with_regular_exception(self) -> None:
        with OutputCapture() as output:
            result = handle_error(
                ValueError('test error'), 'http://example.com/123', date(2023, 1, 15)
            )

        compare(result, expected=True)
        output_text = output.captured
        assert 'http://example.com/123' in output_text
        assert 'Sun 15 Jan 23' in output_text
        assert 'ValueError' in output_text
        assert 'test error' in output_text

    def test_with_lookback_failed(self) -> None:
        with OutputCapture() as output:
            result = handle_error(
                LookBackFailed(date(2023, 2, 15), 'lookback failed'),
                'http://example.com/456',
                date(2023, 2, 20),
            )

        compare(result, expected=False)
        output_text = output.captured
        assert 'http://example.com/456' in output_text
        assert 'Mon 20 Feb 23' in output_text
        assert 'LookBackFailed' in output_text

    def test_with_string_error(self) -> None:
        with OutputCapture() as output:
            result = handle_error(
                'string error message', 'http://example.com/789', date(2023, 3, 10)
            )

        compare(result, expected=True)
        output_text = output.captured
        assert 'http://example.com/789' in output_text
        assert 'Fri 10 Mar 23' in output_text


class TestExport:
    @pytest.fixture
    def mock_config(self) -> Mock:
        config = Mock()
        config.zope = Mock()
        config.zope.url = 'http://example.com'
        return config

    @pytest.fixture
    def sample_period(self) -> Period:
        period = Period(date(2023, 1, 15))
        period.zope_id = 'entry-123'
        period.modified = date(2023, 1, 16)
        period.start_url = 'http://start.url'
        period.start_date = date(2023, 1, 15)
        return period

    def test_export_quiet_mode(self, mock_config: Mock, sample_period: Period) -> None:
        mock_config.zope.list = Mock(return_value=[sample_period])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">Summary text</textarea>'
            '<textarea name="body">Body text</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=sample_period)

        with OutputCapture() as output:
            export(mock_config, quiet=True)

        compare(output.captured, expected='')
        mock_config.zope.list.assert_called_once()
        mock_config.zope.get_soup.assert_called_once()
        mock_config.zope.add_stuff.assert_called_once()

    def test_export_verbose_mode(self, mock_config: Mock, sample_period: Period) -> None:
        mock_config.zope.list = Mock(return_value=[sample_period])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">Summary text</textarea>'
            '<textarea name="body">Body text</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=sample_period)

        with OutputCapture() as output:
            export(mock_config, quiet=False)

        output_text = output.captured
        assert '(2023-01-15) Sunday' in output_text
        assert '2023' in output_text
        assert 'prev:' in output_text
        assert 'pub:' in output_text
        assert 'http://example.com/entry-123/manage' in output_text

    def test_export_with_dump_path(self, mock_config: Mock, sample_period: Period) -> None:
        mock_config.zope.list = Mock(return_value=[sample_period])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">Summary text</textarea>'
            '<textarea name="body">Body text</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=sample_period)

        with TempDirectory() as td:
            assert td.path is not None
            with OutputCapture():
                with patch('diary.export.dump') as mock_dump:
                    export(mock_config, dump_path=Path(td.path), dry_run=True, quiet=True)

            mock_dump.assert_called_once()
            call_args = mock_dump.call_args
            compare(call_args[0][1], expected=sample_period)
            compare(call_args[0][2], expected=True)

    def test_export_stops_on_gap_to_modified_too_large(
        self, mock_config: Mock, sample_period: Period
    ) -> None:
        sample_period.modified = date(2022, 12, 1)
        mock_config.zope.list = Mock(return_value=[sample_period])

        with OutputCapture() as output:
            export(mock_config, quiet=True)

        output_text = output.captured
        assert 'http://example.com/entry-123' in output_text
        assert 'gap too big!' in output_text

    def test_export_stops_on_gap_to_previous_invalid(self, mock_config: Mock) -> None:
        period1 = Period(date(2023, 1, 10))
        period1.zope_id = 'entry-1'
        period1.modified = date(2023, 1, 11)
        period1.start_url = 'http://start.url'
        period1.start_date = date(2023, 1, 10)

        period2 = Period(date(2023, 1, 15))
        period2.zope_id = 'entry-2'
        period2.modified = date(2023, 1, 16)
        period2.start_url = 'http://start.url'
        period2.start_date = date(2023, 1, 15)

        mock_config.zope.list = Mock(return_value=[period2, period1])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">Summary text</textarea>'
            '<textarea name="body">Body text</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=period2)

        with OutputCapture() as output:
            export(mock_config, quiet=True)

        output_text = output.captured
        assert 'http://example.com/entry-1' in output_text
        assert '5 days to previous!' in output_text

    def test_export_with_start_url_and_start_date(
        self, mock_config: Mock, sample_period: Period
    ) -> None:
        mock_config.zope.list = Mock(return_value=[sample_period])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">Summary text</textarea>'
            '<textarea name="body">Body text</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=sample_period)

        with OutputCapture():
            export(mock_config, start_url='http://start', start_date=date(2023, 1, 1), quiet=True)

        mock_config.zope.list.assert_called_once()
        call_args = mock_config.zope.list.call_args[0]
        compare(call_args[2], expected='http://start')
        compare(call_args[3], expected=date(2023, 1, 1))

    def test_export_calls_add_stuff_with_unescaped_html(
        self, mock_config: Mock, sample_period: Period
    ) -> None:
        mock_config.zope.list = Mock(return_value=[sample_period])

        mock_soup = BeautifulSoup(
            '<textarea name="summary">&lt;b&gt;Bold&lt;/b&gt;</textarea>'
            '<textarea name="body">Plain body</textarea>',
            'html.parser',
        )
        mock_config.zope.get_soup = Mock(return_value=mock_soup)
        mock_config.zope.add_stuff = Mock(return_value=sample_period)

        with OutputCapture():
            export(mock_config, quiet=True)

        mock_config.zope.add_stuff.assert_called_once()
        call_args = mock_config.zope.add_stuff.call_args[0]
        compare(call_args[1], expected='<b>Bold</b>')
        compare(call_args[2], expected='Plain body')
