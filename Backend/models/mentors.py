from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, func, Date, Enum, CheckConstraint, DECIMAL
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