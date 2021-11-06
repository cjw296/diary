from datetime import date

from testfixtures import compare

from objects import Stuff, Type, Day


def test_stuff_str_minimal():
    compare(str(Stuff(Type('EVENT'), title='A thing')),
            expected='EVENT A thing')


def test_stuff_str_newlines_at_end():
    compare(str(Stuff(Type('EVENT'), title='A thing\n\n')),
            expected='EVENT A thing')


def test_stuff_str_maximal():
    compare(str(Stuff(Type.did, title='A thing', body='some body text\nmore lines')),
            expected='DID A thing:\n--\nsome body text\nmore lines\n--')


def test_stuff_str_body_with_newline_at_end():
    compare(str(Stuff(Type.did, title='A thing', body='some body text\n')),
            expected='DID A thing:\n--\nsome body text\n--')


def test_day_empty():
    compare(str(Day(date(2020, 2, 1))), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
    ))


def test_day_single():
    compare(str(Day(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun')])), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
        'CANCELLED fun\n'
    ))


def test_day_single_with_body():
    compare(str(Day(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun', 'stuff\nthings')])), expected=(
        '(2020-02-01) Saturday\n'
        '=====================\n'
        'CANCELLED fun:\n'
        '--\n'
        'stuff\n'
        'things\n'
        '--\n'
    ))


def test_mixed():
    compare(str(Day(date(2020, 1, 1), [
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
