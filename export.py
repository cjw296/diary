import html
from argparse import ArgumentParser
from datetime import date
from functools import partial
from pathlib import Path
from testfixtures import diff
from typing import Union

from config import read_config
from dates import parse_date
from objects import Period
from zope import Client, LookBackFailed


def handle_error(e: Union[Exception, str], url: str, modified: date) -> bool:
    print()
    print(f'{url} at {modified:%a %d %b %y}:', type(e).__qualname__, e)
    print()
    return not isinstance(e, LookBackFailed)


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


def main():
    config = read_config()
    zope: Client = config.zope

    parser = ArgumentParser()
    parser.add_argument('--start-url', default='')
    parser.add_argument('--start-date', default=date.max, type=parse_date)
    parser.add_argument('--dump', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    try:
        previous = None
        for period in zope.list(date.min, handle_error, args.start_url, args.start_date):
            latest = period.end or period.start
            to_previous = previous and (previous - latest).days or None
            assert period.modified is not None
            to_modified = (period.modified - latest).days

            if not args.quiet:
                print(
                    f'{period.human_date()} {period.start.year} ',
                    f'prev: {to_previous} days',
                    f'pub: {to_modified} days',
                    f'python export.py '
                    f'--start-url {period.start_url} --start-date {period.start_date}',
                )

            error = partial(
                handle_error, url=f'{zope.url}/{period.zope_id}', modified=period.modified
            )

            if to_modified < -18:
                error(f'{to_modified} days to modified, gap too big!')
                break
            if not (to_previous is None or 1 <= to_previous <= 4):
                error(f'{to_previous} days to previous!')
                break

            edit_url = f'{zope.url}/{period.zope_id}/manage'
            if not args.quiet:
                print(edit_url)
                print()
            soup = zope.get_soup(edit_url, absolute=True)
            (summary_tag,) = soup.find_all('textarea', attrs={'name': 'summary'})
            (body_tag,) = soup.find_all('textarea', attrs={'name': 'body'})

            period = zope.add_stuff(
                period, html.unescape(summary_tag.text), body_tag.text, period.modified
            )

            if not args.quiet:
                print(period)

            if args.dump:
                dump(args.dump.expanduser(), period, args.dry_run)

            previous = period.start
    except KeyboardInterrupt:
        pass
    finally:
        print()


if __name__ == '__main__':
    main()
