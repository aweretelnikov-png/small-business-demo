import pytest
from pydantic import ValidationError

from app.schemas import LeadCreate


@pytest.mark.parametrize(
    ("raw_phone", "expected_phone"),
    [
        ("+7 999 111-22-33", "+79991112233"),
        ("8 (999) 111-22-33", "+79991112233"),
        ("9991112233", "+79991112233"),
    ],
)
def test_phone_is_normalized(raw_phone: str, expected_phone: str) -> None:
    lead = LeadCreate(
        name="Иван",
        phone=raw_phone,
        service="hidden-door",
        district="Москва",
        consent=True,
    )

    assert lead.phone == expected_phone


def test_invalid_phone_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Некорректный российский телефон"):
        LeadCreate(
            name="Иван",
            phone="abcdefghij",
            service="hidden-door",
            district="Москва",
            consent=True,
        )


def test_consent_is_required() -> None:
    with pytest.raises(ValidationError, match="Необходимо согласие"):
        LeadCreate(
            name="Иван",
            phone="+7 999 111-22-33",
            service="hidden-door",
            district="Москва",
            consent=False,
        )


def test_unknown_service_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LeadCreate(
            name="Иван",
            phone="+7 999 111-22-33",
            service="unknown-service",
            district="Москва",
            consent=True,
        )
