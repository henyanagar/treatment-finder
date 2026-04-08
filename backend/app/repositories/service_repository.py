from typing import Optional

from sqlmodel import Session, select

from app.models import Service


def get_by_id(session: Session, service_id: int) -> Optional[Service]:
    return session.get(Service, service_id)


def list_all(session: Session, offset: int = 0, limit: int = 100) -> list[Service]:
    statement = select(Service).offset(offset).limit(limit)
    return list(session.exec(statement).all())
