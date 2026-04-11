from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import Clinic, ClinicServiceLink
from app.repositories import clinic_repository, service_repository
from app.schemas.clinic import ClinicCreate, ClinicServiceLinkCreate


def create_clinic(session: Session, payload: ClinicCreate) -> Clinic:
    clinic = Clinic.model_validate(payload)
    return clinic_repository.create(session, clinic)


def list_clinics(session: Session, offset: int = 0, limit: int = 100) -> list[Clinic]:
    return clinic_repository.list_all(session, offset=offset, limit=limit)


def get_clinic(session: Session, clinic_id: int) -> Clinic:
    clinic = clinic_repository.get_by_id(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic {clinic_id} not found",
        )
    return clinic


def link_service_to_clinic(
    session: Session, clinic_id: int, service_id: int, payload: ClinicServiceLinkCreate
) -> ClinicServiceLink:
    get_clinic(session, clinic_id)
    service = service_repository.get_by_id(session, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_id} not found",
        )

    existing = clinic_repository.get_link(session, clinic_id, service_id)
    if existing:
        return existing

    link = ClinicServiceLink(
        clinic_id=clinic_id,
        service_id=service_id,
        price=payload.price,
        is_available=payload.is_available,
    )
    return clinic_repository.create_link(session, link)


def list_links_for_clinic(
    session: Session, clinic_id: int, offset: int = 0, limit: int = 100
) -> list[ClinicServiceLink]:
    get_clinic(session, clinic_id)
    return clinic_repository.list_links_for_clinic(session, clinic_id, offset=offset, limit=limit)
