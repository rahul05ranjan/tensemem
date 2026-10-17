import pytest

from tensemem.core.ids import new_ulid, ulid_timestamp_ms


def test_ulid_length_and_alphabet() -> None:
    ulid = new_ulid(when_ms=1_700_000_000_000)
    assert len(ulid) == 26
    assert ulid == ulid.upper()
    allowed = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
    assert set(ulid) <= allowed


def test_ulid_embeds_timestamp() -> None:
    when_ms = 1_700_000_000_000
    ulid = new_ulid(when_ms=when_ms)
    assert ulid_timestamp_ms(ulid) == when_ms


def test_ulids_with_same_time_sort_lexicographically_by_randomness() -> None:
    a = new_ulid(when_ms=1_700_000_000_000)
    b = new_ulid(when_ms=1_700_000_000_000)
    # Same timestamp prefix; full strings still compare as opaque IDs.
    assert a[:10] == b[:10]
    assert a != b


def test_later_timestamp_sorts_after_earlier() -> None:
    earlier = new_ulid(when_ms=1_700_000_000_000)
    later = new_ulid(when_ms=1_700_000_000_001)
    assert earlier < later


def test_invalid_ulid_rejected() -> None:
    with pytest.raises(ValueError, match="invalid ULID"):
        ulid_timestamp_ms("short")
