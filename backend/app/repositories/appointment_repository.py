from typing import Optional

from sqlmodel import Session, select

from app.models import Appointment


def create(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def get_by_id(session: Session, appointment_id: int) -> Optional[Appointment]:
    return session.get(Appointment, appointment_id)


def list_all(session: Session, offset: int = 0, limit: int = 100) -> list[Appointment]:
    statement = select(Appointment).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def update(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def delete(session: Session, appointment: Appointment) -> None:
    session.delete(appointment)
    session.commit()
