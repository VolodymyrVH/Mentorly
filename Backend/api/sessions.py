from datetime import datetime, date, time, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from core.database import get_db
from models.users import User, UserRole
from models.sessions import Session as SessionModel, StatusSession
from models.disciplines import Discipline
from models.mentors import MentorDiscipline, MentorProfiles
from schemas.sessions import SessionCreateSchema, SessionResponseSchema, SessionUpdateSchema, SessionStatusUpdateSchema, SessionRescheduleSchema
from api.auth import get_current_user


router = APIRouter(prefix="/sessions", tags=["Sessions"])


ACTIVE_STATUSES = [
    StatusSession.PENDING,
    StatusSession.CONFIRMED,
    StatusSession.STARTED,
]

TERMINAL_STATUSES = [
    StatusSession.REJECTED,
    StatusSession.CANCELED_BY_STUDENT,
    StatusSession.CANCELED_BY_MENTOR,
    StatusSession.COMPLETED,
    StatusSession.NO_SHOW,
]


def get_session_or_404(session_id: int, db: Session):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


def check_session_access(session: SessionModel, current_user: User):
    if (session.student_id != current_user.id and session.mentor_id != current_user.id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="You do not have access to this session")


def check_session_conflict(db: Session, mentor_id: int, student_id: int, datetime_start: datetime, datetime_end: datetime, exclude_session_id: int | None = None):
    query = db.query(SessionModel).filter( SessionModel.status.in_(ACTIVE_STATUSES),
        SessionModel.datetime_start < datetime_end, SessionModel.datetime_end > datetime_start,
        or_(SessionModel.mentor_id == mentor_id, SessionModel.student_id == student_id))

    if exclude_session_id is not None:
        query = query.filter(SessionModel.id != exclude_session_id)

    conflict = query.first()
    if conflict:
        raise HTTPException(status_code=409, detail="The selected time overlaps another session")


def check_mentor_approved(mentor_id: int, db: Session):
    profile = db.query(MentorProfiles).filter(MentorProfiles.mentor_id == mentor_id).first()
    if not profile or not profile.approval_status:
        raise HTTPException(status_code=403, detail="Mentor is not approved")

    return profile


def check_mentor_discipline(mentor_id: int, discipline_id: int, db: Session):
    mentor_discipline = db.query(MentorDiscipline).filter(MentorDiscipline.mentor_id == mentor_id, MentorDiscipline.discipline_id == discipline_id).first()
    if not mentor_discipline:
        raise HTTPException(status_code=400, detail="Mentor does not teach this discipline")

    return mentor_discipline


def check_duration(datetime_start: datetime, datetime_end: datetime, required_minutes: int):
    actual_minutes = (datetime_end - datetime_start).total_seconds() / 60
    if actual_minutes != required_minutes:
        raise HTTPException(status_code=400, detail=f"Session duration must be {required_minutes} minutes")


