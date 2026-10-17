from datetime import UTC, datetime, timedelta

import pytest

from tensemem.core.clock import (
    INSTANT_WIDTH,
    FrozenClock,
    SystemClock,
    format_instant,
    parse_instant,
)


def test_format_instant_is_fixed_width_utc() -> None:
    instant = datetime(2026, 10, 17, 12, 30, 45, 123456, tzinfo=UTC)
    text = format_instant(instant)
    assert len(text) == INSTANT_WIDTH
    assert text == "2026-10-17T12:30:45.123456Z"
    assert parse_instant(text) == instant


def test_format_instant_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        format_instant(datetime(2026, 10, 17, 12, 0, 0))  # noqa: DTZ001


def test_frozen_clock_is_stable_until_advanced() -> None:
    start = datetime(2026, 10, 17, 8, 0, 0, tzinfo=UTC)
    clock = FrozenClock(start)
    assert clock.now() == start
    assert format_instant(clock.now()) == "2026-10-17T08:00:00.000000Z"
    clock.advance(seconds=90)
    assert clock.now() == start + timedelta(seconds=90)


def test_system_clock_returns_aware_utc() -> None:
    now = SystemClock().now()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
