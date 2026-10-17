"""Public identifiers.

Facts and episodes expose ULIDs (Crockford base32, 26 characters). They sort by
creation time and are safe to show in APIs and logs. Database primary keys stay
as integers.
"""

from __future__ import annotations

import os
import time

# Crockford's Base32 (no I, L, O, U).
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_DECODE = {c: i for i, c in enumerate(_ALPHABET)}


def _encode(value: int, length: int) -> str:
    chars = ["\0"] * length
    for i in range(length - 1, -1, -1):
        chars[i] = _ALPHABET[value & 0x1F]
        value >>= 5
    if value:
        msg = "value too large for ULID field"
        raise ValueError(msg)
    return "".join(chars)


def new_ulid(*, when_ms: int | None = None) -> str:
    """Return a new ULID string.

    ``when_ms`` is the Unix epoch in milliseconds. Tests pass a fixed value so
    IDs are reproducible; production code leaves it as ``None``.
    """
    ts = int(time.time() * 1000) if when_ms is None else when_ms
    if ts < 0 or ts >= 2**48:
        msg = f"ULID timestamp out of range: {ts}"
        raise ValueError(msg)

    # 80 bits of randomness from the OS CSPRNG.
    rand = int.from_bytes(os.urandom(10), "big")
    return _encode(ts, 10) + _encode(rand, 16)


def ulid_timestamp_ms(ulid: str) -> int:
    """Extract the millisecond timestamp embedded in a ULID."""
    if len(ulid) != 26:
        msg = f"ULID must be 26 characters, got {len(ulid)}"
        raise ValueError(msg)
    value = 0
    for ch in ulid[:10].upper():
        try:
            value = (value << 5) | _DECODE[ch]
        except KeyError as exc:
            msg = f"invalid ULID character: {ch!r}"
            raise ValueError(msg) from exc
    return value
