from typing import Optional

from sqlmodel import SQLModel


class ServiceBase(SQLModel):
    name: str
    description: Optional[str] = None


class ServiceRead(ServiceBase):
    id: int
