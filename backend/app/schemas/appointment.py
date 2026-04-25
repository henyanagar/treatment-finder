from datetime import UTC, datetime
from typing import Optional

from pydantic import field_serializer
from sqlmodel import Field, SQLModel


class AppointmentCreate(SQLModel):
    user_id: int = Field(..., gt=0)
    notes: Optional[str] = None
    appointment_datetime: datetime = Field(...)
    service_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)


class AppointmentUpdate(SQLModel):
    user_id: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=20)
    service_id: Optional[int] = Field(default=None, gt=0)
    clinic_id: Optional[int] = Field(default=None, gt=0)


class AppointmentRead(SQLModel):
    id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    user_full_name: str = Field(..., min_length=1, max_length=100)
    user_email: Optional[str] = Field(default=None, min_length=3, max_length=255)
    user_phone: str = Field(..., min_length=7, max_length=20, regex=r"^\+?\d{7,20}$")
    notes: Optional[str] = Field(default=None, max_length=2000)
    appointment_datetime: datetime
    created_at: datetime
    status: Optional[str] = Field(default=None, max_length=20)
    rating_id: Optional[int] = Field(default=None, gt=0)
    service_id: int = Field(..., gt=0)
    service_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    clinic_id: int = Field(..., gt=0)
    clinic_name: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @field_serializer("appointment_datetime", "created_at")
    def _serialize_utc(self, value: datetime) -> datetime:
        """Expose naive DB values as UTC-aware so JSON uses a fixed offset (WYSIWYG with ISO)."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class OccupancyRead(SQLModel):
    occupied_datetimes: list[str]
