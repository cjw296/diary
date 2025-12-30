from datetime import date as Date, datetime
from importlib.resources import files
from typing import Any

from lark import Lark, Transformer, Token

from diary.objects import Period, Stuff, text_to_type

grammar = files('diary').joinpath('diary.lark').read_text()
parser = Lark(grammar, parser='lalr')


class Diary(Transformer):
    def start(self, days: list[Any]) -> list[Any]:
        return days

    def date(self, children: list[Any]) -> Date:
        (date_,) = children
        return datetime.strptime(date_.value, '%Y-%m-%d').date()

    def day_name(self, children: list[Any]) -> str:
        (day_name_,) = children
        return day_name_.value

    def date_pair(self, children: list[Any]) -> Date:
        date, token, day_name = children
        date_day_name = date.strftime('%A')
        if date_day_name != day_name:
            raise AssertionError(
                f'line {token.line}: {date} is a {date_day_name}, but day given as {day_name}'
            )
        return date

    def date_line(self, children: list[Any]) -> tuple[Date, Date | None]:
        try:
            date, _ = children
        except ValueError:
            start, _, _, end, _ = children
            return start, end
        else:
            return date, None

    def body(self, children: list[Any]) -> str:
        _, *lines, _ = children
        return ''.join(lines).strip()

    def stuff(self, children: list[Any]) -> Stuff:
        action, tags, _, title, body = children
        if isinstance(body, Token):
            body = None
        return Stuff(
            text_to_type(action.value),
            title.value,
            body,
            tags=[tag.value[1:] for tag in tags.children] or None,
        )

    def day(self, children: list[Any]) -> Period:
        date_, _, stuff, *_ = children
        start, end = date_
        return Period(start, stuff.children, end=end)


def parse(text: str) -> list[Period]:
    tree = parser.parse(text)
    return Diary().transform(tree)
