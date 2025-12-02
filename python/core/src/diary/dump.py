from pathlib import Path

from testfixtures import diff

from diary.objects import Period


def dump(path: Path, period: Period, dry_run: bool):
    year = str(period.start.year)
    month = f'{period.start.month:02}'
    day = f'{period.start.day:02}.txt'
    day_path = path / year / month / day
    content = str(period)
    container = day_path.parent
    if day_path.exists():
        existing = day_path.read_text()
        if existing == content:
            print(f'EXISTS: {day_path}')
        else:
            print(f'UPDATE: {day_path}')
            print(diff(existing, content, x_label='existing', y_label='new'))
    else:
        print(f'   ADD: {day_path}')
    if not dry_run:
        container.mkdir(exist_ok=True, parents=True)
        day_path.write_text(content)
