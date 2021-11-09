from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from bs4 import BeautifulSoup
from requests import Session, Response

from objects import Period


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

    def get(self, uri: str) -> Response:
        return self.request('get', uri)

    def get_soup(self, uri: str) -> BeautifulSoup:
        return BeautifulSoup(self.get(uri).content, features="html.parser")

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

    def list(self, earliest: date) -> Iterable[Period]:
        seen: date = date.max
        next_url = ''

        while earliest < seen:
            soup = self.get_soup(next_url)
            for tag in soup.find_all('a', attrs={'name': True}):
                date_tag = tag.find_next('strong')
                read_url = date_tag.find_next('a', attrs={'class': 'read'})['href']
                post_date = datetime.strptime(date_tag.text, '(%Y-%m-%d) %A').date()
                modified = datetime.strptime(tag['name'], '%Y-%m-%dT%H:%M:%SZ')
                seen = post_date
                if post_date < earliest:
                    break
                yield Day(post_date, zope_id=read_url.rsplit('/', 1)[-1])

            next_url = soup.html.find_next('a', attrs={'class': 'next'})['href']
