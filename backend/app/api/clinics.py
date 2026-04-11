from fastapi import APIRouter
from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.clinic import (
    ClinicCreate,
    ClinicRead,
    ClinicServiceLinkCreate,
    ClinicServiceLinkRead,
)
from app.services import clinic_service

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.post("", response_model=ClinicRead, status_code=201)
def create_clinic(
    payload: ClinicCreate,
    session: Session = Depends(get_session),
) -> ClinicRead:
    return clinic_service.create_clinic(session, payload)


@router.get("", response_model=list[ClinicRead])
def list_clinics(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ClinicRead]:
    return clinic_service.list_clinics(session, offset=offset, limit=limit)


@router.get("/{clinic_id}", response_model=ClinicRead)
def get_clinic(
    clinic_id: int,
    session: Session = Depends(get_session),
) -> ClinicRead:
    return clinic_service.get_clinic(session, clinic_id)


@router.post("/{clinic_id}/services/{service_id}", response_model=ClinicServiceLinkRead)
def link_service_to_clinic(
    clinic_id: int,
    service_id: int,
    payload: ClinicServiceLinkCreate | None = None,
    session: Session = Depends(get_session),
) -> ClinicServiceLinkRead:
    payload = payload or ClinicServiceLinkCreate(service_id=service_id)
    return clinic_service.link_service_to_clinic(session, clinic_id, service_id, payload)


@router.get("/{clinic_id}/services", response_model=list[ClinicServiceLinkRead])
def list_clinic_services(
    clinic_id: int,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ClinicServiceLinkRead]:
    return clinic_service.list_links_for_clinic(session, clinic_id, offset=offset, limit=limit)
