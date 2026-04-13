from fastapi import APIRouter, Body, Depends, Response, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate = Body(...),
    session: Session = Depends(get_session),
) -> AppointmentRead:
    return appointment_service.create_appointment(session, payload)


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[AppointmentRead]:
    return appointment_service.list_appointments(session, offset=offset, limit=limit)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
) -> AppointmentRead:
    return appointment_service.get_appointment(session, appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    session: Session = Depends(get_session),
) -> AppointmentRead:
    return appointment_service.update_appointment(session, appointment_id, payload)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
) -> Response:
    appointment_service.delete_appointment(session, appointment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
