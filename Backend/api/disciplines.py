from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.disciplines import DisciplineCreateSchema, DisciplineResponseSchema, DisciplineUpdateSchema
from models.users import User, UserRole
from models.disciplines import Discipline
from core.database import get_db
from api.auth import get_current_user

router = APIRouter(prefix="/discpline", tags=["tags"])


@router.get("/", response_model=list[DisciplineResponseSchema])
def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):    
    return (db.query(Discipline).offset(skip).limit(limit).all())


@router.get("/name/{name}", response_model=DisciplineResponseSchema)
def get_by_name(name: str, db: Session = Depends(get_db)):
    discipline_db = db.query(Discipline).filter(Discipline.name == name).first()
    if not discipline_db:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discipline_db


@router.get("/id/{id}", response_model=DisciplineResponseSchema)
def get_by_id(discpline_id: int, db: Session = Depends(get_db)):
    discpline_db = db.query(Discipline).filter(Discipline.id == discpline_id).first()
    if not Discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discpline_db


@router.post("/",response_model=DisciplineResponseSchema)
def create_discipline(discipline: DisciplineCreateSchema,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403,detail="Not enough permissions")

    name = discipline.name.strip()
    if not name:
        raise HTTPException(status_code=422,detail="Discipline name cannot be empty")

    existing = (db.query(Discipline).filter(Discipline.name == name).first())
    if existing:
        raise HTTPException(status_code=400, detail="Discipline already exists")

    discipline_db = Discipline(name=name)

    db.add(discipline_db)
    db.commit()
    db.refresh(discipline_db)

    return discipline_db


@router.patch("/{discipline_id}", response_model=DisciplineResponseSchema)
def update_discipline(discipline_id: int, discipline_update: DisciplineUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    discipline_db = (db.query(Discipline).filter(Discipline.id == discipline_id).first())
    if not discipline_db:
        raise HTTPException(status_code=404, detail="Discipline not found")

    name = discipline_update.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Discipline name cannot be empty")

    existing = (db.query(Discipline).filter(Discipline.name == name, Discipline.id != discipline_id).first())
    if existing:
        raise HTTPException(status_code=400, detail="Discipline already exists")

    discipline_db.name = name

    db.commit()
    db.refresh(discipline_db)

    return discipline_db


@router.delete("/{discipline_id}", status_code=204)
def delete_discipline(discipline_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this discipline")
    
    discipline_db = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline_db:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    db.delete(discipline_db)
    db.commit()