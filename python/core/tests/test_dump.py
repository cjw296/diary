from datetime import date
from pathlib import Path

from testfixtures import OutputCapture, TempDirectory, compare

from diary.dump import dump
from diary.objects import Period


class TestDump:
    def test_add_new_file(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            with OutputCapture() as output:
                dump(Path(td.path), period, dry_run=True)
            output_text = output.captured
            assert '   ADD:' in output_text
            assert '2023/01/15.txt' in output_text

    def test_add_new_file_creates_directories(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            dump(Path(td.path), period, dry_run=False)
            day_path = td / '2023' / '01' / '15.txt'
            assert day_path.exists()
            compare(day_path.read_text(), expected=str(period))

    def test_exists_with_same_content(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            day_path = td / '2023' / '01' / '15.txt'
            day_path.parent.mkdir(parents=True)
            day_path.write_text(str(period))

            with OutputCapture() as output:
                dump(Path(td.path), period, dry_run=False)
            output_text = output.captured
            assert 'EXISTS:' in output_text
            assert '2023/01/15.txt' in output_text

    def test_update_with_different_content(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            day_path = td / '2023' / '01' / '15.txt'
            day_path.parent.mkdir(parents=True)
            day_path.write_text('old content')

            with OutputCapture() as output:
                dump(Path(td.path), period, dry_run=False)

            output_text = output.captured
            assert 'UPDATE:' in output_text
            assert '2023/01/15.txt' in output_text
            assert 'existing' in output_text
            assert 'new' in output_text

            compare(day_path.read_text(), expected=str(period))

    def test_dry_run_does_not_write_files(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            dump(Path(td.path), period, dry_run=True)
            day_path = td / '2023' / '01' / '15.txt'
            assert not day_path.exists()

    def test_dry_run_does_not_update_files(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 1, 15))
            day_path = td / '2023' / '01' / '15.txt'
            day_path.parent.mkdir(parents=True)
            original_content = 'original content'
            day_path.write_text(original_content)

            dump(Path(td.path), period, dry_run=True)
            compare(day_path.read_text(), expected=original_content)

    def test_creates_nested_directories(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 12, 31))
            dump(Path(td.path), period, dry_run=False)

            year_dir = td / '2023'
            month_dir = year_dir / '12'
            day_file = month_dir / '31.txt'

            assert year_dir.exists()
            assert year_dir.is_dir()
            assert month_dir.exists()
            assert month_dir.is_dir()
            assert day_file.exists()
            assert day_file.is_file()

    def test_formats_month_with_leading_zero(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 3, 5))
            dump(Path(td.path), period, dry_run=False)
            day_path = td / '2023' / '03' / '05.txt'
            assert day_path.exists()

    def test_formats_day_with_leading_zero(self) -> None:
        with TempDirectory() as td:
            assert td.path is not None
            period = Period(date(2023, 11, 7))
            dump(Path(td.path), period, dry_run=False)
            day_path = td / '2023' / '11' / '07.txt'
            assert day_path.exists()
