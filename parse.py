from datetime import datetime

from lark import Lark, Transformer, Token

from objects import Period, Stuff, text_to_type

with open('diary.lark') as grammar:
    parser = Lark(grammar, parser='lalr')


class Diary(Transformer):
    def start(self, days):
        return days

    def date(self, children):
        (date_,) = children
        return datetime.strptime(date_.value, '%Y-%m-%d').date()

    def day_name(self, children):
        (day_name_,) = children
        return day_name_.value

    def date_pair(self, children):
        date, token, day_name = children
        date_day_name = date.strftime('%A')
        if date_day_name != day_name:
            raise AssertionError(
                f'line {token.line}: {date} is a {date_day_name}, but day given as {day_name}'
            )
        return date

    def date_line(self, children):
        try:
            date, _ = children
        except ValueError:
            start, _, _, end, _ = children
            return start, end
        else:
            return date, None

    def body(self, children):
        _, *lines, _ = children
        return ''.join(lines).strip()

    def stuff(self, children):
        action, tags, _, title, body = children
        if isinstance(body, Token):
            body = None
        return Stuff(
            text_to_type(action.value),
            title.value,
            body,
            tags=[tag.value[1:] for tag in tags.children] or None,
        )

    def day(self, children):
        date_, _, stuff, *_ = children
        start, end = date_
        return Period(start, stuff.children, end=end)


def parse(text: str) -> list[Period]:
    tree = parser.parse(text)
    return Diary().transform(tree)
