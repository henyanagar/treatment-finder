from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentUpdate, OccupancyRead
from app.schemas.rating import RatingCreate, RatingRead
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate = Body(...),
    session: Session = Depends(get_session),
) -> AppointmentRead:
    dt = payload.appointment_datetime
    if dt.minute not in (0,) or dt.second != 0 or dt.microsecond != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time must be on the hour (minutes/seconds must be 00)",
        )
    return appointment_service.create_appointment(session, payload)


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[int] = Query(None, gt=0),
    session: Session = Depends(get_session),
) -> list[AppointmentRead]:
    return appointment_service.list_appointments(
        session, offset=offset, limit=limit, user_id=user_id
    )


@router.get("/occupancy", response_model=OccupancyRead)
def read_occupancy(
    clinic_id: int = Query(..., gt=0),
    range_start: datetime = Query(
        ...,
        description="ISO-8601 range start (inclusive). UTC with Z recommended.",
    ),
    range_end: datetime = Query(
        ...,
        description="ISO-8601 range end (exclusive). UTC with Z recommended.",
    ),
    exclude_appointment_id: Optional[int] = Query(None, gt=0),
    session: Session = Depends(get_session),
) -> OccupancyRead:
    return appointment_service.get_occupancy(
        session,
        clinic_id,
        range_start,
        range_end,
        exclude_appointment_id,
    )


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
    return appointment_service.update_appointment(
        session, appointment_id, payload, actor_user_id=payload.user_id
    )


@router.post("/{appointment_id}/reviews", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def create_appointment_review(
    appointment_id: int,
    payload: RatingCreate,
    user_id: Optional[int] = Query(None, gt=0),
    session: Session = Depends(get_session),
) -> RatingRead:
    return appointment_service.create_rating_for_appointment(
        session, appointment_id, payload, actor_user_id=user_id
    )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    user_id: Optional[int] = Query(None, gt=0),
    session: Session = Depends(get_session),
) -> Response:
    appointment_service.delete_appointment_as_user(
        session, appointment_id, actor_user_id=user_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
