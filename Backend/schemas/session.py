from pydantic import BaseModel, ConfigDict, Field, model_validator
from decimal import Decimal
from datetime import datetime

from models.session import StatusSession


@model_validator(mode="after")
def validate_datetime(self):
    if self.datetime_end <= self.datetime_start:
        raise ValueError("datetime_end must be later than datetime_start")
    return self


class SessionCreateSchema(BaseModel):
    mentor_id: int
    student_id: int
    discipline_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    repeat: bool = False
    datetime_start: datetime
    datetime_end: datetime


class SessionUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    repeat: bool | None = None
    datetime_start: datetime | None = None
    datetime_end: datetime | None = None


class SessionResponseSchema(BaseModel):
    id: int
    mentor_id: int
    student_id: int
    discipline_id: int
    title: str
    description: str | None
    repeat: bool
    status: StatusSession
    price_per_hour: Decimal
    datetime_start: datetime
    datetime_end: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
