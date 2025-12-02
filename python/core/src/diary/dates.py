from datetime import timedelta, date, datetime

SUNDAY = 6
DAY = timedelta(days=1)


def previous_sunday() -> date:
    current = date.today()
    current -= DAY
    while current.weekday() != SUNDAY:
        current -= DAY
    return current


def parse_date(text) -> date:
    return datetime.strptime(text, '%Y-%m-%d').date()
