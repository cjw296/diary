from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Optional


class Type(StrEnum):
    event = 'EVENT'
    did = 'DID'
    didnt = "DIDN'T"
    note = "NOTE"
    cancelled = 'CANCELLED'
    postponed = 'POSTPONED'


TYPE_SYNONYMS = {
    'ABANDONED': Type.cancelled,
    'ABANDONDED': Type.cancelled,
    'CANCEL': Type.cancelled,
    'CANCELED': Type.cancelled,
    'CANCELLD': Type.cancelled,
    'CANCELELD': Type.cancelled,
    'CANDELLED': Type.cancelled,
    'CANELLED': Type.cancelled,
    'CANNCELLED': Type.cancelled,
    'DDI': Type.did,
    'DD': Type.did,
    'DI': Type.did,
    'DITCHED': Type.cancelled,
    "DDN'T": Type.didnt,
    'DIDNT': Type.didnt,
    'EVEN': Type.event,
    'EVENTS': Type.event,
    'POPSTPONED': Type.postponed,
    'RESCHEDULED': Type.postponed,
    'SUSPENDED': Type.postponed,
}


def text_to_type(text: str) -> Type:
    try:
        return Type(text)
    except ValueError:
        type_ = TYPE_SYNONYMS.get(text)
        if type_ is None:
            raise
        return type_


@dataclass
class Stuff:
    type: Type
    title: str
    body: str = None
    tags: list[str] = None

    def __str__(self):
        tags = ''.join(f':{tag}' for tag in (self.tags or ()))
        text = f'{self.type.value}{tags} {self.title.strip()}'
        if self.body:
            body = self.body if self.body.endswith('\n') else self.body + '\n'
            text += f':\n--\n{body}--'
        return text


@dataclass
class Period:
    start: date
    stuff: list[Stuff] = ()
    end: Optional[date] = None
    zope_id: str = None
    start_url: str = None
    start_date: date = None
    modified: date = None

    def __post_init__(self):
        if self.start == self.end:
            self.end = None
        elif self.end and self.start > self.end:
            raise AssertionError(f'{self.start} > {self.end}')

    @property
    def date(self):
        assert self.end is None, str(self.end)
        return self.start

    def _date(self, format):
        text = self.start.strftime(format)
        if self.end:
            text += self.end.strftime(' to ' + format)
        return text

    def human_date(self):
        return self._date('%a %d %b')

    def title_date(self):
        return self._date('(%Y-%m-%d) %A')

    def summary(self):
        return '\n'.join(str(s) for s in self.stuff)

    def __str__(self):
        header = self.title_date()
        parts = [header, '=' * len(header)]
        summary = self.summary()
        if summary:
            parts.append(summary)
        parts.append('')
        return '\n'.join(parts)
