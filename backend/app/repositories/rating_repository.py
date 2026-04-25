from typing import Optional

from sqlalchemy import Float, cast, func
from sqlmodel import Session, select

from app.models import Rating


def create(session: Session, rating: Rating) -> Rating:
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating


def get_by_appointment_id(session: Session, appointment_id: int) -> Optional[Rating]:
    statement = select(Rating).where(Rating.appointment_id == appointment_id)
    return session.exec(statement).first()


def get_clinic_rating_stats(session: Session, clinic_id: int) -> tuple[Optional[float], int]:
    # Cast to Float explicitly so SQL always performs floating-point average.
    statement = select(func.avg(cast(Rating.rating, Float)), func.count(Rating.id)).where(
        Rating.clinic_id == clinic_id
    )
    average, count = session.exec(statement).one()
    return (float(average) if average is not None else None, int(count or 0))
