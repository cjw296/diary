from datetime import date

from testfixtures import compare, ShouldRaise

from objects import Period, Stuff, Type
from parse import parse
from zope import Client, LookBackFailed


def test_roundtrip_day_empty():
    day = Period(date(2020, 2, 1))
    compare(parse(str(day)), expected=[day])


def test_roundtrip_day_single():
    day = Period(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun')])
    compare(parse(str(day)), expected=[day])


def test_roundtrip_day_start_and_end():
    day = Period(date(2020, 2, 1), end=date(2020, 2, 3))
    compare(parse(str(day)), expected=[day])


def test_roundtrip_day_single_with_body():
    day = Period(date(2020, 2, 1), [Stuff(Type.cancelled, 'fun', 'stuff\nthings')])
    compare(parse(str(day)), expected=[day])


def test_roundtip_mixed():
    day = Period(date(2020, 1, 1), [
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
            Period(date(2021, 11, 2), [
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
            Period(date(2021, 11, 2), [
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
            Period(date(2021, 11, 2), [
                Stuff(Type.did, "thing 1"),
            ]),
            Period(date(2021, 11, 3), [
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
            Period(date(2021, 11, 2), [
                Stuff(Type.did, "thing 1"),
            ]),
            Period(date(2021, 11, 3), [
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
            Period(date(2021, 11, 3), [
                Stuff(Type.did, "stuff"),
                Stuff(Type.did, "get delayed by trains", body=(
                    "19:32 Padd to Bristol - Delay/Repay, arrived shortly after 21:04, so\n"
                    "60 mins delay."
                )),
                Stuff(Type.cancelled, "fun: trains delayed"),
            ]),
            Period(date(2021, 11, 4), [
                Stuff(Type.did, "more stuff"),
                Stuff(Type.did, "submit foo:  2298535"),
                Stuff(Type.did, "bullet point thing", body=(
                    "- point 1\n"
                    "- point 2\n"
                    "- point 3"
                )),
            ]),
        ])


def test_multiple_empty():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "\n"
            "(2021-11-04) Thursday\n"
            "======================\n"
        )),
        expected=[
            Period(date(2021, 11, 3), []),
            Period(date(2021, 11, 4), []),
        ])


def test_colon_after_event():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "EVENT: something happened\n"
        )),
        expected=[
            Period(date(2021, 11, 3), [Stuff(Type.event, 'something happened')]),
        ])


def test_stuff_synonyms():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "CANCEL everything\n"
        )),
        expected=[
            Period(date(2021, 11, 3), [Stuff(Type.cancelled, 'everything')]),
        ])


def test_tags():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "DID:tag1:tag2 some thing\n"
        )),
        expected=[
            Period(date(2021, 11, 3), [Stuff(Type.did, 'some thing', tags=['tag1', 'tag2'])]),
        ])


def test_tags_with_body():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "DID:tag1:tag2 some thing:\n"
            "--\n"
            "The body\n"
            "--\n"
        )),
        expected=[
            Period(date(2021, 11, 3), [
                Stuff(Type.did, 'some thing', body='The body', tags=['tag1', 'tag2'])
            ]),
        ])


def test_newline_in_body():
    compare(
        parse((
            "(2021-11-03) Wednesday\n"
            "======================\n"
            "DID something interesting:\n"
            "--\n"
            "part 1\n"
            "\n"
            "part 2\n"
            "--\n"
        )),
        expected=[
            Period(date(2021, 11, 3), [
                Stuff(Type.did, 'something interesting', 'part 1\n\npart 2')
            ]),
        ])


