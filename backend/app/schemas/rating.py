from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RatingCreate(SQLModel):
    appointment_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=120)
    review: Optional[str] = Field(default=None, max_length=2000)


class RatingRead(SQLModel):
    id: int = Field(..., gt=0)
    appointment_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=120)
    review: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime
