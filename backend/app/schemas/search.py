from typing import Optional

from sqlmodel import Field, SQLModel


class SearchClinicResult(SQLModel):
    clinic_id: int = Field(..., gt=0)
    clinic_name: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=120)
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    matched_service_name: str = Field(..., min_length=1, max_length=200)
