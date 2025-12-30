from datetime import date

from testfixtures import Replacer, ShouldRaise, compare, mock_date

import diary.store
from diary.objects import Period, Stuff, Type
from diary.store import MemoryStore, Store


def test_memory_store_satisfies_protocol() -> None:
    store: Store = MemoryStore()
    compare(store is not None, expected=True)


def test_get_nonexistent() -> None:
    store = MemoryStore()
    compare(store.get(date(2024, 1, 15)), expected=None)


def test_put_and_get(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    stuff = Stuff(type=Type.event, title="Test event")
    store.put(Period(start=date(2024, 1, 15), stuff=[stuff]))

    compare(
        store.get(date(2024, 1, 15)),
        expected=Period(start=date(2024, 1, 15), stuff=[stuff], modified=date(2001, 1, 1)),
    )


def test_query_all(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    store.put(Period(start=date(2024, 1, 15)))
    store.put(Period(start=date(2024, 1, 16)))
    store.put(Period(start=date(2024, 1, 17)))

    compare(
        list(store.query()),
        expected=[
            Period(start=date(2024, 1, 15), modified=date(2001, 1, 1)),
            Period(start=date(2024, 1, 16), modified=date(2001, 1, 2)),
            Period(start=date(2024, 1, 17), modified=date(2001, 1, 4)),
        ],
    )


def test_query_with_start(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    store.put(Period(start=date(2024, 1, 15)))
    store.put(Period(start=date(2024, 1, 16)))
    store.put(Period(start=date(2024, 1, 17)))

    compare(
        list(store.query(start=date(2024, 1, 16))),
        expected=[
            Period(start=date(2024, 1, 16), modified=date(2001, 1, 2)),
            Period(start=date(2024, 1, 17), modified=date(2001, 1, 4)),
        ],
    )


def test_query_with_end(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    store.put(Period(start=date(2024, 1, 15)))
    store.put(Period(start=date(2024, 1, 16)))
    store.put(Period(start=date(2024, 1, 17)))

    compare(
        list(store.query(end=date(2024, 1, 16))),
        expected=[
            Period(start=date(2024, 1, 15), modified=date(2001, 1, 1)),
            Period(start=date(2024, 1, 16), modified=date(2001, 1, 2)),
        ],
    )


def test_query_with_range(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    store.put(Period(start=date(2024, 1, 15)))
    store.put(Period(start=date(2024, 1, 16)))
    store.put(Period(start=date(2024, 1, 17)))
    store.put(Period(start=date(2024, 1, 18)))

    compare(
        list(store.query(start=date(2024, 1, 16), end=date(2024, 1, 17))),
        expected=[
            Period(start=date(2024, 1, 16), modified=date(2001, 1, 2)),
            Period(start=date(2024, 1, 17), modified=date(2001, 1, 4)),
        ],
    )


def test_query_with_updated_since() -> None:
    store = MemoryStore()
    period1 = Period(start=date(2024, 1, 15), modified=date(2024, 1, 10))
    period2 = Period(start=date(2024, 1, 16), modified=date(2024, 1, 12))
    period3 = Period(start=date(2024, 1, 17), modified=date(2024, 1, 14))
    store.periods[period1.start] = period1
    store.periods[period2.start] = period2
    store.periods[period3.start] = period3

    compare(list(store.query(updated_since=date(2024, 1, 12))), expected=[period2, period3])


def test_history_existing(replace: Replacer) -> None:
    replace.in_module(date, mock_date(), module=diary.store)
    store = MemoryStore()
    store.put(Period(start=date(2024, 1, 15)))

    compare(
        store.history(date(2024, 1, 15)),
        expected=[Period(start=date(2024, 1, 15), modified=date(2001, 1, 1))],
    )


def test_history_nonexistent() -> None:
    store = MemoryStore()
    with ShouldRaise(KeyError("No period for 2024-01-15")):
        store.history(date(2024, 1, 15))
