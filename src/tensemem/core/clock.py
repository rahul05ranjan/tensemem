"""Clock abstraction for bi-temporal timestamps (ADR 0005).

All stored times are UTC fixed-width ISO 8601 text so SQLite text order matches
time order. Production code uses :class:`SystemClock`; tests inject
:class:`FrozenClock`.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol, runtime_checkable

# YYYY-MM-DDTHH:MM:SS.ffffffZ — always 27 characters.
INSTANT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
INSTANT_WIDTH = 27


@runtime_checkable
class Clock(Protocol):
    """Source of "now" for recorded_at and related fields."""

    def now(self) -> datetime:
        """Return the current UTC time (timezone-aware)."""
        ...


class SystemClock:
    """Wall clock in UTC."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class FrozenClock:
    """Clock that always returns a fixed instant (for tests)."""

    def __init__(self, instant: datetime) -> None:
        self._instant = _ensure_utc(instant)

    def now(self) -> datetime:
        return self._instant

    def set(self, instant: datetime) -> None:
        """Move the frozen instant forward or backward."""
        self._instant = _ensure_utc(instant)

    def advance(self, *, seconds: float = 0, milliseconds: int = 0) -> datetime:
        """Advance the frozen clock and return the new instant."""
        delta = timedelta(seconds=seconds, milliseconds=milliseconds)
        self._instant = self._instant + delta
        return self._instant


def format_instant(instant: datetime) -> str:
    """Format a timezone-aware datetime as fixed-width UTC ISO text."""
    utc = _ensure_utc(instant)
    # strftime %f is always 6 digits; Z is appended explicitly.
    return utc.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def parse_instant(text: str) -> datetime:
    """Parse a fixed-width UTC instant produced by :func:`format_instant`."""
    if len(text) != INSTANT_WIDTH or not text.endswith("Z"):
        msg = f"expected {INSTANT_WIDTH}-char UTC instant ending in Z, got {text!r}"
        raise ValueError(msg)
    naive = datetime.strptime(text[:-1], "%Y-%m-%dT%H:%M:%S.%f")  # noqa: DTZ007
    return naive.replace(tzinfo=UTC)


def _ensure_utc(instant: datetime) -> datetime:
    if instant.tzinfo is None:
        msg = "datetime must be timezone-aware (UTC)"
        raise ValueError(msg)
    return instant.astimezone(UTC)
