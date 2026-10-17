"""Domain types shared by the resolver, storage, and public API.

These are pure data models. Persistence and the decision table live in later
modules; this file is the contract they share.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Cardinality(StrEnum):
    ONE = "ONE"
    MANY = "MANY"


class OpKind(StrEnum):
    SET = "SET"
    ADD = "ADD"
    REMOVE = "REMOVE"
    RETRACT = "RETRACT"
    REPLACE_SET = "REPLACE_SET"
    DENY = "DENY"


class Modality(StrEnum):
    ASSERTED = "asserted"
    PLANNED = "planned"
    HYPOTHETICAL = "hypothetical"
    NEGATED = "negated"


class ValidPrecision(StrEnum):
    INSTANT = "instant"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    UNKNOWN = "unknown"


class FactStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"
    STALE = "STALE"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


class FactSource(StrEnum):
    EXTRACTED = "extracted"
    EXPLICIT = "explicit"
    DERIVED = "derived"
    IMPORTED = "imported"


class EdgeKind(StrEnum):
    SUPERSEDES = "SUPERSEDES"
    EVIDENCED_BY = "EVIDENCED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    CONTRADICTS = "CONTRADICTS"


class EpisodeKind(StrEnum):
    MESSAGE = "message"
    EXPLICIT_OP = "explicit_op"


class EpisodeRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class EpisodeStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    DISMISSED = "DISMISSED"
    DELETED = "DELETED"


class PredicateSpec(BaseModel):
    """How a new predicate should be registered when the extractor invents one."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    cardinality: Cardinality = Cardinality.ONE
    description: str = ""
    aliases: tuple[str, ...] = ()


class ExtractedOp(BaseModel):
    """One typed operation proposed by the extractor (or built by the deterministic API)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    subject: str
    predicate: str
    object: str
    op: OpKind
    modality: Modality = Modality.ASSERTED
    valid_from: str | None = None
    valid_precision: ValidPrecision = ValidPrecision.UNKNOWN
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    new_predicate: PredicateSpec | None = None
    evidence: str = ""
    is_confirmation: bool = False


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ops: tuple[ExtractedOp, ...] = ()


class Freshness(BaseModel):
    """How up to date a read is relative to the episode log (ADR 0006)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    as_of_seq: int = Field(ge=0)
    latest_seq: int = Field(ge=0)
    pending: int = Field(ge=0)
    failed: int = Field(ge=0)
    projection_version: int = Field(ge=1, default=1)

    @property
    def is_current(self) -> bool:
        return self.pending == 0 and self.failed == 0


class AddResult(BaseModel):
    """Returned by ``Memory.add`` so callers can wait for read-your-writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    seq: int = Field(ge=1)
    episode_ids: tuple[str, ...] = ()
    job_id: str | None = None


class FactView(BaseModel):
    """Public shape of a fact as returned by ``state`` / ``history`` / ``explain``."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    subject: str
    predicate: str
    object: str
    status: FactStatus
    modality: Modality = Modality.ASSERTED
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    valid_from: str | None = None
    valid_to: str | None = None
    valid_precision: ValidPrecision = ValidPrecision.UNKNOWN
    recorded_at: str
    recorded_seq: int = Field(ge=0)


class OnStale(StrEnum):
    FLAG = "flag"
    RAISE = "raise"


class StaleMemoryError(Exception):
    """Raised when ``on_stale='raise'`` and the watermark has not reached ``min_seq``."""

    def __init__(self, *, min_seq: int, freshness: Freshness) -> None:
        self.min_seq = min_seq
        self.freshness = freshness
        super().__init__(
            f"memory not current: need seq>={min_seq}, as_of_seq={freshness.as_of_seq}, "
            f"pending={freshness.pending}, failed={freshness.failed}"
        )


# Resolved mutation intents produced by the decision table (Day 7-8). Kept here
# so storage and the resolver share one vocabulary from day one.
MutationKind = Literal[
    "insert_active",
    "insert_candidate",
    "insert_historical",
    "reinforce",
    "supersede",
    "retract",
    "reject",
    "drop",
]


class Mutation(BaseModel):
    """One state change decided by ``resolve()`` before ``apply()`` writes it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: MutationKind
    op: ExtractedOp
    reason: str
    target_fact_id: str | None = None

    @field_validator("reason")
    @classmethod
    def _reason_nonempty(cls, value: str) -> str:
        if not value.strip():
            msg = "mutation reason must be non-empty"
            raise ValueError(msg)
        return value
