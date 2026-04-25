from sqlalchemy import or_
from sqlmodel import Session, distinct, select

from app.models import Clinic, ClinicServiceLink, Service


def search_clinics_by_service_name(session: Session, query: str) -> list[tuple]:
    pattern = f"%{query.strip()}%"
    statement = (
        select(
            distinct(Clinic.id),
            Clinic.name,
            Clinic.city,
            Clinic.rating,
            Service.name,
        )
        .join(ClinicServiceLink, ClinicServiceLink.clinic_id == Clinic.id)
        .join(Service, Service.id == ClinicServiceLink.service_id)
        .where(ClinicServiceLink.is_available.is_(True))
        .where(
            or_(
                Clinic.name.ilike(pattern),
                Clinic.address.ilike(pattern),
                Service.name.ilike(pattern),
                Service.description.ilike(pattern),
            )
        )
        .order_by(Clinic.name)
    )
    return list(session.exec(statement).all())
