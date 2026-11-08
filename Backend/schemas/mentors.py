from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class MentorDisciplineCreateSchema(BaseModel):
    mentor_id: int
    discipline_id: int
    price: Decimal = Field(gt=0)
    duration_in_minutes: int = Field(gt=0)


class MentorDisciplineUpdateSchema(BaseModel):
    price: Decimal | None = Field(default=None, gt=0)
    duration_in_minutes: int | None = Field(default=None, gt=0)


class MentorDisciplineResponseSchema(BaseModel):
    id: int
    mentor_id: int
    discipline_id: int
    price: Decimal
    duration_in_minutes: int

    model_config = ConfigDict(from_attributes=True)