from datetime import date

from testfixtures import compare, ShouldRaise

from objects import Stuff, Type, Period


def test_only_start():
    day = Period(start=date(2020, 2, 1))
    compare(day.start, expected=date(2020, 2, 1))
    compare(day.end, expected=None)
    compare(day.date, expected=date(2020, 2, 1))


def test_start_and_end():
    day = Period(start=date(2020, 2, 1), end=date(2020, 2, 3))
    compare(day.start, expected=date(2020, 2, 1))
    compare(day.end, expected=date(2020, 2, 3))
    with ShouldRaise(AssertionError('2020-02-03')):
        day.date


def test_start_and_end_same():
    day = Period(start=date(2020, 2, 1), end=date(2020, 2, 1))
    compare(day.start, expected=date(2020, 2, 1))
    compare(day.end, expected=None)
    compare(day.date, expected=date(2020, 2, 1))


def test_start_greater_than_end():
    with ShouldRaise(AssertionError('2020-02-02 > 2020-02-01')):
        Period(start=date(2020, 2, 2), end=date(2020, 2, 1))


def test_stuff_str_minimal():
    compare(str(Stuff(Type('EVENT'), title='A thing')),
            expected='EVENT A thing')


def test_stuff_str_newlines_at_end():
    compare(str(Stuff(Type('EVENT'), title='A thing\n\n')),
            expected='EVENT A thing')


def test_stuff_str_maximal():
    compare(str(Stuff(Type.did,
                      title='A thing',
                      body='some body text\nmore lines',
                      tags=['tag1', 'tag2'])),
            expected='DID:tag1:tag2 A thing:\n--\nsome body text\nmore lines\n--')


def test_stuff_str_body_with_newline_at_end():
    compare(str(Stuff(Type.did, title='A thing', body='some body text\n')),
            expected='DID A thing:\n--\nsome body text\n--')


def test_day_empty():
    compare(str(Period(date(2020, 2, 1))), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
    ))


def test_start_and_end_serialized():
    compare(str(Period(date(2020, 2, 1), end=date(2020, 2, 3))), expected=(
        '(2020-02-01) Saturday to (2020-02-03) Monday\n'
        '============================================\n'
    ))


def test_day_single():
    compare(str(Period(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun')])), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
        'CANCELLED fun\n'
    ))


def test_day_single_with_body():
    compare(str(Period(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun', 'stuff\nthings')])), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
        'CANCELLED fun:\n'
        '--\n'
        'stuff\n'
        'things\n'
        '--\n'
    ))


def test_mixed():
    compare(str(Period(date(2020, 1, 1), [
        Stuff(Type.did, 'sleep'),
        Stuff(Type.cancelled, 'fun', body='bad\nthings\n'),
        Stuff(Type.event, 'a thing'),
        Stuff(Type.postponed, 'something else'),
    ])), expected=(
        '(2020-01-01) Wednesday\n'
        '======================\n'
        'DID sleep\n'
        'CANCELLED fun:\n'
        '--\n'
        'bad\n'
        'things\n'
        '--\n'
        'EVENT a thing\n'
        'POSTPONED something else\n'
    ))


def test_human_date_no_end():
    compare(Period(date(2020, 2, 1)).human_date(), expected='Sat 01 Feb')


def test_human_date_start_and_end_serialized():
    compare(
        Period(date(2020, 2, 1), end=date(2020, 2, 3)).human_date(),
        expected='Sat 01 Feb to Mon 03 Feb'
    )
