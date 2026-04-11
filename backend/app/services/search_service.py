from sqlmodel import Session

from app.repositories import search_repository
from app.schemas.search import SearchClinicResult

def search(session: Session, query: str) -> list[SearchClinicResult]:
    if not query.strip():
        return []

    rows = search_repository.search_clinics_by_service_name(session, query)
    return [
        SearchClinicResult(
            clinic_id=clinic_id,
            clinic_name=clinic_name,
            city=city,
            rating=rating,
            matched_service_name=matched_service_name,
        )
        for clinic_id, clinic_name, city, rating, matched_service_name in rows
    ]
