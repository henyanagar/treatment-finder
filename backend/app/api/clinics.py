from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.db import get_session
from app.repositories import clinic_repository
from app.schemas.clinic import ClinicRead

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicRead])
def list_clinics(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[ClinicRead]:
    return clinic_repository.list_all(session, offset=offset, limit=limit)


@router.get("/{clinic_id}", response_model=ClinicRead)
def get_clinic(
    clinic_id: int,
    session: Session = Depends(get_session),
) -> ClinicRead:
    clinic = clinic_repository.get_by_id(session, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic {clinic_id} not found",
        )
    return clinic
