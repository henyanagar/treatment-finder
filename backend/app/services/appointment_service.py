from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.models import Appointment, Clinic, Service
from app.repositories import appointment_repository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

_DB_UNAVAILABLE = (
    "A database error occurred. Please try again in a moment.",
)


def _validate_service_exists(session: Session, service_id: int) -> None:
    if not session.get(Service, service_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service {service_id} does not exist",
        )


def _validate_clinic_exists(session: Session, clinic_id: int) -> None:
    if not session.get(Clinic, clinic_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clinic {clinic_id} does not exist",
        )


def _validate_supporting_entities(
    session: Session,
    service_id: Optional[int] = None,
    clinic_id: Optional[int] = None,
) -> None:
    if service_id is not None:
        _validate_service_exists(session, service_id)
    if clinic_id is not None:
        _validate_clinic_exists(session, clinic_id)


def create_appointment(session: Session, payload: AppointmentCreate) -> Appointment:
    _validate_supporting_entities(session, payload.service_id, payload.clinic_id)
    appointment = Appointment.model_validate(payload)
    try:
        return appointment_repository.create(session, appointment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def get_appointment(session: Session, appointment_id: int) -> Appointment:
    try:
        appointment = appointment_repository.get_by_id(session, appointment_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found",
        )
    return appointment


def list_appointments(session: Session, offset: int = 0, limit: int = 100) -> list[Appointment]:
    try:
        return appointment_repository.list_all(session, offset=offset, limit=limit)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def update_appointment(
    session: Session, appointment_id: int, payload: AppointmentUpdate
) -> Appointment:
    appointment = get_appointment(session, appointment_id)
    updates = payload.model_dump(exclude_unset=True)

    _validate_supporting_entities(
        session,
        service_id=updates.get("service_id"),
        clinic_id=updates.get("clinic_id"),
    )

    appointment.sqlmodel_update(updates)
    try:
        return appointment_repository.update(session, appointment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def delete_appointment(session: Session, appointment_id: int) -> None:
    appointment = get_appointment(session, appointment_id)
    try:
        appointment_repository.delete(session, appointment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None
