import pytest
from pydantic import ValidationError

from tensemem.core.models import (
    AddResult,
    Cardinality,
    ExtractedOp,
    ExtractionResult,
    FactStatus,
    Freshness,
    Modality,
    Mutation,
    OpKind,
    PredicateSpec,
    StaleMemoryError,
    ValidPrecision,
)


def test_extracted_op_round_trip() -> None:
    op = ExtractedOp(
        subject="user",
        predicate="lives_in",
        object="Bangalore",
        op=OpKind.SET,
        modality=Modality.ASSERTED,
        valid_from="2026-10-10T00:00:00.000000Z",
        valid_precision=ValidPrecision.DAY,
        confidence=0.95,
        evidence="I moved to Bangalore last week",
    )
    restored = ExtractedOp.model_validate_json(op.model_dump_json())
    assert restored == op
    assert restored.op is OpKind.SET


def test_extraction_result_accepts_multiple_ops() -> None:
    result = ExtractionResult(
        ops=(
            ExtractedOp(
                subject="user",
                predicate="lives_in",
                object="Bangalore",
                op=OpKind.SET,
                evidence="moved to Bangalore",
            ),
            ExtractedOp(
                subject="user",
                predicate="uses_language",
                object="Rust",
                op=OpKind.REPLACE_SET,
                evidence="only write Rust",
                new_predicate=PredicateSpec(
                    name="uses_language",
                    cardinality=Cardinality.MANY,
                ),
            ),
        )
    )
    assert len(result.ops) == 2
    assert result.ops[1].new_predicate is not None
    assert result.ops[1].new_predicate.cardinality is Cardinality.MANY


def test_confidence_must_be_unit_interval() -> None:
    with pytest.raises(ValidationError):
        ExtractedOp(
            subject="user",
            predicate="lives_in",
            object="Delhi",
            op=OpKind.SET,
            confidence=1.5,
        )


def test_freshness_is_current() -> None:
    current = Freshness(as_of_seq=3, latest_seq=3, pending=0, failed=0)
    assert current.is_current is True
    stale = Freshness(as_of_seq=2, latest_seq=3, pending=1, failed=0)
    assert stale.is_current is False


def test_add_result_and_stale_error() -> None:
    added = AddResult(seq=7, episode_ids=("01ARZ3NDEKTSV4RRFFQ69G5FAV",))
    assert added.seq == 7
    freshness = Freshness(as_of_seq=6, latest_seq=7, pending=1, failed=0)
    err = StaleMemoryError(min_seq=7, freshness=freshness)
    assert err.min_seq == 7
    assert "pending=1" in str(err)


def test_mutation_requires_reason() -> None:
    op = ExtractedOp(
        subject="user",
        predicate="lives_in",
        object="Delhi",
        op=OpKind.SET,
    )
    with pytest.raises(ValidationError):
        Mutation(kind="drop", op=op, reason="   ")
    mutation = Mutation(kind="insert_active", op=op, reason="no prior active fact")
    assert mutation.target_fact_id is None
    assert FactStatus.ACTIVE.value == "ACTIVE"
