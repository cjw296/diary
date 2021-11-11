from argparse import ArgumentParser
from datetime import timedelta, date, datetime
from functools import partial
from typing import Union

from config import read_config
from zope import Client, LookBackFailed

SUNDAY = 6
DAY = timedelta(days=1)


def previous_sunday() -> date:
    current = date.today()
    current -= DAY
    while current.weekday() != SUNDAY:
        current -= DAY
    return current


def handle_error(e: Union[Exception, str], url: str, modified: date) -> bool:
    print()
    print(f'{url} at {modified:%a %d %b %y}:', type(e).__qualname__, e)
    print()
    return not isinstance(e, LookBackFailed)


def date_from_text(text: str):
    return datetime.strptime(text, '%Y-%m-%d').date()


def main():
    config = read_config()
    zope: Client = config.zope

    parser = ArgumentParser()
    parser.add_argument('--start-url', default='')
    parser.add_argument('--start-date', default=date.max, type=date_from_text)
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

            try:
                print(zope.add_stuff(period, summary_tag.text, body_tag.text))
            except:
                print(summary_tag)
                print(body_tag)
                raise

            previous = period.start
    except KeyboardInterrupt:
        pass
    finally:
        print()


if __name__ == '__main__':
    main()
