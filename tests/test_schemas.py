import pytest
from pydantic import ValidationError

from pipeline.schemas import Anchor, Commitment, ServiceItem


def _commitment(**over):
    base = dict(
        id="C01",
        title="t",
        title_ar="ع",
        statement="s",
        statement_ar="ع",
        jurisdiction="federal",
        kind="target",
        source_ids=["S01"],
        anchors=[{"source_id": "S01", "text": "fifty percent"}],
    )
    base.update(over)
    return Commitment(**base)


def test_minimal_commitment_ok():
    assert _commitment().deadline_precision == "none"


def test_precision_requires_date():
    with pytest.raises(ValidationError):
        _commitment(deadline_precision="year")


def test_date_requires_precision():
    with pytest.raises(ValidationError):
        _commitment(deadline="2027-12-31")


def test_target_number_needs_comparator_and_text():
    with pytest.raises(ValidationError):
        _commitment(target_number=50.0, target_value="50%")


def test_unknown_unit_rejected():
    with pytest.raises(ValidationError):
        _commitment(unit="widgets")


def test_anchor_must_be_short():
    with pytest.raises(ValidationError):
        Anchor(source_id="S01", text=" ".join(["w"] * 15))


def _item(**over):
    base = dict(
        id="X1",
        entity_id="SE01",
        sector="health",
        kind="service",
        audience="citizen",
        name="n",
        annual_transactions=10,
        maturity=2,
        oversight=True,
        audit_trail=True,
        uae_residency=True,
        fallback=True,
    )
    base.update(over)
    return ServiceItem(**base)


def test_synthetic_flag_cannot_be_false():
    with pytest.raises(ValidationError):
        _item(is_synthetic=False)


def test_operation_must_be_internal():
    with pytest.raises(ValidationError):
        _item(kind="operation", audience="citizen")


def test_service_cannot_be_internal():
    with pytest.raises(ValidationError):
        _item(audience="internal")
