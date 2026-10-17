"""Public identifiers.

Facts and episodes expose ULIDs. Generation and Crockford encoding come from
``python-ulid``; we only wrap it behind a tiny API used by the rest of the engine.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ulid import ULID


def new_ulid(*, when_ms: int | None = None) -> str:
    """Return a new ULID string.

    ``when_ms`` is the Unix epoch in milliseconds. Tests pass a fixed value so
    IDs are reproducible; production code leaves it as ``None``.
    """
    if when_ms is None:
        return str(ULID())
    if when_ms < 0 or when_ms >= 2**48:
        msg = f"ULID timestamp out of range: {when_ms}"
        raise ValueError(msg)
    instant = datetime.fromtimestamp(when_ms / 1000, tz=UTC)
    return str(ULID.from_datetime(instant))


def ulid_timestamp_ms(ulid: str) -> int:
    """Extract the millisecond timestamp embedded in a ULID."""
    try:
        return ULID.from_str(ulid).milliseconds
    except (TypeError, ValueError) as exc:
        msg = f"invalid ULID: {ulid!r}"
        raise ValueError(msg) from exc
