from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Date, Enum, CheckConstraint
from enum import Enum as PyEnum

from core.database import Base


class UserRole(PyEnum):
    USER = "USER"
    MENTOR = "MENTOR"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    profile_picture = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    dob = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("length(phone) >= 10", name="phone_length"),
    )