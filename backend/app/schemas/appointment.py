from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class AppointmentCreate(SQLModel):
    user_full_name: str
    user_phone: str
    notes: Optional[str] = None
    appointment_datetime: datetime
    service_id: int
    clinic_id: int


class AppointmentUpdate(SQLModel):
    user_full_name: Optional[str] = None
    user_phone: Optional[str] = None
    notes: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    service_id: Optional[int] = None
    clinic_id: Optional[int] = None


class AppointmentRead(SQLModel):
    id: int
    user_full_name: str
    user_phone: str
    notes: Optional[str]
    appointment_datetime: datetime
    created_at: datetime
    service_id: int
    clinic_id: int
