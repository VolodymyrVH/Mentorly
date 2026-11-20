from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from decimal import Decimal
from models.sessions import StatusSession


class SessionCreateSchema(BaseModel):
    mentor_id: int
    discipline_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    repeat: bool = False
    datetime_start: datetime
    datetime_end: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.datetime_start >= self.datetime_end:
            raise ValueError("End must be later than start")
        if self.datetime_start.tzinfo is None or self.datetime_end.tzinfo is None:
            raise ValueError("Timezone information is required")
        return self


class SessionUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    repeat: bool | None = None


class SessionStatusUpdateSchema(BaseModel):
    status: StatusSession


class SessionRescheduleSchema(BaseModel):
    datetime_start: datetime
    datetime_end: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.datetime_start >= self.datetime_end:
            raise ValueError("End must be later than start")
        if self.datetime_start.tzinfo is None or self.datetime_end.tzinfo is None:
            raise ValueError("Timezone information is required")
        return self


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