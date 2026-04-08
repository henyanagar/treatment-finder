from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import Appointment, Clinic, Service
from app.repositories import appointment_repository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


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
    return appointment_repository.create(session, appointment)


def get_appointment(session: Session, appointment_id: int) -> Appointment:
    appointment = appointment_repository.get_by_id(session, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found",
        )
    return appointment


def list_appointments(session: Session, offset: int = 0, limit: int = 100) -> list[Appointment]:
    return appointment_repository.list_all(session, offset=offset, limit=limit)


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
    return appointment_repository.update(session, appointment)


def delete_appointment(session: Session, appointment_id: int) -> None:
    appointment = get_appointment(session, appointment_id)
    appointment_repository.delete(session, appointment)
