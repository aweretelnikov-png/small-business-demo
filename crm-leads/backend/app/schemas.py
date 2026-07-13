import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=30)
    service: Literal["false-door", "hidden-door", "decorative-door"]
    district: str = Field(min_length=2, max_length=200)
    desired_date: date | None = None
    comment: str | None = Field(default=None, max_length=2000)
    consent: bool

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)

        if len(digits) == 10:
            digits = "7" + digits
        elif len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]

        if len(digits) != 11 or not digits.startswith("7"):
            raise ValueError("Некорректный российский телефон")

        return f"+{digits}"

    @field_validator("consent")
    @classmethod
    def consent_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Необходимо согласие на обработку данных")
        return value


class LeadResponse(BaseModel):
    lead_id: int
    status: str


class LeadRead(BaseModel):
    id: int
    name: str
    phone: str
    service: str
    district: str
    desired_date: date | None
    comment: str | None
    status: str
    crm_external_id: str | None
    created_at: datetime
