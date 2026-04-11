from typing import Optional

from sqlmodel import Field, SQLModel


class ServiceBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int = Field(..., gt=0)
