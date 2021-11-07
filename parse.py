from datetime import datetime

from lark import Lark, Transformer, Token

from objects import Day, Stuff, Type

with open('diary.lark') as grammar:
    parser = Lark(grammar)


class Diary(Transformer):

    def start(self, days):
        return days

    def date(self, children):
        date_, = children
        return datetime.strptime(date_.value, '%Y-%m-%d').date()

    def day_name(self, children):
        day_name_, = children
        return day_name_.value

    def date_line(self, children):
        date, token, day_name, _ = children
        date_day_name = date.strftime('%A')
        if date_day_name != day_name:
            raise AssertionError(
                f'line {token.line}: {date} is a {date_day_name}, but day given as {day_name}'
            )
        return date

    def body(self, children):
        _, _, *lines, _ = children
        return ''.join(lines).strip()

    def stuff(self, children):
        action, _, title, body = children
        if isinstance(body, Token):
            body = None
        return Stuff(Type(action.value), title.value, body)

    def day(self, children):
        date_, _, stuff, *_ = children
        return Day(date_, stuff.children)


def parse(text: str) -> list[Day]:
    tree = parser.parse(text)
    return Diary().transform(tree)
