from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.search import SearchClinicResult
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchClinicResult])
def search(
    query: str,
    session: Session = Depends(get_session),
) -> list[SearchClinicResult]:
    return search_service.search(session, query)
