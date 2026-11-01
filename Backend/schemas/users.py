from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserRole(str, Enum):
    USER = "USER"
    MENTOR = "MENTOR"
    ADMIN = "ADMIN"


class UserCreateSchema(BaseModel):
    firstname: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    email: EmailStr = Field(max_length=255)
    phone: str = Field(min_length=10, max_length=15)
    profile_picture: str | None = Field(max_length=255)
    dob: date

    @field_validator("dob")
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Date of birth must be in the past")
        
        return v


class UserLoginSchema(BaseModel):
    login: str = Field(min_length=1, max_length=255) #add check phone or email
    password: str = Field(min_length=8)


class UserUpdateSchema(BaseModel):
    firstname: str | None = Field(None, min_length=1, max_length=100)
    lastname: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8)
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=10, max_length=15)
    profile_picture: str | None = Field(None, max_length=255)
    dob: date | None = None


class UserRoleUpdateSchame(BaseModel):
    role: UserRole


class UserResponseSchema(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    phone: str
    profile_picture: str
    role: UserRole
    dob: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)