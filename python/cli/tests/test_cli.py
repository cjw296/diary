from datetime import date
from pathlib import Path
from unittest.mock import Mock

from click.testing import CliRunner
from testfixtures import Replacer, compare

from diary_cli.cli import click_export, click_ingest, main


class TestMain:
    def test_main_group_invokes(self):
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        compare(result.exit_code, expected=0)
        compare('Usage:' in result.output, expected=True)


class TestExportCommand:
    def test_export_with_start_date(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_export = Mock()
            r.replace('diary_cli.cli.export', mock_export)

            result = runner.invoke(click_export, ['--start-date', '2023-01-15'])

            compare(result.exit_code, expected=0)
            call_args = mock_export.call_args
            compare(call_args[0][2], expected=date(2023, 1, 15))

    def test_export_with_all_options(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_export = Mock()
            r.replace('diary_cli.cli.export', mock_export)

            result = runner.invoke(
                click_export,
                [
                    '--start-url',
                    'http://example.com',
                    '--start-date',
                    '2023-01-15',
                    '--dump',
                    '/tmp/dump',
                    '--dry-run',
                    '--quiet',
                ],
            )

            compare(result.exit_code, expected=0)
            mock_export.assert_called_once()
            call_args = mock_export.call_args
            compare(call_args[0][1], expected='http://example.com')
            compare(call_args[0][2], expected=date(2023, 1, 15))
            compare(call_args[0][3], expected=Path('/tmp/dump'))
            compare(call_args[0][4], expected=True)
            compare(call_args[0][5], expected=True)


class TestIngestCommand:
    def test_ingest_with_defaults(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_ingest = Mock()
            r.replace('diary_cli.cli.ingest', mock_ingest)

            result = runner.invoke(click_ingest)

            compare(result.exit_code, expected=0)
            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args
            compare(call_args[0][1], expected=True)
            compare(call_args[0][2], expected=None)

    def test_ingest_with_no_trim(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_ingest = Mock()
            r.replace('diary_cli.cli.ingest', mock_ingest)

            result = runner.invoke(click_ingest, ['--no-trim'])

            compare(result.exit_code, expected=0)
            call_args = mock_ingest.call_args
            compare(call_args[0][1], expected=False)

    def test_ingest_with_target(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_ingest = Mock()
            r.replace('diary_cli.cli.ingest', mock_ingest)

            result = runner.invoke(click_ingest, ['--target', '2023-01-20'])

            compare(result.exit_code, expected=0)
            call_args = mock_ingest.call_args
            compare(call_args[0][2], expected=date(2023, 1, 20))

    def test_ingest_with_all_options(self):
        runner = CliRunner()
        with Replacer() as r:
            mock_config = Mock()
            r.replace('diary_cli.cli.read_config', Mock(return_value=mock_config))
            mock_ingest = Mock()
            r.replace('diary_cli.cli.ingest', mock_ingest)

            result = runner.invoke(click_ingest, ['--no-trim', '--target', '2023-01-20'])

            compare(result.exit_code, expected=0)
            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args
            compare(call_args[0][1], expected=False)
            compare(call_args[0][2], expected=date(2023, 1, 20))
