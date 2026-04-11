from typing import Optional

from sqlmodel import Field, SQLModel


class AIConsultRequest(SQLModel):
    query: str = Field(..., min_length=1, max_length=4000)


class AIConsultClinicRead(SQLModel):
    clinic_id: int = Field(..., gt=0)
    clinic_name: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=120)
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)


class AIConsultResponse(SQLModel):
    matched_service_id: Optional[int] = Field(default=None, gt=0)
    matched_service_name: Optional[str] = Field(
        default=None, min_length=1, max_length=200
    )
    matched_service_ids: list[int] = Field(default_factory=list)
    matched_service_names: list[str] = Field(default_factory=list)
    location: Optional[str] = Field(default=None, max_length=120)
    reason: str = Field(..., min_length=1, max_length=2000)
    explanation: str = Field(..., min_length=1, max_length=4000)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    clinics: list[AIConsultClinicRead]
