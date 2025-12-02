import html
from datetime import date
from functools import partial
from pathlib import Path
from typing import Union

from diary.config import Config
from diary.dump import dump
from diary.objects import Period
from diary.zope import Client, LookBackFailed


def handle_error(e: Union[Exception, str], url: str, modified: date) -> bool:
    print()
    print(f'{url} at {modified:%a %d %b %y}:', type(e).__qualname__, e)
    print()
    return not isinstance(e, LookBackFailed)


def export(
    config: Config,
    start_url: str = '',
    start_date: date = date.max,
    dump_path: Path | None = None,
    dry_run: bool = False,
    quiet: bool = False,
) -> None:
    zope: Client = config.zope

    previous = None
    for period in zope.list(date.min, handle_error, start_url, start_date):
        latest = period.end or period.start
        to_previous = previous and (previous - latest).days or None
        assert period.modified is not None
        to_modified = (period.modified - latest).days

        if not quiet:
            print(
                f'{period.human_date()} {period.start.year} ',
                f'prev: {to_previous} days',
                f'pub: {to_modified} days',
                f'python export.py --start-url {period.start_url} --start-date {period.start_date}',
            )

        error = partial(handle_error, url=f'{zope.url}/{period.zope_id}', modified=period.modified)

        if to_modified < -18:
            error(f'{to_modified} days to modified, gap too big!')
            break
        if not (to_previous is None or 1 <= to_previous <= 4):
            error(f'{to_previous} days to previous!')
            break

        edit_url = f'{zope.url}/{period.zope_id}/manage'
        if not quiet:
            print(edit_url)
            print()
        soup = zope.get_soup(edit_url, absolute=True)
        (summary_tag,) = soup.find_all('textarea', attrs={'name': 'summary'})
        (body_tag,) = soup.find_all('textarea', attrs={'name': 'body'})

        period = zope.add_stuff(
            period, html.unescape(summary_tag.text), body_tag.text, period.modified
        )

        if not quiet:
            print(period)

        if dump_path:
            dump(dump_path.expanduser(), period, dry_run)

        previous = period.start
