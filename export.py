import html
from argparse import ArgumentParser
from datetime import date
from functools import partial
from pathlib import Path
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


def dump(path: Path, period: Period):
    year = str(period.start.year)
    month = f'{period.start.month:02}'
    day = f'{period.start.day:02}.txt'
    container = path / year / month
    container.mkdir(exist_ok=True, parents=True)
    (container / day).write_text(str(period))


def main():
    config = read_config()
    zope: Client = config.zope

    parser = ArgumentParser()
    parser.add_argument('--start-url', default='')
    parser.add_argument('--start-date', default=date.max, type=parse_date)
    parser.add_argument('--dump', type=Path)
    args = parser.parse_args()

    try:
        previous = None
        for period in zope.list(date.min, handle_error, args.start_url, args.start_date):
            latest = period.end or period.start
            to_previous = previous and (previous - latest).days or None
            to_modified = (period.modified - latest).days

            print(f'{period.human_date()} {period.start.year} ',
                  f'prev: {to_previous} days',
                  f'pub: {to_modified} days',
                  f'python export.py '
                  f'--start-url {period.start_url} --start-date {period.start_date}')

            error = partial(handle_error,
                            url=f'{zope.url}/{period.zope_id}',
                            modified=period.modified)

            if to_modified < -18:
                error(f'{to_modified} days to modified, gap too big!')
                break
            if not (to_previous is None or 1 <= to_previous <= 4):
                error(f'{to_previous} days to previous!')
                break

            edit_url = f'{zope.url}/{period.zope_id}/manage'
            print(edit_url)
            print()
            soup = zope.get_soup(edit_url, absolute=True)
            summary_tag, = soup.find_all('textarea', attrs={'name': 'summary'})
            body_tag, = soup.find_all('textarea', attrs={'name': 'body'})

            period = zope.add_stuff(
                period, html.unescape(summary_tag.text), body_tag.text, period.modified
            )

            print(period)

            if args.dump:
                dump(args.dump.expanduser(), period)

            previous = period.start
    except KeyboardInterrupt:
        pass
    finally:
        print()


if __name__ == '__main__':
    main()
