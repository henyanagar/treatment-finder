from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.db import get_session
from app.repositories import service_repository
from app.schemas.service import ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def list_services(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ServiceRead]:
    return service_repository.list_all(session, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: int,
    session: Session = Depends(get_session),
) -> ServiceRead:
    service = service_repository.get_by_id(session, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_id} not found",
        )
    return service
