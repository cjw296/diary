import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Callable, Any, Optional

from bs4 import BeautifulSoup
from requests import Session, Response

from objects import Period
from parse import parse

DATE_FORMAT = '(%Y-%m-%d) %A'

DAY_PATTERN = r'(?:(\w+)\s+)?(\d{1,2})?(?:rd|th|st|nd)?(?: (\w+))?(?: (\d+))?'
DAY_RANGE_PATTERN = re.compile(rf'^{DAY_PATTERN}(?:\s*(?:-|to)\s*{DAY_PATTERN})?$')

MONTH_ALIASES = {'Sept': 'September'}


class LookBackFailed(ValueError):

    def __init__(self, possible: date, text: str):
        self.possible = possible
        self.text = text

    def __str__(self):
        return f"Looked back to {self.possible}, couldn't match {self.text}"


@dataclass
class Client:
    url: str
    username: str
    password: str

    def __post_init__(self):
        self.session: Session = Session()
        self.session.auth = (self.username, self.password)

    def request(self, method: str, uri: str, absolute=False, **kw):
        if not absolute:
            uri = self.url+uri
        result = getattr(self.session, method)(uri, **kw)
        result.raise_for_status()
        return result

    def get(self, uri: str, absolute: bool = False) -> Response:
        return self.request('get', uri, absolute)

    def get_soup(self, uri: str, absolute: bool = False) -> BeautifulSoup:
        return BeautifulSoup(self.get(uri, absolute).content, features="html.parser")

    def post(self, uri: str, data: dict[str, str]) -> Response:
        return self.request('post', uri, data=data)

    def _post_data(self, day) -> dict[str, str]:
        return {
            'title': day.title_date(),
            'author': '-',
            'summary': day.summary().encode('latin-1'),
            'encoding': 'Plain',
            'addPosting:method': ' Add ',
        }

    def add(self, day: Period):
        data = self._post_data(day)
        data['addPosting:method'] = ' Add '
        self.post('', data=data)

    def update(self, day: Period):
        assert day.zope_id
        data = self._post_data(day)
        data['edit:method'] = 'Change'
        self.post(f'/{day.zope_id}', data=data)

    @staticmethod
    def lookback(
            start: date,
            text: str,
            day_name: str,
            day_number_text: str,
            month_name: Optional[str],
            year_text:  Optional[str],
            *,
            max_days: int
    ):
        day_number = int(day_number_text)
        for i in range(max_days):
            possible = start - timedelta(days=i)
            if possible.day == day_number:
                break
        else:
            raise LookBackFailed(possible, text) from None
        if day_name:
            possible_day_names = possible.strftime('%A'), possible.strftime('%a')
            if day_name not in possible_day_names:
                raise AssertionError(
                    f'{possible} was a {possible_day_names[0]}, but entry had {day_name}'
                )
        if month_name:
            month_name = MONTH_ALIASES.get(month_name, month_name)
            possible_month_names = possible.strftime('%B'), possible.strftime('%b')
            if month_name not in possible_month_names:
                raise AssertionError(
                    f'{possible} was in {possible_month_names[0]}, but entry had {month_name}'
                )
        if year_text:
            possible_year = possible.strftime('%Y')
            if year_text != possible_year:
                raise AssertionError(
                    f'{possible} was in {possible_year}, but entry had {year_text}'
                )
        return possible

    @classmethod
    def infer_date(cls, text: str, previous: date = None):
        text = text.strip()
        try:
            inferred = datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            match = DAY_RANGE_PATTERN.match(text)
            if not match:
                if text in calendar.day_name:
                    for i in range(1, 5):
                        possible = previous - timedelta(days=i)
                        if possible.strftime('%A') == text:
                            return possible, None
                raise ValueError(f'Bad format: {text!r}')
            name, day, month, year, end_name, end_day, end_month, end_year = match.groups()
            if end_day:
                end = cls.lookback(previous, text, end_name, end_day, end_month, end_year,
                                   max_days=5)
                if day and month and year:
                    start = datetime.strptime(f'{day} {month} {year}', '%d %b %Y').date()
                else:
                    start = cls.lookback(end, text, name, day, month, year,
                                         max_days=25)
                return start, end
            else:
                inferred = cls.lookback(previous, text, name, day, month, year,
                                        max_days=5)
        else:
            formatted = inferred.strftime(DATE_FORMAT)
            assert formatted == text, f'{inferred:%d %b %y} was a {inferred:%A}, got: {text}'
        return inferred, None

    def list(
            self, earliest: date,
            handle_error: Callable[[Exception, str, date], bool] = lambda e: False,
            next_url: str = '', seen: date = date.max,
    ) -> Iterable[Period]:
        while earliest < seen:
            soup = self.get_soup(next_url)
            start_date = seen
            for tag in soup.find_all('a', attrs={'name': True}):
                date_tag = tag.find_next('strong')
                read_url = date_tag.find_next('a', attrs={'class': 'read'})['href']
                zope_id = read_url.rsplit('/', 1)[-1]
                modified = datetime.strptime(tag['name'], '%Y-%m-%dT%H:%M:%SZ')
                try:
                    start, end = self.infer_date(date_tag.text, seen)
                except Exception as e:
                    if handle_error(e, read_url, modified):
                        continue
                    else:
                        raise
                seen = start
                if start < earliest:
                    break
                yield Period(
                    start,
                    end=end,
                    zope_id=zope_id,
                    start_url=next_url,
                    start_date=start_date,
                    modified=modified.date()
                )

            next_link = soup.html.find_next('a', attrs={'class': 'next'})
            if next_link is None:
                return
            next_url = next_link['href']

    @staticmethod
    def add_stuff(period: Period, summary: str, body: str) -> Period:
        assert not body.strip(), repr(body)
        # remove leading and trailing whitespace
        summary = summary.strip()
        # remove trailing whitespace
        summary = re.sub(r'\s+$', '', summary, flags=re.MULTILINE)
        # remove blank lines
        summary = summary.replace('\n\n', '\n')
        # any initial text becomes an event:
        if not re.match('^[A-Z]+ ', summary):
            summary = 'EVENT '+summary
        source = str(period)+summary+'\n'
        try:
            return parse(source)[0]
        except Exception as e:
            line = getattr(e, 'line', None)
            if line is None:
                raise
            before = '\n'.join(source.split('\n')[:line])
            pointer = ' '*(e.column-1)+'^'
            raise ValueError(f'\n{e}\n\n{before}\n{pointer}') from None
