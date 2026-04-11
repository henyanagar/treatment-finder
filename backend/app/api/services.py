from fastapi import APIRouter
from fastapi import Depends
from sqlmodel import Session

from app.schemas.clinic import ClinicRead
from app.core.database import get_session
from app.schemas.service import ServiceCreate, ServiceRead
from app.services import service_service

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceRead, status_code=201)
def create_service(
    payload: ServiceCreate,
    session: Session = Depends(get_session),
) -> ServiceRead:
    return service_service.create_service(session, payload)


@router.get("", response_model=list[ServiceRead])
def list_services(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ServiceRead]:
    return service_service.list_services(session, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: int,
    session: Session = Depends(get_session),
) -> ServiceRead:
    return service_service.get_service(session, service_id)


@router.get("/{service_id}/clinics", response_model=list[ClinicRead])
def list_clinics_for_service(
    service_id: int,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ClinicRead]:
    return service_service.list_clinics_for_service(
        session, service_id, offset=offset, limit=limit
    )