class TestInferDates:

    def test_standard(self):
        compare(Client.infer_date('(2021-11-08) Monday'), expected=(date(2021, 11, 8), None))

    def test_day_mismatch(self):
        with ShouldRaise(AssertionError('08 Nov 21 was a Monday, got: (2021-11-08) Tuesday')):
            Client.infer_date('(2021-11-08) Tuesday')

    def test_just_day_and_date(self):
        compare(
            Client.infer_date(
                ' Sunday \t23rd\n',
                previous=date(2020, 2, 24),
            ),
            expected=(date(2020, 2, 23), None)
        )

    def test_day_date_and_month(self):
        compare(
            Client.infer_date('Saturday 5th May', previous=date(2018, 5, 6)),
            expected=(date(2018, 5, 5), None)
        )

    def test_date_and_month(self):
        compare(
            Client.infer_date('5th July', previous=date(2008, 7, 6)),
            expected=(date(2008, 7, 5), None)
        )

    def test_date_and_sept(self):
        compare(
            Client.infer_date('30th Sept', previous=date(2005, 10, 1)),
            expected=(date(2005, 9, 30), None)
        )

    def test_just_day_name(self):
        compare(
            Client.infer_date(
                'Tuesday',
                previous=date(2007, 5, 30),
            ),
            expected=(date(2007, 5, 29), None)
        )

    def test_just_day_name_too_far_back(self):
        sunday = date(2021, 11, 7)
        with ShouldRaise(ValueError("Bad format: 'Sunday'")):
            Client.infer_date('Sunday', previous=sunday)

    def test_day_date_and_bad_month(self):
        with ShouldRaise(AssertionError("2018-05-05 was in May, but entry had June")):
            Client.infer_date('Saturday 5th June', previous=date(2018, 5, 6))

    def test_not_within_look_back(self):
        with ShouldRaise(LookBackFailed(date(2020, 2, 20), "Sunday 18th")):
            Client.infer_date('Sunday 18th', previous=date(2020, 2, 24))

    def test_day_not_match_date(self):
        with ShouldRaise(AssertionError("2020-02-22 was a Saturday, but entry had Sunday")):
            Client.infer_date('Sunday 22nd', previous=date(2020, 2, 24))

    def test_day_bad_year(self):
        with ShouldRaise(AssertionError("2011-01-02 was in 2011, but entry had 2010")):
            Client.infer_date(
                'Sunday 2nd Jan 2010', previous=date(2011, 1, 3)
            )

    def test_bad_format(self):
        with ShouldRaise(ValueError("Bad format: 'Sunday 234th'")):
            Client.infer_date('Sunday 234th')

    def test_date_range_found(self):
        compare(expected=(date(2018, 6, 18), date(2018, 6, 22)),
                actual=Client.infer_date('Monday 18th - Friday 22nd', previous=date(2018, 6, 23)))

    def test_date_range_no_space(self):
        compare(expected=(date(2010, 1, 30), date(2010, 1, 31)),
                actual=Client.infer_date('Saturday 30th-Sunday 31st', previous=date(2010, 2, 1)))

    def test_date_range_short_day(self):
        compare(expected=(date(2015, 9, 6), date(2015, 9, 12)),
                actual=Client.infer_date('Sunday 6th - Sat 12th', previous=date(2015, 9, 13)))

    def test_date_range_to(self):
        compare(expected=(date(2013, 3, 26), date(2013, 4, 9)),
                actual=Client.infer_date(
                    'Tuesday 26th March to Tuesday 9th April', previous=date(2013, 4, 10)
                ))

    def test_date_range_full(self):
        compare(expected=(date(2010, 12, 17), date(2011, 1, 2)),
                actual=Client.infer_date(
                    'Friday 17th Dec 2010 - Sunday 2nd Jan 2011', previous=date(2011, 1, 3)
                ))

    def test_date_range_excess_lookback(self):
        text = 'Friday 1st - Wednesday 27th'
        with ShouldRaise(LookBackFailed(date(2018, 6, 3), text)):
            Client.infer_date(text, previous=date(2018, 6, 28)),

    def test_date_range_very_explicit_range(self):
        text = 'Friday 24th Sep 2004- Thursday 21st October'
        compare(expected=(date(2004, 9, 24), date(2004, 10, 21)),
                actual=Client.infer_date(text, previous=date(2004, 10, 22)))

    def test_date_range_lookback_edge_case(self):
        compare(expected=(date(2008, 6, 4), date(2008, 6, 8)),
                actual=Client.infer_date(
                    '4th June - 8th June', previous=date(2008, 6, 9)
                ))


class TestAddStuff:

    def test_simple(self):
        compare(
            Client.add_stuff(
                Period(start=date(2021, 11, 9)),
                summary=(
                    'DID something\n'
                ),
                body='\n',
            ),
            expected=Period(start=date(2021, 11, 9), stuff=[
                Stuff(Type.did, "something"),
            ])
        )

    def test_no_newlines_at_end(self):
        compare(
            Client.add_stuff(
                Period(start=date(2021, 11, 9)),
                summary=(
                    'DID something'
                ),
                body='\n',
            ),
            expected=Period(start=date(2021, 11, 9), stuff=[
                Stuff(Type.did, "something"),
            ])
        )

    def test_no_whitespace_at_end(self):
        compare(
            Client.add_stuff(
                Period(start=date(2021, 11, 9)),
                summary=(
                    'DID something\n \t\n \n\n'
                ),
                body='\n',
            ),
            expected=Period(start=date(2021, 11, 9), stuff=[
                Stuff(Type.did, "something"),
            ])
        )
