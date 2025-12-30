from datetime import date
from typing import Iterable, Protocol, Sequence

from diary.objects import Period


class MemoryStore:
    """Simple in-memory Store implementation for testing."""

    def __init__(self) -> None:
        self.periods: dict[date, Period] = {}

    def get(self, dt: date) -> Period | None:
        return self.periods.get(dt)

    def put(self, period: Period) -> None:
        period.modified = date.today()
        self.periods[period.start] = period

    def query(
        self,
        start: date | None = None,
        end: date | None = None,
        updated_since: date | None = None,
    ) -> Iterable[Period]:
        for dt in sorted(self.periods.keys()):
            period = self.periods[dt]
            if start is not None and dt < start:
                continue
            if end is not None and dt > end:
                continue
            if updated_since is not None:
                if period.modified is None or period.modified < updated_since:
                    continue
            yield period

    def history(self, dt: date) -> Sequence[Period]:
        if dt not in self.periods:
            raise KeyError(f"No period for {dt}")
        return [self.periods[dt]]


class Store(Protocol):
    """Protocol for storing and retrieving diary periods.

    This protocol defines a common interface for different diary storage
    backends including local file trees (with sqlite indexing), monolithic
    text files, and remote Zope blogging systems.

    The protocol supports efficient synchronization between stores via
    modification timestamp tracking and incremental queries.
    """

    def get(self, dt: date) -> Period | None:
        """Retrieve a period for a specific date.

        :param dt: The date to retrieve.
        :return: Period for the given date if it exists, None otherwise.
                 The returned Period should include its modification timestamp
                 in the ``modified`` field if available.
        """
        ...

    def put(self, period: Period) -> None:
        """Store a period (upsert: creates if new, updates if exists).

        The period's start date is used as the primary key. If a period
        already exists for that date, it is replaced.

        Implementations should update the period's modification timestamp
        to the current time when storing.

        :param period: The period to store.
        :raises ValueError: If period.start is None or period has invalid date range.
        """
        ...

    def query(
        self,
        start: date | None = None,
        end: date | None = None,
        updated_since: date | None = None,
    ) -> Iterable[Period]:
        """Query periods within a date range, optionally filtered by modification time.

        All parameters are optional - omitting all returns all periods in the store.

        :param start: Start date (inclusive). If None, queries from the earliest
                      available period.
        :param end: End date (inclusive). If None, queries to the most recent
                    available period.
        :param updated_since: If provided, only return periods that were modified
                              on or after this date. Essential for efficient
                              synchronization between stores.
        :return: Iterator of periods in chronological order (earliest to latest).
                 Each Period includes its modification timestamp in the ``modified``
                 field if available.

        .. note::
           Implementations may use lazy evaluation and pagination for
           efficiency. For large date ranges, periods are yielded incrementally.
        """
        ...

    def history(self, dt: date) -> Sequence[Period]:
        """Get the version history for a period at a specific date.

        Returns all historical versions of the period for the given date,
        ordered from oldest to newest. Useful for conflict resolution,
        auditing, and understanding how entries evolved over time.

        :param dt: The date to get history for.
        :return: Sequence of Period objects representing all versions, ordered
                 chronologically (oldest first). Each Period includes its
                 modification timestamp in the ``modified`` field.
        :raises KeyError: If no period exists for the given date. It is not
                         valid to call this method for a date that has no
                         periods.

        .. note::
           Stores that don't maintain version history may return a
           single-element sequence containing just the current version.
        """
        ...
