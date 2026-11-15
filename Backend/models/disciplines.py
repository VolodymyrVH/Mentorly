from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    mentor_discipline = relationship("MentorDiscipline", back_populates="discipline", cascade="all, delete-orphan")