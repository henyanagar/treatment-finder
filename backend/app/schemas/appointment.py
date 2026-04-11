from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AppointmentCreate(SQLModel):
    user_full_name: str = Field(..., min_length=1, max_length=100)
    user_phone: str = Field(..., min_length=1, regex=r"^\+?1?\d{9,15}$")
    notes: Optional[str] = None
    appointment_datetime: datetime = Field(...)
    service_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)


class AppointmentUpdate(SQLModel):
    user_full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    user_phone: Optional[str] = Field(
        default=None, min_length=1, regex=r"^\+?1?\d{9,15}$"
    )
    notes: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    service_id: Optional[int] = Field(default=None, gt=0)
    clinic_id: Optional[int] = Field(default=None, gt=0)


class AppointmentRead(SQLModel):
    id: int = Field(..., gt=0)
    user_full_name: str = Field(..., min_length=1, max_length=100)
    user_phone: str = Field(..., min_length=1, regex=r"^\+?1?\d{9,15}$")
    notes: Optional[str] = Field(default=None, max_length=2000)
    appointment_datetime: datetime
    created_at: datetime
    service_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
