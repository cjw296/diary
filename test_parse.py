from datetime import date

from lark import UnexpectedEOF
from testfixtures import compare, ShouldRaise

from parse import parse
from objects import Day, Stuff, Type


def test_roundtrip_day_empty():
    day = Day(date(2020, 2, 1))
    with ShouldRaise(UnexpectedEOF):
        parse(str(day))


def test_roundtrip_day_single():
    day = Day(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun')])
    compare(parse(str(day)), expected=[day])


def test_roundtrip_day_single_with_body():
    day = Day(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun', 'stuff\nthings')])
    compare(parse(str(day)), expected=[day])


def test_roundtip_mixed():
    day = Day(date(2020, 1, 1), [
        Stuff(Type.did, 'sleep'),
        Stuff(Type.cancelled, 'fun', body='bad\nthings'),
        Stuff(Type.event, 'a thing'),
        Stuff(Type.postponed, 'something else'),
    ])
    compare(parse(str(day)), expected=[day])


def test_single_sad():
    compare(
        parse((
            "(2021-11-02) Tuesday\n"
            "==================\n"
            "EVENT woke far too early :-(\n"
        )),
        expected=[
            Day(date(2021, 11, 2), [
                Stuff(Type.event, "woke far too early :-("),
            ])
        ])


def test_multi_sad_stuff():
    compare(
        parse((
            "(2021-11-02) Tuesday\n"
            "==================\n"
            "DID see dentist, again :'(\n"
            "DID form\n"
        )),
        expected=[
            Day(date(2021, 11, 2), [
                Stuff(Type.did, "see dentist, again :'("),
                Stuff(Type.did, "form"),
            ])
        ])


def test_multi_day():
    compare(
        parse((
            "(2021-11-02) Tuesday\n"
            "==================\n"
            "DID thing 1\n"
            "\n"
            "(2021-11-03) Wednesday\n"
            "==================\n"
            "DID thing 2\n"
        )),
        expected=[
            Day(date(2021, 11, 2), [
                Stuff(Type.did, "thing 1"),
            ]),
            Day(date(2021, 11, 3), [
                Stuff(Type.did, "thing 2"),
            ]),
        ])


def test_multi_day_multi_line_separator():
    compare(
        parse((
            "(2021-11-02) Tuesday\n"
            "==================\n"
            "DID thing 1\n"
            "\n\n\n"
            "(2021-11-03) Wednesday\n"
            "==================\n"
            "DID thing 2\n"
        )),
        expected=[
            Day(date(2021, 11, 2), [
                Stuff(Type.did, "thing 1"),
            ]),
            Day(date(2021, 11, 3), [
                Stuff(Type.did, "thing 2"),
            ]),
        ])


def test_full_example():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "DID stuff\n"
            "DID get delayed by trains:\n"
            "--\n"
            "19:32 Padd to Bristol - Delay/Repay, arrived shortly after 21:04, so\n"
            "60 mins delay.\n"
            "--\n"
            "CANCELLED fun: trains delayed\n"
            "\n"
            "(2021-11-04) Thursday\n"
            "======================\n"
            "DID more stuff\n"
            "DID submit foo:  2298535\n"
            "DID bullet point thing:\n"
            "--\n"
            "- point 1\n"
            "- point 2\n"
            "- point 3\n"
            "--\n"
        )),
        expected=[
            Day(date(2021, 11, 3), [
                Stuff(Type.did, "stuff"),
                Stuff(Type.did, "get delayed by trains", body=(
                    "19:32 Padd to Bristol - Delay/Repay, arrived shortly after 21:04, so\n"
                    "60 mins delay."
                )),
                Stuff(Type.cancelled, "fun: trains delayed"),
            ]),
            Day(date(2021, 11, 4), [
                Stuff(Type.did, "more stuff"),
                Stuff(Type.did, "submit foo:  2298535"),
                Stuff(Type.did, "bullet point thing", body=(
                    "- point 1\n"
                    "- point 2\n"
                    "- point 3"
                )),
            ]),
        ])
