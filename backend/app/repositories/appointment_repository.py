from datetime import datetime
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.models import Appointment


def create(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def get_by_id(session: Session, appointment_id: int) -> Optional[Appointment]:
    statement = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            selectinload(Appointment.user),
            selectinload(Appointment.service),
            selectinload(Appointment.clinic),
        )
    )
    return session.exec(statement).first()


def list_all(
    session: Session,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
) -> list[Appointment]:
    statement = select(Appointment).options(
        selectinload(Appointment.user),
        selectinload(Appointment.service),
        selectinload(Appointment.clinic),
    )
    if user_id is not None:
        statement = statement.where(Appointment.user_id == user_id)
    statement = statement.offset(offset).limit(limit)
    return list(session.exec(statement).all())


def list_for_clinic_between(
    session: Session,
    clinic_id: int,
    range_start: datetime,
    range_end: datetime,
    exclude_appointment_id: Optional[int] = None,
) -> list[Appointment]:
    statement = (
        select(Appointment)
        .where(Appointment.clinic_id == clinic_id)
        .where(col(Appointment.appointment_datetime) >= range_start)
        .where(col(Appointment.appointment_datetime) < range_end)
    )
    if exclude_appointment_id is not None:
        statement = statement.where(Appointment.id != exclude_appointment_id)
    return list(session.exec(statement).all())


def find_same_slot(
    session: Session,
    clinic_id: int,
    at: datetime,
    exclude_appointment_id: Optional[int] = None,
) -> Optional[Appointment]:
    statement = select(Appointment).where(
        Appointment.clinic_id == clinic_id,
        Appointment.appointment_datetime == at,
    )
    if exclude_appointment_id is not None:
        statement = statement.where(Appointment.id != exclude_appointment_id)
    return session.exec(statement).first()


def update(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def delete(session: Session, appointment: Appointment) -> None:
    session.delete(appointment)
    session.commit()
