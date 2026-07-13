from datetime import date
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

    @field_validator("consent")
    @classmethod
    def consent_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Необходимо согласие на обработку данных")
        return value


class LeadResponse(BaseModel):
    lead_id: int
    status: str
