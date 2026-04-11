from typing import Optional

from sqlmodel import Session, select

from app.models import Clinic, ClinicServiceLink, Service


def create(session: Session, service: Service) -> Service:
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


def get_by_id(session: Session, service_id: int) -> Optional[Service]:
    return session.get(Service, service_id)


def list_all(session: Session, offset: int = 0, limit: int = 100) -> list[Service]:
    statement = select(Service).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def list_clinics_for_service(
    session: Session, service_id: int, offset: int = 0, limit: int = 100
) -> list[Clinic]:
    statement = (
        select(Clinic)
        .join(ClinicServiceLink, ClinicServiceLink.clinic_id == Clinic.id)
        .where(ClinicServiceLink.service_id == service_id)
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def list_available_clinics_for_service(
    session: Session, service_id: int, offset: int = 0, limit: int = 100
) -> list[Clinic]:
    statement = (
        select(Clinic)
        .join(ClinicServiceLink, ClinicServiceLink.clinic_id == Clinic.id)
        .where(ClinicServiceLink.service_id == service_id)
        .where(ClinicServiceLink.is_available.is_(True))
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())
