from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from schemas.users import UserCreateSchema, UserResponseSchema, UserRole, UserUpdateSchema, UserRoleUpdateSchame
from models.users import UserRole, User
from core.database import get_db
from core.security import hash_password
from api.auth import get_current_user

router = APIRouter(prefix="/users", tags=["tags"])


@router.get("/", response_model=list[UserResponseSchema])
def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/email/{email}", response_model=UserResponseSchema)
def get_by_email(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_db = db.query(User).filter(User.email == email).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


@router.get("/phone/{phone}", response_model=UserResponseSchema)
def get_by_phone(phone: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_db = db.query(User).filter(User.phone == phone).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


@router.get("/me", response_model=UserResponseSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponseSchema)
def get_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db


@router.post("/", response_model=UserResponseSchema)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(or_(
        User.email == user.email,
        User.phone == user.phone
    )).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or phone number already registered")
    
    user_db = User(
        **user.model_dump(exclude={"password"}),
        password_hash=hash_password(user.password),
        role=UserRole.USER
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db


@router.patch("/{user_id}", response_model=UserResponseSchema)
def update_user(user_id: int, user_update: UserUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user_db, field, value)

    db.commit()
    db.refresh(user_db)
    
    return user_db


@router.patch("/{user_id}/role", response_model=UserResponseSchema)
def change_role_user(user_id: int, user_role: UserRoleUpdateSchame, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_db = db.query(User).filter(User.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_db.role = user_role.role
    db.commit()
    db.refresh(user_db)

    return user_db


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
    user_db = db.query(User).filter(User.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user_db)
    db.commit()
