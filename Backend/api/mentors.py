from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.mentors import *
from models.users import User, UserRole
from models.disciplines import Discipline
from models.mentors import *
from core.database import get_db
from api.auth import get_current_user

router = APIRouter(prefix="/mentor", tags=["tags"])


@router.get("/mentor-disciplines/mentor/{mentor_id}", response_model=list[MentorDisciplineResponseSchema])
def get_all_mentor_discipline_by_mentor_id(mentor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != mentor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    mentor_disciplines = (
        db.query(
            MentorDiscipline.id,
            MentorDiscipline.mentor_id,
            MentorDiscipline.discipline_id,
            Discipline.name.label("discipline_name"),
            MentorDiscipline.price,
            MentorDiscipline.duration_in_minutes
        )
        .join(
            Discipline,
            MentorDiscipline.discipline_id == Discipline.id
        )
        .filter(MentorDiscipline.mentor_id == mentor_id)
        .all()
    )

    return mentor_disciplines


@router.post("/", response_model=MentorDisciplineResponseSchema, status_code=201)
def create_mentor_discipline(data: MentorDisciplineCreateSchema,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.id != data.mentor_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    mentor = db.query(User).filter(User.id == data.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    if mentor.role != UserRole.MENTOR:
        raise HTTPException(status_code=400, detail="User is not a mentor")

    discipline = db.query(Discipline).filter(Discipline.id == data.discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")

    existing = db.query(MentorDiscipline).filter(
        MentorDiscipline.mentor_id == data.mentor_id,
        MentorDiscipline.discipline_id == data.discipline_id
    ).first()
    if existing:
        raise HTTPException(status_code=409,detail="Mentor already teaches this discipline")

    mentor_discipline = MentorDiscipline(
        mentor_id=data.mentor_id,
        discipline_id=data.discipline_id,
        price=data.price,
        duration_in_minutes=data.duration_in_minutes
    )

    db.add(mentor_discipline)
    db.commit()
    db.refresh(mentor_discipline)

    return {
        "id": mentor_discipline.id,
        "mentor_id": mentor_discipline.mentor_id,
        "discipline_id": mentor_discipline.discipline_id,
        "discipline_name": discipline.name,
        "price": mentor_discipline.price,
        "duration_in_minutes": mentor_discipline.duration_in_minutes
    }


@router.patch("/{mentor_discipline_id}",response_model=MentorDisciplineResponseSchema)
def update_mentor_discipline(mentor_discipline_id: int, data: MentorDisciplineUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mentor_discipline = db.query(MentorDiscipline).filter(MentorDiscipline.id == mentor_discipline_id).first()
    if not mentor_discipline:
        raise HTTPException(status_code=404, detail="Mentor discipline not found")

    if (current_user.id != mentor_discipline.mentor_id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    for key, value in update_data.items():
        setattr(mentor_discipline, key, value)

    db.commit()
    db.refresh(mentor_discipline)

    return {
        "id": mentor_discipline.id,
        "mentor_id": mentor_discipline.mentor_id,
        "discipline_id": mentor_discipline.discipline_id,
        "discipline_name": mentor_discipline.discipline.name,
        "price": mentor_discipline.price,
        "duration_in_minutes": mentor_discipline.duration_in_minutes
    }


@router.delete("/{mentor_discipline_id}")
def delete_mentor_discipline(mentor_discipline_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mentor_discipline = db.query(MentorDiscipline).filter(MentorDiscipline.id == mentor_discipline_id).first()
    if not mentor_discipline:
        raise HTTPException(status_code=404,detail="Mentor discipline not found")

    if (current_user.id != mentor_discipline.mentor_id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403,detail="Not enough permissions")

    db.delete(mentor_discipline)
    db.commit()

    return {"detail": "Mentor discipline deleted successfully"}