#requests
@router.post("/", response_model=SessionResponseSchema, status_code=status.HTTP_201_CREATED)
def create_session(data: SessionCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id == data.mentor_id:
        raise HTTPException(status_code=400, detail="You cannot book yourself")
    
    mentor = db.query(User).filter(User.id == data.mentor_id).first()
    if not mentor or mentor.role != UserRole.MENTOR:
        raise HTTPException(status_code=404, detail="Mentor not found")

    check_mentor_approved(mentor.id, db)

    discipline = db.query(Discipline).filter(Discipline.id == data.discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")

    mentor_discipline = check_mentor_discipline(mentor.id, discipline.id, db)
    check_duration(data.datetime_start, data.datetime_end, mentor_discipline.duration_in_minutes)
    check_session_conflict(db, mentor.id, current_user.id, data.datetime_start, data.datetime_end)

    new_session = SessionModel(
        mentor_id=mentor.id,
        student_id=current_user.id,
        discipline_id=discipline.id,
        title=data.title,
        description=data.description,
        repeat=data.repeat,
        status=StatusSession.PENDING,
        price_per_hour=mentor_discipline.price,
        datetime_start=data.datetime_start,
        datetime_end=data.datetime_end,
    )

    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
    except Exception:
        db.rollback()
        raise

    return new_session



@router.get("/me", response_model=list[SessionResponseSchema])
def get_my_sessions(status_filter: StatusSession | None = Query( default=None, alias="status"), upcoming: bool = False, role_filter: str | None = Query(default=None, pattern="^(student|mentor)$"),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(SessionModel).filter(or_( SessionModel.student_id == current_user.id, SessionModel.mentor_id == current_user.id))

    if status_filter:
        query = query.filter(SessionModel.status == status_filter)

    if role_filter == "student":
        query = query.filter(SessionModel.student_id == current_user.id)

    elif role_filter == "mentor":
        query = query.filter(SessionModel.mentor_id == current_user.id)

    if upcoming:
        query = query.filter(SessionModel.datetime_start >= datetime.now())

    return query.order_by(SessionModel.datetime_start.asc()).all()


@router.get("/{session_id}", response_model=SessionResponseSchema)
def get_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session_or_404(session_id, db)
    check_session_access(session, current_user)
    return session


@router.patch("/{session_id}", response_model=SessionResponseSchema)
def update_session(session_id: int, data: SessionUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session_or_404(session_id, db)
    check_session_access(session, current_user)

    if session.status not in [ StatusSession.PENDING, StatusSession.CONFIRMED]:
        raise HTTPException(tatus_code=400, detail="This session cannot be edited")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(session, field, value)

    try:
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise

    return session


@router.patch("/{session_id}/status", response_model=SessionResponseSchema)
def update_session_status(session_id: int, data: SessionStatusUpdateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session_or_404(session_id, db)
    check_session_access(session, current_user)

    old_status = session.status
    new_status = data.status

    if old_status == new_status:
        return session

    if current_user.id == session.mentor_id:
        if old_status != StatusSession.PENDING:
            raise HTTPException(status_code=400, detail="Only pending sessions can be confirmed or rejected")

        if new_status not in [StatusSession.CONFIRMED, StatusSession.REJECTED]:
            raise HTTPException(status_code=403, detail="Invalid status transition for mentor")

    elif current_user.id == session.student_id:
        if new_status != StatusSession.CANCELED_BY_STUDENT:
            raise HTTPException(status_code=403, detail="Student can only cancel the session")

        if old_status not in [StatusSession.PENDING, StatusSession.CONFIRMED]:
            raise HTTPException(status_code=400, detail="This session cannot be canceled")

    elif current_user.role == UserRole.ADMIN:
        allowed_admin_statuses = set(StatusSession)

        if new_status not in allowed_admin_statuses:
            raise HTTPException(status_code=400, detail="Invalid session status")

    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    session.status = new_status

    try:
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise

    return session


@router.patch("/{session_id}/reschedule", response_model=SessionResponseSchema)
def reschedule_session(session_id: int, data: SessionRescheduleSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session_or_404(session_id, db)
    check_session_access(session, current_user)

    if session.status not in [StatusSession.PENDING, StatusSession.CONFIRMED]:
        raise HTTPException(status_code=400, detail="This session cannot be rescheduled")

    check_session_conflict(
        db,
        session.mentor_id,
        session.student_id,
        data.datetime_start,
        data.datetime_end,
        exclude_session_id=session.id
    )

    mentor_discipline = check_mentor_discipline(
        session.mentor_id,
        session.discipline_id,
        db
    )

    check_duration(
        data.datetime_start,
        data.datetime_end,
        mentor_discipline.duration_in_minutes
    )

    session.datetime_start = data.datetime_start
    session.datetime_end = data.datetime_end
    session.status = StatusSession.PENDING

    try:
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise

    return session


@router.get("/availability")
def get_availability(mentor_id: int, discipline_id: int, requested_date: date = Query(alias="date"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mentor = db.query(User).filter(User.id == mentor_id, User.role == UserRole.MENTOR).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    check_mentor_approved(mentor.id, db)
    mentor_discipline = check_mentor_discipline(mentor.id, discipline_id, db)

    day_start = datetime.combine( requested_date, time.min, tzinfo=None)
    day_end = day_start + timedelta(days=1)

    booked_sessions = db.query(SessionModel).filter(
        SessionModel.mentor_id == mentor_id,
        SessionModel.status.in_(ACTIVE_STATUSES),
        SessionModel.datetime_start < day_end,
        SessionModel.datetime_end > day_start
    ).all()

    busy_intervals = [
        {
            "start": s.datetime_start,
            "end": s.datetime_end
        }
        for s in booked_sessions
    ]

    slot_minutes = 30
    duration_minutes = mentor_discipline.duration_in_minutes

    available_slots = []

    current_slot = day_start

    while current_slot + timedelta(minutes=duration_minutes) <= day_end:
        slot_end = current_slot + timedelta(minutes=duration_minutes)

        is_busy = any(
            interval["start"] < slot_end
            and interval["end"] > current_slot
            for interval in busy_intervals
        )

        if not is_busy:
            available_slots.append({
                "datetime_start": current_slot.isoformat(),
                "datetime_end": slot_end.isoformat()
            })

        current_slot += timedelta(minutes=slot_minutes)

    return {
        "mentor_id": mentor_id,
        "discipline_id": discipline_id,
        "date": requested_date,
        "duration_in_minutes": duration_minutes,
        "available_slots": available_slots
    }


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session_or_404(session_id, db)
    check_session_access(session, current_user)

    if session.status != StatusSession.PENDING:
        raise HTTPException(status_code=400, detail="Only pending sessions can be deleted")

    try:
        db.delete(session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "detail": "Session deleted successfully"
    }