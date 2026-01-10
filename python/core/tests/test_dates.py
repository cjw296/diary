from datetime import date

from testfixtures import Replace, ShouldRaise, compare, mock_date

from diary.dates import parse_date, previous_sunday


class TestPreviousSunday:
    def test_when_today_is_monday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 16, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_tuesday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 17, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_wednesday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 18, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_thursday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 19, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_friday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 20, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_saturday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 21, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))

    def test_when_today_is_sunday(self) -> None:
        with Replace('diary.dates.date', mock_date(2023, 1, 22, delta=0)):
            result = previous_sunday()
            compare(result, expected=date(2023, 1, 15))


class TestParseDate:
    def test_valid_date(self) -> None:
        result = parse_date('2023-01-15')
        compare(result, expected=date(2023, 1, 15))

    def test_another_valid_date(self) -> None:
        result = parse_date('2024-12-25')
        compare(result, expected=date(2024, 12, 25))

    def test_invalid_date_format(self) -> None:
        with ShouldRaise(ValueError):
            parse_date('01/15/2023')

    def test_invalid_date_string(self) -> None:
        with ShouldRaise(ValueError):
            parse_date('not-a-date')

    def test_empty_string(self) -> None:
        with ShouldRaise(ValueError):
            parse_date('')
