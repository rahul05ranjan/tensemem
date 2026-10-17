"""Injectable "now" for bi-temporal timestamps (ADR 0005).

Stored times are UTC fixed-width ISO 8601 text so SQLite text order matches time
order. Call sites take a ``Clock`` (any zero-arg callable returning UTC
``datetime``). Production uses :func:`utc_now`; tests use :class:`FrozenClock`.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

# YYYY-MM-DDTHH:MM:SS.ffffffZ — always 27 characters.
INSTANT_WIDTH = 27

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    """Wall-clock time in UTC."""
    return datetime.now(UTC)


class FrozenClock:
    """Callable clock that always returns a fixed instant (for tests)."""

    def __init__(self, instant: datetime) -> None:
        self._instant = _ensure_utc(instant)

    def __call__(self) -> datetime:
        return self._instant

    def set(self, instant: datetime) -> None:
        """Move the frozen instant forward or backward."""
        self._instant = _ensure_utc(instant)

    def advance(self, *, seconds: float = 0, milliseconds: int = 0) -> datetime:
        """Advance the frozen clock and return the new instant."""
        self._instant = self._instant + timedelta(seconds=seconds, milliseconds=milliseconds)
        return self._instant


def format_instant(instant: datetime) -> str:
    """Format a timezone-aware datetime as fixed-width UTC ISO text."""
    utc = _ensure_utc(instant)
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
