from typing import Optional

from sqlmodel import SQLModel


class ClinicBase(SQLModel):
    name: str
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None


class ClinicRead(ClinicBase):
    id: int
