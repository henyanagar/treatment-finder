from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Clinic, Service
from app.repositories import service_repository
from app.schemas.service import ServiceCreate


def create_service(session: Session, payload: ServiceCreate) -> Service:
    existing = session.exec(select(Service).where(Service.name == payload.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service with name '{payload.name}' already exists",
        )
    service = Service.model_validate(payload)
    return service_repository.create(session, service)


def list_services(session: Session, offset: int = 0, limit: int = 100) -> list[Service]:
    return service_repository.list_all(session, offset=offset, limit=limit)


def get_service(session: Session, service_id: int) -> Service:
    service = service_repository.get_by_id(session, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_id} not found",
        )
    return service


def list_clinics_for_service(
    session: Session, service_id: int, offset: int = 0, limit: int = 100
) -> list[Clinic]:
    get_service(session, service_id)
    return service_repository.list_clinics_for_service(
        session, service_id, offset=offset, limit=limit
    )
