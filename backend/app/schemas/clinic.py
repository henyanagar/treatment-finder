from typing import Optional

from sqlmodel import Field, SQLModel


class ClinicBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=300)
    city: str = Field(..., min_length=1, max_length=120)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)


class ClinicRead(ClinicBase):
    id: int = Field(..., gt=0)


class ClinicCreate(ClinicBase):
    pass


class ClinicServiceLinkRead(SQLModel):
    id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    service_id: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0.0)
    is_available: bool


class ClinicServiceLinkCreate(SQLModel):
    service_id: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0.0)
    is_available: bool = True
