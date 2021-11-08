from dataclasses import dataclass
from datetime import date
from enum import Enum


class Type(Enum):
    event = 'EVENT'
    did = 'DID'
    cancelled = 'CANCELLED'
    postponed = 'POSTPONED'


@dataclass
class Stuff:
    type: Type
    title: str
    body: str = None

    def __str__(self):
        text = f'{self.type.value} {self.title.strip()}'
        if self.body:
            body = self.body if self.body.endswith('\n') else self.body+'\n'
            text += f':\n--\n{body}--'
        return text


@dataclass
class Day:
    date: date
    stuff: list[Stuff] = ()
    zope_id: str = None

    def human_date(self):
        return self.date.strftime('%a %d %b')

    def title_date(self):
        return self.date.strftime('(%Y-%m-%d) %A')

    def summary(self):
        return '\n'.join(str(s) for s in self.stuff)

    def __str__(self):
        header = self.title_date()
        parts = [header, '='*len(header)]
        summary = self.summary()
        if summary:
            parts.append(summary)
        parts.append('')
        return '\n'.join(parts)
