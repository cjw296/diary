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

    def __str__(self):
        header = self.date.strftime('(%Y-%m-%d) %A')
        parts = [header, '='*len(header)]
        parts.extend(str(s) for s in self.stuff)
        parts.append('')
        return '\n'.join(parts)
