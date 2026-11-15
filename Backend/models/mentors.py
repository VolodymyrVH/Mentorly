from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, func, Date, Enum, CheckConstraint, DECIMAL, Numeric, Boolean
from sqlalchemy.orm import relationship

from core.database import Base


class MentorDiscipline(Base):
    __tablename__ = "mentor_discipline"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration_in_minutes = Column(Integer, nullable=False)

    user = relationship("User", back_populates="mentor_discipline")
    discipline = relationship("Discipline", back_populates="mentor_discipline")


class MentorProfiles(Base):
    __tablename__ = "mentor_profiles"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    bio = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    rating = Column(Numeric(2, 1), nullable=False, default=0)
    review_count = Column(Integer, nullable=False, default=0)
    approval_status = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    mentor = relationship("User", back_populates="mentor_profile")

    __table_args__ = (
            CheckConstraint("experience_years >= 0", name="check_experience_positive"),
            CheckConstraint("rating >= 0 AND rating <= 5", name="check_rating_range"),
            CheckConstraint("review_count >= 0", name="check_review_count_positive"),
    )