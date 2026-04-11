from typing import Optional

from sqlmodel import Session, select

from app.models import Clinic, ClinicServiceLink


def create(session: Session, clinic: Clinic) -> Clinic:
    session.add(clinic)
    session.commit()
    session.refresh(clinic)
    return clinic


def get_by_id(session: Session, clinic_id: int) -> Optional[Clinic]:
    return session.get(Clinic, clinic_id)


def list_all(session: Session, offset: int = 0, limit: int = 100) -> list[Clinic]:
    statement = select(Clinic).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def get_link(session: Session, clinic_id: int, service_id: int) -> Optional[ClinicServiceLink]:
    statement = select(ClinicServiceLink).where(
        ClinicServiceLink.clinic_id == clinic_id,
        ClinicServiceLink.service_id == service_id,
    )
    return session.exec(statement).first()


def create_link(session: Session, link: ClinicServiceLink) -> ClinicServiceLink:
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def list_links_for_clinic(
    session: Session, clinic_id: int, offset: int = 0, limit: int = 100
) -> list[ClinicServiceLink]:
    statement = (
        select(ClinicServiceLink)
        .where(ClinicServiceLink.clinic_id == clinic_id)
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())
