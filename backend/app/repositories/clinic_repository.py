from typing import Optional

from sqlmodel import Session, select

from app.models import Clinic


def get_by_id(session: Session, clinic_id: int) -> Optional[Clinic]:
    return session.get(Clinic, clinic_id)


def list_all(session: Session, offset: int = 0, limit: int = 100) -> list[Clinic]:
    statement = select(Clinic).offset(offset).limit(limit)
    return list(session.exec(statement).all())
