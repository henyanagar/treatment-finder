from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.models import Appointment, Clinic, Rating, Service, User
from app.repositories import appointment_repository, rating_repository
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
    OccupancyRead,
)
from app.schemas.rating import RatingCreate

_DB_UNAVAILABLE = "A database error occurred. Please try again in a moment."


def _naive_utc(dt: datetime) -> datetime:
    """Persist naive UTC instants consistently for SQLite comparisons."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def _ensure_future_naive(dt_naive_utc: datetime) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    if dt_naive_utc <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date and time must be in the future",
        )


def _ensure_slot_available(
    session: Session,
    clinic_id: int,
    at_naive_utc: datetime,
    exclude_appointment_id: Optional[int],
) -> None:
    conflict = appointment_repository.find_same_slot(
        session,
        clinic_id,
        at_naive_utc,
        exclude_appointment_id=exclude_appointment_id,
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That time slot is already booked for this clinic",
        )


def _iso_z(dt: datetime) -> str:
    aware = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)
    return aware.isoformat().replace("+00:00", "Z")


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


def _get_user_or_400(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} does not exist",
        )
    return user


def _to_appointment_read(session: Session, appointment: Appointment, user: User) -> AppointmentRead:
    service_name = appointment.service.name if appointment.service else None
    if service_name is None:
        service = session.get(Service, appointment.service_id)
        service_name = service.name if service else None

    clinic_name = appointment.clinic.name if appointment.clinic else None
    if clinic_name is None:
        clinic = session.get(Clinic, appointment.clinic_id)
        clinic_name = clinic.name if clinic else None

    return AppointmentRead(
        id=appointment.id,
        user_id=appointment.user_id,
        user_full_name=user.full_name,
        user_email=user.email,
        user_phone=user.phone,
        notes=appointment.notes,
        appointment_datetime=appointment.appointment_datetime,
        created_at=appointment.created_at,
        status=appointment.status,
        rating_id=appointment.rating_id,
        service_id=appointment.service_id,
        service_name=service_name,
        clinic_id=appointment.clinic_id,
        clinic_name=clinic_name,
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


def create_appointment(session: Session, payload: AppointmentCreate) -> AppointmentRead:
    _validate_supporting_entities(session, payload.service_id, payload.clinic_id)
    user = _get_user_or_400(session, payload.user_id)
    data = payload.model_dump()
    at_naive = _naive_utc(data["appointment_datetime"])
    _ensure_future_naive(at_naive)
    _ensure_slot_available(session, data["clinic_id"], at_naive, exclude_appointment_id=None)
    data["appointment_datetime"] = at_naive
    appointment = Appointment.model_validate(data)
    try:
        created = appointment_repository.create(session, appointment)
        return _to_appointment_read(session, created, user)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def get_appointment_entity(session: Session, appointment_id: int) -> Appointment:
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


def get_appointment(session: Session, appointment_id: int) -> AppointmentRead:
    appointment = get_appointment_entity(session, appointment_id)
    user = appointment.user or _get_user_or_400(session, appointment.user_id)
    return _to_appointment_read(session, appointment, user)


def _assert_appointment_user(appointment: Appointment, user_id: Optional[int]) -> None:
    if user_id is None:
        return
    if appointment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this appointment",
        )


def get_occupancy(
    session: Session,
    clinic_id: int,
    range_start: datetime,
    range_end: datetime,
    exclude_appointment_id: Optional[int],
) -> OccupancyRead:
    _validate_clinic_exists(session, clinic_id)
    rs = _naive_utc(range_start)
    re = _naive_utc(range_end)
    if rs >= re:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="range_start must be before range_end",
        )
    try:
        rows = appointment_repository.list_for_clinic_between(
            session,
            clinic_id,
            rs,
            re,
            exclude_appointment_id=exclude_appointment_id,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None

    return OccupancyRead(
        occupied_datetimes=[_iso_z(r.appointment_datetime) for r in rows],
    )


def list_appointments(
    session: Session,
    offset: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
) -> list[AppointmentRead]:
    try:
        appointments = appointment_repository.list_all(
            session, offset=offset, limit=limit, user_id=user_id
        )
        if not appointments:
            return []
        return [
            _to_appointment_read(
                session,
                appointment,
                appointment.user or _get_user_or_400(session, appointment.user_id),
            )
            for appointment in appointments
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def update_appointment(
    session: Session,
    appointment_id: int,
    payload: AppointmentUpdate,
    actor_user_id: Optional[int] = None,
) -> AppointmentRead:
    appointment = get_appointment_entity(session, appointment_id)
    _assert_appointment_user(appointment, actor_user_id)
    updates = payload.model_dump(exclude_unset=True)
    if "user_id" in updates and updates["user_id"] != appointment.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment user cannot be changed",
        )

    _validate_supporting_entities(
        session,
        service_id=updates.get("service_id"),
        clinic_id=updates.get("clinic_id"),
    )

    if "appointment_datetime" in updates:
        at_naive = _naive_utc(updates["appointment_datetime"])
        clinic_for_slot = updates.get("clinic_id", appointment.clinic_id)
        _ensure_future_naive(at_naive)
        _ensure_slot_available(
            session,
            clinic_for_slot,
            at_naive,
            exclude_appointment_id=appointment_id,
        )
        updates["appointment_datetime"] = at_naive

    appointment.sqlmodel_update(updates)
    try:
        updated = appointment_repository.update(session, appointment)
        user = updated.user or _get_user_or_400(session, updated.user_id)
        return _to_appointment_read(session, updated, user)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def delete_appointment(session: Session, appointment_id: int) -> None:
    appointment = get_appointment_entity(session, appointment_id)
    try:
        appointment_repository.delete(session, appointment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def delete_appointment_as_user(
    session: Session, appointment_id: int, actor_user_id: Optional[int]
) -> None:
    appointment = get_appointment_entity(session, appointment_id)
    _assert_appointment_user(appointment, actor_user_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    appointment_at = _naive_utc(appointment.appointment_datetime)
    if appointment_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only upcoming appointments can be cancelled",
        )
    if str(appointment.status or "").upper() == "CANCELLED":
        return
    appointment.status = "CANCELLED"
    try:
        appointment_repository.update(session, appointment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None


def create_rating_for_appointment(
    session: Session,
    appointment_id: int,
    payload: RatingCreate,
    actor_user_id: Optional[int] = None,
) -> Rating:
    appointment = get_appointment_entity(session, appointment_id)
    _assert_appointment_user(appointment, actor_user_id)

    if payload.appointment_id != appointment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="appointment_id in payload does not match route parameter",
        )
    if payload.clinic_id != appointment.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="clinic_id does not match the appointment clinic",
        )

    # Completed-only: user can rate only past appointments.
    now = datetime.now(UTC).replace(tzinfo=None)
    appointment_at = _naive_utc(appointment.appointment_datetime)
    if appointment_at > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed appointments can be reviewed",
        )

    if appointment.rating_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment already rated",
        )

    try:
        existing = rating_repository.get_by_appointment_id(session, appointment_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment already rated",
        )

    rating = Rating.model_validate(payload)
    try:
        created = rating_repository.create(session, rating)
        appointment.rating_id = created.id
        clinic = session.get(Clinic, appointment.clinic_id)
        if clinic is not None:
            average, count = rating_repository.get_clinic_rating_stats(
                session, appointment.clinic_id
            )
            previous_count = int(clinic.reviews_count or 0)
            previous_average = float(clinic.rating or 0.0)

            if previous_count > 0:
                # Preserve already-persisted aggregate as historical baseline.
                # This avoids jumps for seeded clinics (e.g. 4.7 with existing reviews)
                # even when rating rows were not historically backfilled.
                total_count = previous_count + 1
                total_average = round(
                    ((previous_average * float(previous_count)) + float(created.rating))
                    / float(total_count),
                    1,
                )
            else:
                total_count = int(count)
                total_average = round(float(average), 1) if average is not None else None

            clinic.rating = total_average
            clinic.reviews_count = total_count
            session.add(clinic)
        appointment_repository.update(session, appointment)
        return created
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_UNAVAILABLE,
        ) from None
