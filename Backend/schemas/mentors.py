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
    discipline_name: str
    price: Decimal
    duration_in_minutes: int

    model_config = ConfigDict(from_attributes=True)


class MentorProfileCreateSchema(BaseModel):
    bio: str | None = None
    degree: str | None = None
    experience_years: int | None = Field(default=None, ge=0)


class MentorProfileUpdateSchema(BaseModel):
    bio: str | None = None
    degree: str | None = None
    experience_years: int | None = Field(default=None, ge=0)

    
class MentorProfileResponseSchema(BaseModel):
    id: int
    mentor_id: int

    firstname: str
    lastname: str
    email: str
    profile_picture: str | None

    bio: str | None
    degree: str | None
    experience_years: int | None
    rating: Decimal
    review_count: int
    approval_status: bool

    model_config = ConfigDict(from_attributes=True)


class MentorProfileApprovalSchema(BaseModel):
    approval_status: bool