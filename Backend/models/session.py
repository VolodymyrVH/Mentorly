from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Enum, CheckConstraint, ForeignKey, Boolean, DECIMAL
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from core.database import Base


class StatusSession(PyEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELED_BY_STUDENT = "CANCELED_BY_STUDENT"
    CANCELED_BY_MENTOR = "CANCELED_BY_MENTOR"
    NO_SHOW = "NO_SHOW"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    repeat = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(StatusSession, name="session_status"), nullable=False, default=StatusSession.PENDING)
    price_per_hour = Column(DECIMAL(10, 2), nullable=False)
    datetime_start = Column(TIMESTAMP(timezone=True), nullable=False)
    datetime_end = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("price_per_hour > 0", name="check_session_price_positive"),
        CheckConstraint("datetime_end > datetime_start", name="check_session_datetime"),)

    mentor = relationship("User", back_populates="session_mentor", foreign_keys=[mentor_id])
    student = relationship("User", back_populates="session_student", foreign_keys=[student_id])

    discipline = relationship("Discipline")
